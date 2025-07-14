import React, { useState, useEffect } from 'react';
import RuleCard from '../components/RuleCard';
import SearchBar from '../components/SearchBar';
import CategoryFilter from '../components/CategoryFilter';
import './Home.css';

const Home = () => {
  const [rules, setRules] = useState([]);
  const [filteredRules, setFilteredRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetchRules();
  }, []);

  useEffect(() => {
    filterRules();
  }, [rules, searchTerm, selectedCategory]);

  const fetchRules = async () => {
    try {
      const response = await fetch('/amazonq-rules/rules_catalog.json');
      if (!response.ok) {
        throw new Error('Failed to fetch rules catalog');
      }
      const data = await response.json();
      const rulesArray = Object.values(data.rules);
      setRules(rulesArray);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const filterRules = () => {
    let filtered = rules;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(rule =>
        rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(rule => rule.category === selectedCategory);
    }

    setFilteredRules(filtered);
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
  };

  if (loading) {
    return (
      <div className="home">
        <div className="container">
          <div className="loading-container">
            <div className="loading"></div>
            <p>Loading rules catalog...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home">
        <div className="container">
          <div className="error-container">
            <h2>Error Loading Rules</h2>
            <p>{error}</p>
            <button onClick={fetchRules} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="home">
      <div className="container">
        <div className="hero-section">
          <h1 className="hero-title glitch" data-text="Amazon Q Rules">
            Amazon Q Rules
          </h1>
          <p className="hero-subtitle">
            Discover and manage development rules for AWS, Python, Terraform, and more
          </p>
        </div>

        <div className="filters-section">
          <SearchBar onSearch={handleSearch} />
          <CategoryFilter 
            selectedCategory={selectedCategory}
            onCategoryChange={handleCategoryChange}
            rules={rules}
          />
        </div>

        <div className="stats-section">
          <div className="stat">
            <span className="stat-number">{filteredRules.length}</span>
            <span className="stat-label">Rules Found</span>
          </div>
          <div className="stat">
            <span className="stat-number">{new Set(rules.map(r => r.category)).size}</span>
            <span className="stat-label">Categories</span>
          </div>
          <div className="stat">
            <span className="stat-number">{rules.reduce((acc, r) => acc + r.tags.length, 0)}</span>
            <span className="stat-label">Total Tags</span>
          </div>
        </div>

        <div className="rules-grid">
          {filteredRules.map(rule => (
            <RuleCard key={rule.name} rule={rule} />
          ))}
        </div>

        {filteredRules.length === 0 && !loading && (
          <div className="no-results">
            <h3>No rules found</h3>
            <p>Try adjusting your search terms or category filter.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
