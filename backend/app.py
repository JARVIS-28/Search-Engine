#imports
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
import re
import urllib.parse
import concurrent.futures
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import hashlib
import json

# Load environment variables
load_dotenv()

# Get API keys from environment
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

app = Flask(__name__)
CORS(app)

# Load sentence transformer model for better semantic search
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def get_embedding(text: str) -> np.ndarray:
    """Generate embeddings for a given text using SentenceTransformer."""
    return model.encode(text, convert_to_tensor=True)

def compute_similarity(query_embedding: torch.Tensor, text: str) -> float:
    """Calculate semantic similarity between query and text."""
    if not text.strip():
        return 0.0
    text_embedding = model.encode(text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(query_embedding, text_embedding)[0][0].item()
    return similarity

def get_content_hash(content: str) -> str:
    """Generate a hash of the content to detect duplicates."""
    return hashlib.md5(content.lower().encode()).hexdigest()

def remove_duplicates(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate results based on content similarity and URL patterns."""
    seen_hashes = set()
    seen_domains = set()
    unique_results = []
    
    for result in results:
        content = f"{result['title']} {result.get('snippet', '')}"
        content_hash = get_content_hash(content)
        
        # Extract domain from URL
        domain = urllib.parse.urlparse(result['url']).netloc
        
        # Check if content is unique and domain hasn't been seen too many times
        if content_hash not in seen_hashes and domain_count(seen_domains, domain) < 2:
            seen_hashes.add(content_hash)
            seen_domains.add(domain)
            unique_results.append(result)
            
    return unique_results

def domain_count(seen_domains: set, domain: str) -> int:
    """Count how many times a domain has been seen."""
    return sum(1 for d in seen_domains if d == domain)

def filter_relevant_results(results: List[Dict[str, Any]], query_embedding: torch.Tensor, threshold: float = 0.3) -> List[Dict[str, Any]]:
    """Filter results based on relevance score."""
    filtered_results = []
    
    for result in results:
        content = f"{result['title']} {result.get('snippet', '')}"
        similarity = compute_similarity(query_embedding, content)
        
        if similarity >= threshold:
            result['relevance'] = similarity
            filtered_results.append(result)
            
    return filtered_results

def fetch_content(url):
    """Fetch the full content from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script, style, and nav elements
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
            
        # Extract main content based on common content containers
        content = ""
        main_elements = soup.select("main, article, #content, .content, .main, #main, .post, #post")
        
        if main_elements:
            for element in main_elements:
                content += element.get_text(separator=" ", strip=True) + " "
        else:
            # Fallback to body text if no main content containers found
            content = soup.body.get_text(separator=" ", strip=True)
            
        # Clean up the content
        content = re.sub(r'\s+', ' ', content).strip()
        return content[:10000]  # Limit content length to avoid errors
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

# Wikipedia Search
def search_wikipedia(query, query_embedding, max_results=3):
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
    try:
        response = requests.get(url).json()
        results = []
        
        for item in response["query"]["search"]:
            title = item["title"]
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            snippet = BeautifulSoup(item.get("snippet", ""), "html.parser").get_text()
            
            # Get full content for top results
            content_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={title.replace(' ', '_')}&format=json"
            content_response = requests.get(content_url).json()
            page_id = next(iter(content_response["query"]["pages"]))
            full_content = content_response["query"]["pages"][page_id].get("extract", snippet)
            
            results.append({
                "title": title,
                "url": page_url,
                "snippet": snippet,
                "content": full_content,
                "relevance": compute_similarity(query_embedding, title + " " + full_content)
            })
            
        # Sort by relevance and take top max_results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return [{"title": r["title"], "url": r["url"], "snippet": r["snippet"], "content": r["content"], "relevance": r["relevance"]} for r in results[:max_results]]
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return []

# ArXiv Search
def search_arxiv(query, query_embedding, max_results=3):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=10"
    try:
        response = requests.get(url).text
        entries = response.split('<entry>')[1:]
        results = []
        
        for entry in entries:
            try:
                title = entry.split('<title>')[1].split('</title>')[0].strip()
                abstract = ""
                if "<summary>" in entry:
                    abstract = entry.split('<summary>')[1].split('</summary>')[0].strip()
                link = entry.split('<id>')[1].split('</id>')[0].strip()
                
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": abstract[:200] + "..." if len(abstract) > 200 else abstract,
                    "content": abstract,
                    "relevance": compute_similarity(query_embedding, title + " " + abstract)
                })
            except Exception as e:
                print(f"Error parsing ArXiv entry: {e}")
                continue
                
        # Sort by relevance and take top max_results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return [{"title": r["title"], "url": r["url"], "snippet": r["snippet"], "content": r["content"], "relevance": r["relevance"]} for r in results[:max_results]]
    except Exception as e:
        print(f"ArXiv search error: {e}")
        return []

# News API Search
def search_news(query, query_embedding, max_results=3):
    try:
        # Using NewsAPI.org
        base_url = "https://newsapi.org/v2/everything"
        api_key = "bb4256541ca24dbda24d80e21d29bd51"
        
        params = {
            'q': query,
            'apiKey': api_key,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': 10  # Get 10 results to filter for relevance
        }
        
        response = requests.get(base_url, params=params)
        if not response.ok:
            print(f"News API error: {response.status_code}")
            return []
            
        data = response.json()
        results = []
        
        if data.get('status') != 'ok' or 'articles' not in data:
            print("No news data in response")
            return []
            
        for article in data['articles']:
            try:
                title = article.get('title', '')
                url = article.get('url', '')
                description = article.get('description', '')
                source = article.get('source', {}).get('name', '')
                published_at = article.get('publishedAt', '')
                author = article.get('author', '')
                
                if title and url:
                    # Create a rich snippet with source, date, and author
                    snippet_parts = []
                    if description:
                        snippet_parts.append(description[:150] + "..." if len(description) > 150 else description)
                    if source:
                        snippet_parts.append(f"Source: {source}")
                    if published_at:
                        snippet_parts.append(f"Published: {published_at}")
                    if author:
                        snippet_parts.append(f"By: {author}")
                        
                    snippet = " | ".join(snippet_parts)
                    content = f"{title}. {description}"
                    
                    results.append({
                    "title": title,
                        "url": url,
                    "snippet": snippet,
                        "content": content,
                        "relevance": compute_similarity(query_embedding, content)
                })
            except Exception as e:
                print(f"Error processing news item: {e}")
                continue

        # Sort by relevance and take top max_results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
        
    except Exception as e:
        print(f"News search error: {e}")
        return []

# Reddit Search
def search_reddit(query, query_embedding, max_results=3):
    url = f"https://www.reddit.com/search.json?q={query}&limit=10"
    headers = {"User-Agent": "Search-App/1.0 (by /u/SearchAppDev)"}
    
    try:
        response = requests.get(url, headers=headers).json()
        results = []
        
        for post in response["data"]["children"]:
            post_data = post["data"]
            title = post_data["title"]
            url = f"https://www.reddit.com{post_data['permalink']}"
            selftext = post_data.get("selftext", "")
            
            results.append({
                "title": title,
                "url": url,
                "snippet": selftext[:200] + "..." if len(selftext) > 200 else selftext,
                "content": selftext,
                "relevance": compute_similarity(query_embedding, title + " " + selftext)
            })
            
        # Sort by relevance and take top max_results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return [{"title": r["title"], "url": r["url"], "snippet": r["snippet"], "content": r["content"], "relevance": r["relevance"]} for r in results[:max_results]]
    except Exception as e:
        print(f"Reddit search error: {e}")
        return []

# YouTube Search (No API key required)
def search_youtube(query, query_embedding, max_results=3):
    try:
        if not YOUTUBE_API_KEY:
            print("YouTube API key not found in environment variables")
            raise Exception("YouTube API key not configured")

        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 10,
            'type': 'video',
            'relevanceLanguage': 'en'
        }
        
        response = requests.get(base_url, params=params)
        if not response.ok:
            print(f"YouTube API error: Status code {response.status_code}")
            print(f"Response content: {response.text}")
            raise Exception(f"YouTube API error: {response.status_code}")
            
        data = response.json()
        results = []
        
        if 'items' not in data:
            print(f"No items in YouTube response: {data}")
            raise Exception("No items in YouTube response")
            
        for item in data['items']:
            try:
                video_id = item['id']['videoId']
                snippet = item['snippet']
                title = snippet.get('title', '')
                description = snippet.get('description', '')
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                if title and url:
                    content = f"{title}. {description}"
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": description[:200] + "..." if len(description) > 200 else description,
                        "content": content,
                        "relevance": compute_similarity(query_embedding, content)
                    })
                    
            except Exception as e:
                print(f"Error processing YouTube result: {e}")
                continue
                
        # Sort by relevance and take top max_results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
        
    except Exception as e:
        print(f"YouTube API search error: {e}")
        print("Falling back to web scraping method...")
        # Fallback to scraping search results if API fails
        try:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = requests.get(search_url, headers=headers)
            if not response.ok:
                print(f"YouTube scraping error: Status code {response.status_code}")
                return []
                
            # Extract video information from the page
            results = []
            try:
                # Find the initial data in the page
                start_marker = 'var ytInitialData = '
                end_marker = '};'
                
                content = response.text
                start_idx = content.find(start_marker)
                if start_idx == -1:
                    return []
                    
                start_idx += len(start_marker)
                end_idx = content.find(end_marker, start_idx) + 1
                
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Navigate through the JSON structure to find video results
                video_items = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [{}])[0].get('itemSectionRenderer', {}).get('contents', [])
                
                for item in video_items[:10]:
                    try:
                        video_renderer = item.get('videoRenderer', {})
                        if not video_renderer:
                            continue
                            
                        video_id = video_renderer.get('videoId', '')
                        title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', '')
                        description = video_renderer.get('descriptionSnippet', {}).get('runs', [{}])[0].get('text', '')
                        
                        if video_id and title:
                            url = f"https://www.youtube.com/watch?v={video_id}"
                            content = f"{title}. {description}"
                            
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": description[:200] + "..." if len(description) > 200 else description,
                                "content": content,
                                "relevance": compute_similarity(query_embedding, content)
                            })
                            
                    except Exception as e:
                        print(f"Error processing YouTube result item: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error parsing YouTube page data: {e}")
                return []
                
            # Sort by relevance and take top max_results
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results[:max_results]
            
        except Exception as e:
            print(f"YouTube fallback search error: {e}")
            return []
            
        return []

# Web Search using DuckDuckGo
def search_web(query, query_embedding, max_results=3):
    try:
        # Using direct HTTP request to DuckDuckGo
        url = "https://html.duckduckgo.com/html/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        data = {
            'q': query,
            's': '0',
            'dc': '20'
        }
        
        response = requests.post(url, headers=headers, data=data)
        if not response.ok:
            print(f"Web search error: Status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Find all search result elements
        search_results = soup.find_all('div', {'class': 'result'})
        
        for result in search_results[:10]:  # Process top 10 results
            try:
                # Extract title and link
                title_elem = result.find('a', {'class': 'result__a'})
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                url = title_elem['href']
                
                # Extract snippet
                snippet_elem = result.find('a', {'class': 'result__snippet'})
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                if title and url:
                    # Clean the URL if it's a redirect URL
                    if url.startswith('/'):
                        url = f"https://duckduckgo.com{url}"
                    
                    content = f"{title}. {snippet}"
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "content": content,
                        "relevance": compute_similarity(query_embedding, content)
                    })
            
            except Exception as e:
                print(f"Error processing web result: {e}")
                continue
        
        # Sort by relevance and take top max_results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
        
    except Exception as e:
        print(f"Web search error: {e}")
        # Fallback to alternative search if main search fails
        try:
            # Using Qwant as fallback
            qwant_url = f"https://api.qwant.com/v3/search/web"
            params = {
                'q': query,
                'locale': 'en_US',
                'count': 10
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(qwant_url, params=params, headers=headers)
            if not response.ok:
                return []
                
            data = response.json()
            results = []
            
            if 'data' in data and 'result' in data['data'] and 'items' in data['data']['result']:
                for item in data['data']['result']['items']:
                    title = item.get('title', '')
                    url = item.get('url', '')
                    snippet = item.get('description', '')
                    
                    if title and url:
                        content = f"{title}. {snippet}"
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "content": content,
                            "relevance": compute_similarity(query_embedding, content)
                        })
                
                # Sort by relevance and take top max_results
                results.sort(key=lambda x: x["relevance"], reverse=True)
                return results[:max_results]
                
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
            
        return []

def generate_comprehensive_summary(query, all_results):
    """Generate a comprehensive summary from all search results."""
    # Combine content from all sources, prioritizing high relevance results
    combined_content = f"Information about {query}:\n\n"
    
    # Sort all results by relevance
    flat_results = []
    for source, results in all_results.items():
        for result in results:
            flat_results.append({
                "source": source,
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "relevance": result["relevance"]
            })
    
    # Sort by relevance, highest first
    flat_results.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Get top 5 most relevant pieces of content
    top_contents = []
    sources_included = set()
    
    for result in flat_results:
        # Ensure diverse sources
        if len(top_contents) < 5 or result["source"] not in sources_included:
            top_contents.append(result["content"])
            sources_included.add(result["source"])
            
        if len(top_contents) >= 8:  # Limit to 8 total sources
            break
    
    # Combine content (limit length to avoid tokenizer limits)
    combined_text = " ".join(top_contents)
    combined_text = combined_text[:3800]  # Limit input size for summarizer
    
    try:
        # Generate comprehensive summary
        summary = summarizer(combined_text, max_length=250, min_length=100, do_sample=False)[0]["summary_text"]
        
        # Generate source-specific mini-summaries
        source_summaries = {}
        for source, results in all_results.items():
            if results:
                source_text = " ".join([r["content"] for r in results[:2]])[:1500]  # Take top 2 results
                if len(source_text) > 200:  # Only summarize if we have enough content
                    try:
                        source_summary = summarizer(source_text, max_length=100, min_length=30, do_sample=False)[0]["summary_text"]
                        source_summaries[source] = source_summary
                    except Exception as e:
                        print(f"Error summarizing {source} content: {e}")
                        source_summaries[source] = results[0]["snippet"] if results[0]["snippet"] else "Summary not available."
        
        return {
            "main_summary": summary,
            "source_summaries": source_summaries
        }
    except Exception as e:
        print(f"Error generating summary: {e}")
        return {
            "main_summary": f"Information about {query} could not be summarized due to an error.",
            "source_summaries": {}
        }

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    print(f"Received search query: {query}")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Generate embedding for the query once to reuse for all searches
        query_embedding = get_embedding(query)
        print("Generated query embedding")
        
        # Run searches using ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            print("Starting parallel searches...")
            # Submit search tasks
            futures = {
                'web': executor.submit(search_web, query, query_embedding, 3),
                'wikipedia': executor.submit(search_wikipedia, query, query_embedding, 3),
                'arxiv': executor.submit(search_arxiv, query, query_embedding, 3),
                'news': executor.submit(search_news, query, query_embedding, 3),
                'reddit': executor.submit(search_reddit, query, query_embedding, 3),
                'youtube': executor.submit(search_youtube, query, query_embedding, 3)
            }
            
            # Get results
            results = {}
            for source, future in futures.items():
                try:
                    results[source] = future.result()
                    print(f"{source.capitalize()} results: {len(results[source])}")
                except Exception as e:
                    print(f"Error getting {source} results: {e}")
                    results[source] = []
        
        # Filter results by relevance and remove duplicates across all sources
        all_results = []
        for source, source_results in results.items():
            filtered_results = filter_relevant_results(source_results, query_embedding, threshold=0.3)
            for result in filtered_results:
                result['source'] = source
                all_results.append(result)
        
        # Remove duplicates from all results
        unique_results = remove_duplicates(all_results)
        
        # Sort by relevance and organize by source
        unique_results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Reorganize results by source
        organized_results = {
            'web': [],
            'wikipedia': [],
            'arxiv': [],
            'news': [],
            'reddit': [],
            'youtube': []
        }
        
        for result in unique_results:
            source = result.pop('source')  # Remove source from result dict
            if len(organized_results[source]) < 3:  # Limit to top 3 per source
                organized_results[source].append(result)
        
        response_data = {
            "query": query,
            "web": organized_results['web'],
            "wikipedia": organized_results['wikipedia'],
            "arxiv": organized_results['arxiv'],
            "news": organized_results['news'],
            "reddit": organized_results['reddit'],
            "youtube": organized_results['youtube']
        }
        
        print("Sending response...")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)