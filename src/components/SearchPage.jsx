import React, { useState, useEffect } from 'react';
import './SearchPage.css';
import DarkModeToggle from './DarkModeToggle';
import ParticleEffect from './ParticleEffect';

const SearchPage = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState({});
    const [isSearching, setIsSearching] = useState(false);
    const [searchHistory, setSearchHistory] = useState([]);
    const [error, setError] = useState('');
    const [darkMode, setDarkMode] = useState(() => {
        // Get initial dark mode from localStorage or default to true
        const savedMode = localStorage.getItem('darkMode');
        return savedMode !== null ? JSON.parse(savedMode) : true;
    });
    const [hasSearched, setHasSearched] = useState(false);

    // Update localStorage when dark mode changes
    useEffect(() => {
        localStorage.setItem('darkMode', JSON.stringify(darkMode));
    }, [darkMode]);

    const handleSearch = async () => {
        if (!query.trim() || isSearching) return;

        setIsSearching(true);
        setError('');

        try {
            const response = await fetch(`http://localhost:5000/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data) {
                const organizedResults = {
                    web: (data.web || []).map(result => ({ ...result, source: 'Web' })),
                    wikipedia: (data.wikipedia || []).map(result => ({ ...result, source: 'Wikipedia' })),
                    arxiv: (data.arxiv || []).map(result => ({ ...result, source: 'ArXiv' })),
                    news: (data.news || []).map(result => ({ ...result, source: 'News' })),
                    reddit: (data.reddit || []).map(result => ({ ...result, source: 'Reddit' })),
                    youtube: (data.youtube || []).map(result => ({ ...result, source: 'YouTube' }))
                };
                
                setResults(organizedResults);
                setSearchHistory((prevHistory) => [...new Set([query, ...prevHistory])]);
                setHasSearched(true);
            } else {
                setResults({});
            }
        } catch (error) {
            console.error('Error fetching search results:', error);
            setError('Failed to fetch results. Please try again later.');
            setResults({});
        }

        setIsSearching(false);
    };

    const handleClearResults = () => {
        setResults({});
        setError('');
        setHasSearched(false);
        setQuery('');
    };

    const toggleDarkMode = () => setDarkMode(!darkMode);

    return (
        <div className={`search-container ${darkMode ? 'dark-mode' : 'light-mode'} ${hasSearched ? 'has-results' : ''}`}>
            <ParticleEffect darkMode={darkMode} />
            <div className={`search-content ${hasSearched ? 'has-results' : ''}`}>
                <div className={`header ${hasSearched ? 'top' : 'centered'}`}>
                    <div className="search-input-container">
                        <input
                            type="text"
                            placeholder="Search the infinite dataverse..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        />
                    </div>
                    <div className="button-container">
                        <button onClick={handleSearch} disabled={isSearching}>
                            {isSearching ? 'SEARCHING...' : 'SEARCH'}
                        </button>
                        <button onClick={handleClearResults} className="clear-button">
                            CLEAR
                        </button>
                        <DarkModeToggle darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
                    </div>
                </div>

                {error && <p className="error-message">{error}</p>}

                <div className="search-results-container">
                    {Object.entries(results).map(([source, sourceResults]) => (
                        sourceResults && sourceResults.length > 0 && (
                            <div key={source} className="source-section">
                                <h2 className="source-title">{source.charAt(0).toUpperCase() + source.slice(1)} Results</h2>
                                <div className="source-results">
                                    {sourceResults.map((result, index) => (
                                        <div key={index} className="result-card">
                                            <div className={`result-source ${source.toLowerCase()}`}>
                                                {source}
                                            </div>
                                            <h3>{result.title}</h3>
                                            <p>{result.snippet || result.summary}</p>
                                            {source === 'youtube' && (
                                                <div className="video-preview">
                                                    <iframe
                                                        width="100%"
                                                        height="200"
                                                        src={`https://www.youtube.com/embed/${result.url.split('v=')[1]}`}
                                                        frameBorder="0"
                                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                                        allowFullScreen
                                                        title={`YouTube video: ${result.title}`}
                                                    ></iframe>
                                                </div>
                                            )}
                                            <a href={result.url} target="_blank" rel="noopener noreferrer">
                                                {source === 'youtube' ? 'Watch Video' : 'Read More'}
                                            </a>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    ))}
                </div>

                {searchHistory.length > 0 && (
                    <div className="search-history">
                        <h4>Search History</h4>
                        <ul>
                            {searchHistory.map((entry, index) => (
                                <li key={index} onClick={() => {
                                    setQuery(entry);
                                    handleSearch();
                                }}>
                                    {entry}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SearchPage;
