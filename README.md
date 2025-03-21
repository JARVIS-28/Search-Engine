# Infinite Dataverse Search Engine

A modern, responsive search engine application built with React that provides a beautiful user interface for searching across multiple data sources. Features a stunning particle animation background and seamless dark/light mode transitions.

![Search Engine Demo](demo-screenshot.png)

## 🌟 Features

- **Beautiful Particle Animation Background**
  - Interactive particle effects that respond to cursor movement
  - Seamless animations and transitions
  - Customizable particle behavior

- **Advanced Search Functionality**
  - Real-time search results
  - Multi-source search integration (Reddit, Web, etc.)
  - Search history tracking
  - Clean and organized result display

- **Modern UI/UX**
  - Dark/Light mode toggle
  - Responsive design for all screen sizes
  - Smooth animations and transitions
  - Elegant card-based result layout

- **Accessibility**
  - Keyboard navigation support
  - Screen reader friendly
  - High contrast mode
  - Focus management

## 🚀 Technologies Used

- **Frontend**
  - React.js
  - React Router
  - CSS3 with modern features
  - HTML5 Canvas for particles

- **Backend**
  - Python (Flask)
  - Reddit API integration
  - Web scraping capabilities

## 💻 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/infinite-dataverse-search.git
   ```

2. Install frontend dependencies:
   ```bash
   cd search-app
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Start the frontend development server:
   ```bash
   cd search-app
   npm start
   ```

5. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

## 🔧 Configuration

1. Backend Configuration:
   - Create a `.env` file in the backend directory
   - Add your Reddit API credentials:
     ```
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     ```

2. Frontend Configuration:
   - The frontend will run on `http://localhost:3000`
   - The backend API is configured to run on `http://localhost:5000`

## 🎨 Project Structure

```
search-app/
├── src/
│   ├── components/
│   │   ├── LandingPage/
│   │   ├── SearchPage/
│   │   ├── ParticleEffect/
│   │   └── DarkModeToggle/
│   ├── App.js
│   └── App.css
└── backend/
    ├── app.py
    └── requirements.txt
```

## 🌈 Features in Detail

### Particle Animation
- Interactive background with dynamic particle movement
- Particles respond to cursor movement
- Configurable particle density and behavior

### Search Functionality
- Real-time search results
- Multiple data source integration
- Search history tracking
- Organized result categorization

### UI Components
- Modern, clean interface
- Responsive design
- Dark/Light mode toggle
- Smooth transitions and animations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Particle animation inspired by various open-source projects
- UI design influenced by modern search engines
- Special thanks to the React and Python communities

## 📧 Contact

Your Name - your.email@example.com
Project Link: [https://github.com/yourusername/infinite-dataverse-search](https://github.com/yourusername/infinite-dataverse-search)
