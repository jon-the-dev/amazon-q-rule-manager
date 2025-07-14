import React from 'react';
import './CategoryFilter.css';

const CategoryFilter = ({ selectedCategory, onCategoryChange, rules }) => {
  const categories = ['all', ...new Set(rules.map(rule => rule.category))].sort();
  
  const getCategoryCount = (category) => {
    if (category === 'all') return rules.length;
    return rules.filter(rule => rule.category === category).length;
  };

  const getCategoryColor = (category) => {
    const colors = {
      aws: '#ff9900',
      python: '#3776ab',
      terraform: '#623ce4',
      javascript: '#f7df1e',
      react: '#61dafb',
      ruby: '#cc342d',
      serverless: '#fd5750'
    };
    return colors[category] || '#00ff41';
  };

  return (
    <div className="category-filter">
      <label className="filter-label">Category:</label>
      <div className="category-buttons">
        {categories.map(category => (
          <button
            key={category}
            onClick={() => onCategoryChange(category)}
            className={`category-button ${selectedCategory === category ? 'active' : ''}`}
            style={{
              '--category-color': category !== 'all' ? getCategoryColor(category) : '#00ff41'
            }}
          >
            <span className="category-name">
              {category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
            </span>
            <span className="category-count">
              {getCategoryCount(category)}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CategoryFilter;
