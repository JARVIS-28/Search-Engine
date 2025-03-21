# from flask import Flask, request, jsonify
# from transformers import pipeline
# import requests

# app = Flask(__name__)

# # Summarization Model
# summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

# # New Model for Extracting Top Relevant Results
# from sentence_transformers import SentenceTransformer, util
# embedder = SentenceTransformer('all-MiniLM-L6-v2')

# # Function to calculate dynamic summarization lengths
# def get_dynamic_lengths(text):
#     input_length = len(text.split())
#     max_length = min(max(input_length // 2, 20), 150)  # Max limit of 150
#     min_length = min(max(input_length // 4, 15), max_length - 10)
#     return max_length, min_length

# # Function to extract relevant results using embeddings
# def get_top_relevant_results(query, results, top_n=3):
#     query_embedding = embedder.encode(query, convert_to_tensor=True)
#     scores = [
#         (result, util.pytorch_cos_sim(query_embedding, embedder.encode(result['summary'], convert_to_tensor=True)).item())
#         for result in results
#     ]
#     sorted_results = sorted(scores, key=lambda x: x[1], reverse=True)
#     return [result[0] for result in sorted_results[:top_n]]

# # Data Fetching Function
# def fetch_data(query):
#     sources = [
#         f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}",
#         f"https://www.reddit.com/r/{query}/.json",
#         f"https://api.twitter.com/2/tweets/search/recent?query={query}"
#     ]

#     results = []
#     for source in sources:
#         try:
#             response = requests.get(source)
#             data = response.json()

#             # Wikipedia
#             if 'extract' in data:
#                 max_len, min_len = get_dynamic_lengths(data['extract'])
#                 summary = summarizer(data['extract'], max_length=max_len, min_length=min_len, do_sample=False)
#                 results.append({
#                     'title': data['title'],
#                     'summary': summary[0]['summary_text'],
#                     'link': data['content_urls']['desktop']['page']
#                 })

#             # Reddit
#             elif 'data' in data and 'children' in data['data']:
#                 for post in data['data']['children'][:3]:  # Top 3 Reddit posts
#                     results.append({
#                         'title': post['data']['title'],
#                         'summary': post['data']['selftext'][:300] + "...",
#                         'link': f"https://reddit.com{post['data']['permalink']}"
#                     })

#             # Twitter (Placeholder since live Twitter API requires proper auth)
#             elif 'data' in data:
#                 for tweet in data['data'][:3]:  # Top 3 tweets
#                     results.append({
#                         'title': 'Tweet',
#                         'summary': tweet['text'],
#                         'link': f"https://twitter.com/i/web/status/{tweet['id']}"
#                     })

#         except Exception as e:
#             continue

#     return get_top_relevant_results(query, results)

# # Search Endpoint
# @app.route('/search', methods=['GET'])
# def search():
#     query = request.args.get('query')
#     if not query:
#         return jsonify({'error': 'Query parameter is required'}), 400

#     results = fetch_data(query)
#     return jsonify({'results': results})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)



# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from transformers import pipeline
# import requests
# from sentence_transformers import SentenceTransformer, util

# app = Flask(__name__)
# CORS(app)  # Enables Cross-Origin Requests

# # Summarization Model
# summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

# # Embedding Model
# embedder = SentenceTransformer('all-MiniLM-L6-v2')

# # Function to calculate dynamic summarization lengths
# def get_dynamic_lengths(text):
#     input_length = len(text.split())
#     max_length = min(max(input_length // 2, 20), 150)  
#     min_length = min(max(input_length // 4, 15), max_length - 10)
#     return max_length, min_length

# # Extract relevant results
# def get_top_relevant_results(query, results, top_n=3):
#     query_embedding = embedder.encode(query, convert_to_tensor=True)
#     scores = [
#         (result, util.pytorch_cos_sim(query_embedding, embedder.encode(result['summary'], convert_to_tensor=True)).item())
#         for result in results
#     ]
#     sorted_results = sorted(scores, key=lambda x: x[1], reverse=True)
#     return [result[0] for result in sorted_results[:top_n]]

# # Data Fetching Function
# def fetch_data(query):
#     sources = [
#         f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}",
#         f"https://www.reddit.com/r/{query}/.json",
#         f"https://api.twitter.com/2/tweets/search/recent?query={query}"
#     ]

#     results = []
#     for source in sources:
#         try:
#             response = requests.get(source)
#             data = response.json()

#             if 'extract' in data:
#                 max_len, min_len = get_dynamic_lengths(data['extract'])
#                 summary = summarizer(data['extract'], max_length=max_len, min_length=min_len, do_sample=False)
#                 results.append({
#                     'title': data['title'],
#                     'summary': summary[0]['summary_text'],
#                     'link': data['content_urls']['desktop']['page']
#                 })
#             elif 'data' in data and 'children' in data['data']:
#                 for post in data['data']['children'][:3]:
#                     results.append({
#                         'title': post['data']['title'],
#                         'summary': post['data']['selftext'][:300] + "...",
#                         'link': f"https://reddit.com{post['data']['permalink']}"
#                     })
#             elif 'data' in data:
#                 for tweet in data['data'][:3]:
#                     results.append({
#                         'title': 'Tweet',
#                         'summary': tweet['text'],
#                         'link': f"https://twitter.com/i/web/status/{tweet['id']}"
#                     })
#         except Exception:
#             continue

#     return get_top_relevant_results(query, results)

# @app.route('/search', methods=['GET'])
# def search():
#     query = request.args.get('query')
#     if not query:
#         return jsonify({'error': 'Query parameter is required'}), 400

#     results = fetch_data(query)
#     return jsonify({'results': results})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import requests
from sentence_transformers import SentenceTransformer, util
from cachetools import TTLCache

app = Flask(__name__)
CORS(app)

# Summarization Model
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

# Embedding Model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Cache for improved performance (expires in 10 minutes)
cache = TTLCache(maxsize=100, ttl=600)

# Function to calculate dynamic summarization lengths
def get_dynamic_lengths(text):
    input_length = len(text.split())
    max_length = min(max(input_length, 150), 500)  
    min_length = min(max(input_length // 2, 100), max_length - 50)
    return max_length, min_length

# Extract top relevant results
def get_top_relevant_results(query, results, top_n=3):
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    scores = [
        (result, util.pytorch_cos_sim(query_embedding, embedder.encode(result['summary'], convert_to_tensor=True)).item())
        for result in results
    ]
    sorted_results = sorted(scores, key=lambda x: x[1], reverse=True)
    return [result[0] for result in sorted_results[:top_n]]

# Highlight keywords in text
def highlight_keywords(text, keywords):
    for word in keywords.split():
        text = text.replace(word, f"**{word}**")
    return text

# Data fetching function
def fetch_data(query, page=1, per_page=3):
    if query in cache:
        return cache[query]

    sources = [
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}",
        f"https://www.reddit.com/r/{query}/.json",
        f"https://api.twitter.com/2/tweets/search/recent?query={query}",
        f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={per_page}",
        f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={per_page}",
        f"https://newsapi.org/v2/everything?q={query}&apiKey=bb4256541ca24dbda24d80e21d29bd51"
    ]

    results = []
    for source in sources:
        try:
            response = requests.get(source)
            response.raise_for_status()  
            data = response.json()

            if 'extract' in data:
                max_len, min_len = get_dynamic_lengths(data['extract'])
                summary = summarizer(data['extract'], max_length=max_len, min_length=min_len, do_sample=False)
                results.append({
                    'title': data['title'],
                    'summary': highlight_keywords(summary[0]['summary_text'], query),
                    'link': data['content_urls']['desktop']['page']
                })
            elif 'data' in data and 'children' in data['data']:
                for post in data['data']['children'][:per_page]:
                    results.append({
                        'title': post['data']['title'],
                        'summary': highlight_keywords(post['data']['selftext'][:500] + "...", query),
                        'link': f"https://reddit.com{post['data']['permalink']}"
                    })
            elif 'data' in data:
                for tweet in data['data'][:per_page]:
                    tweet_text = tweet.get('text', 'No text available')
                    tweet_link = f"https://twitter.com/i/web/status/{tweet['id']}" if 'id' in tweet else 'No link available'
                    results.append({
                        'title': 'Tweet',
                        'summary': highlight_keywords(tweet_text, query),
                        'link': tweet_link
                })

            feed_data = data.get('feed', {})
            if 'entry' in feed_data:
                for entry in feed_data['entry'][:per_page]:
                    results.append({
                        'title': entry.get('title', {}).get('$t', 'No title available'),
                        'summary': entry.get('summary', {}).get('$t', 'No summary available'),
                        'link': entry.get('link', [{}])[0].get('href', 'No link available')
                    })

            elif 'papers' in data:
                for paper in data['papers']:
                    results.append({
                        'title': paper['title'],
                        'summary': highlight_keywords(paper.get('abstract', 'No abstract available'), query),
                        'link': paper['url']
                    })
            elif 'articles' in data:
                for article in data['articles'][:per_page]:
                    results.append({
                        'title': article['title'],
                        'summary': highlight_keywords(article['description'], query),
                        'link': article['url']
                    })
        except requests.exceptions.RequestException:
            continue  

    # Generate main summary by combining top results
    combined_text = " ".join(result['summary'] for result in results)
    main_summary = summarizer(combined_text, max_length=200, min_length=100, do_sample=False)[0]['summary_text']

    # Top 3 results for each source
    top_results = get_top_relevant_results(query, results)
    cache[query] = {'main_summary': main_summary, 'results': top_results}  
    return cache[query]

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    page = int(request.args.get('page', 1))  
    per_page = int(request.args.get('per_page', 3))

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    results = fetch_data(query, page, per_page)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
