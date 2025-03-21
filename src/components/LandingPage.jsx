import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';
import ParticleEffect from './ParticleEffect';

const LandingPage = () => {
    const navigate = useNavigate();

    const handleButtonClick = () => {
        const vortex = document.createElement('div');
        vortex.className = 'vortex-animation';
        document.body.appendChild(vortex);

        setTimeout(() => {
            vortex.remove();
            navigate('/search');
        }, 1000);
    };

    return (
        <div className="landing-container">
            <ParticleEffect darkMode={true} />
            <div className="landing-content">
                <h1>Explore the Infinite Dataverse</h1>
                <p>Navigate through vast information landscapes with ease.</p>
                <button onClick={handleButtonClick}>ENTER</button>
            </div>
        </div>
    );
};

export default LandingPage;
