import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          <span className="logo-text glitch" data-text="Amazon Q">
            Amazon Q
          </span>
          <span className="logo-subtitle">Rule Manager</span>
        </Link>
        
        <nav className="nav">
          <Link to="/" className="nav-link">
            Rules Catalog
          </Link>
          <a 
            href="https://github.com/zerodaysec/amazonq-rules" 
            target="_blank" 
            rel="noopener noreferrer"
            className="nav-link"
          >
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
};

export default Header;
