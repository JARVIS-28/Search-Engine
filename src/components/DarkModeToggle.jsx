import React from 'react';
import './DarkModeToggle.css';

const DarkModeToggle = ({ darkMode, toggleDarkMode }) => {
    return (
        <button onClick={toggleDarkMode} className="dark-mode-toggle">
            {darkMode ? '☀️ LIGHT' : '🌙 DARK'}
        </button>
    );
};

export default DarkModeToggle;
