import React from 'react';
import { Link } from 'react-router-dom';
import './RuleCard.css';

const RuleCard = ({ rule }) => {
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

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="rule-card card-hover fade-in">
      <div className="rule-card-header">
        <div className="rule-category" style={{ color: getCategoryColor(rule.category) }}>
          {rule.category.toUpperCase()}
        </div>
        <div className="rule-version">v{rule.version}</div>
      </div>

      <div className="rule-card-body">
        <h3 className="rule-title">{rule.title}</h3>
        <p className="rule-description">{rule.description}</p>

        {rule.tags && rule.tags.length > 0 && (
          <div className="rule-tags">
            {rule.tags.slice(0, 4).map(tag => (
              <span key={tag} className="rule-tag">
                {tag}
              </span>
            ))}
            {rule.tags.length > 4 && (
              <span className="rule-tag-more">+{rule.tags.length - 4}</span>
            )}
          </div>
        )}

        {rule.examples && rule.examples.length > 0 && (
          <div className="rule-examples">
            <h4>Examples:</h4>
            <ul>
              {rule.examples.slice(0, 2).map((example, index) => (
                <li key={index}>{example}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="rule-card-footer">
        <div className="rule-meta">
          {rule.author && (
            <span className="rule-author">by {rule.author}</span>
          )}
          {rule.updated_at && (
            <span className="rule-date">Updated {formatDate(rule.updated_at)}</span>
          )}
        </div>

        <div className="rule-actions">
          <Link to={`/rule/${rule.name}`} className="btn btn-primary">
            View Details
          </Link>
          {rule.source_url && (
            <a 
              href={rule.source_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn btn-secondary"
            >
              Source
            </a>
          )}
        </div>
      </div>

      {(rule.dependencies?.length > 0 || rule.conflicts?.length > 0) && (
        <div className="rule-dependencies">
          {rule.dependencies?.length > 0 && (
            <div className="dependency-info">
              <span className="dependency-label">Depends on:</span>
              <span className="dependency-list">
                {rule.dependencies.join(', ')}
              </span>
            </div>
          )}
          {rule.conflicts?.length > 0 && (
            <div className="conflict-info">
              <span className="conflict-label">Conflicts with:</span>
              <span className="conflict-list">
                {rule.conflicts.join(', ')}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RuleCard;
