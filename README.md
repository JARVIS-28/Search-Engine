# Infinite Dataverse Search Engine

A modern search engine application built with React and Flask that provides an intuitive interface for searching across multiple data sources. The application features a responsive design with dark/light mode support and real-time search capabilities.

## 🌟 Key Features

### Search Capabilities
- Real-time search results with debouncing
- Multi-source data integration (Reddit, Web)
- Intelligent result ranking and aggregation
- Search history with local storage persistence

### User Interface
- Responsive design for all screen sizes
- Dark/Light mode theming
- Interactive particle animation background
- Clean, card-based result layout
- Keyboard navigation support
- Screen reader compatibility

## 🚀 Technical Stack

### Frontend Architecture
- **Core Framework**: React.js 18
- **State Management**: React Hooks and Context API
- **Routing**: React Router v6
- **Styling**: 
  - Modern CSS3 (Flexbox, Grid)
  - CSS Modules for component scoping
  - CSS Variables for theming
- **Performance**:
  - Debounced search inputs
  - Lazy loading components
  - Optimized re-renders
  - Local storage for persistence

### Backend Architecture
- **Core Framework**: 
  - Flask 2.0+
  - Flask-CORS for cross-origin handling
  - Werkzeug for WSGI interface

- **Search Implementation** (`search_api.py`):
  - Asynchronous search execution
  - Result aggregation system
  - Response caching layer
  - Rate limiting middleware

- **Data Sources**:
  - Reddit Integration:
    - PRAW (Python Reddit API Wrapper)
    - Subreddit content extraction
    - Comment thread analysis
  - Web Search:
    - Custom scraping implementation
    - URL validation
    - Content summarization

- **Data Processing**:
  - Text Processing:
    - NLTK for tokenization
    - Stop words filtering
    - Word lemmatization
  - Result Ranking:
    - TF-IDF scoring
    - Source reliability weighting
    - Content freshness scoring

## 💻 Getting Started

### Prerequisites
- Node.js 16+
- Python 3.8+
- npm or yarn
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JARVIS-28/Search-Engine.git
cd Search-Engine
```

2. Frontend setup:
```bash
cd search-app
npm install
```

3. Backend setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. Backend Environment:
Create `.env` in the backend directory:
```
FLASK_ENV=development
FLASK_APP=app.py
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

2. Start the services:

Frontend:
```bash
cd search-app
npm start
```

Backend:
```bash
cd backend
python app.py
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📁 Project Structure

```
search-app/
├── public/
├── src/
│   ├── components/
│   │   ├── SearchPage/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── ResultsList.jsx
│   │   │   └── SearchHistory.jsx
│   │   ├── ParticleEffect/
│   │   │   └── ParticleCanvas.jsx
│   │   └── DarkModeToggle/
│   │       └── ThemeToggle.jsx
│   ├── hooks/
│   │   ├── useDebounce.js
│   │   └── useTheme.js
│   ├── context/
│   │   └── ThemeContext.js
│   └── App.js
└── backend/
    ├── app.py
    ├── search_api.py
    ├── models/
    │   ├── text_processor.py
    │   └── ranking.py
    ├── utils/
    │   ├── cache.py
    │   └── rate_limiter.py
    └── requirements.txt
```

## 🔧 API Endpoints

### Search API
- `GET /api/search`
  - Query params: `q` (search term), `sources` (data sources)
  - Returns: JSON with ranked and aggregated results

### History API
- `GET /api/history`
  - Returns: Recent search history
- `POST /api/history`
  - Adds new search term to history

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/NewFeature`
3. Commit changes: `git commit -m 'Add NewFeature'`
4. Push to branch: `git push origin feature/NewFeature`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

JARVIS-28
Project Link: [https://github.com/JARVIS-28/Search-Engine](https://github.com/JARVIS-28/Search-Engine)
