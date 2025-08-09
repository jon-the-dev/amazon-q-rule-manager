import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import './RuleDetail.css';

const RuleDetail = () => {
  const { ruleName } = useParams();
  const [rule, setRule] = useState(null);
  const [ruleContent, setRuleContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRuleDetails = async () => {
      try {
        const basePath = process.env.PUBLIC_URL || '';
        // Fetch rule metadata
        const catalogResponse = await fetch(`${basePath}/rules_catalog.json`);
        if (!catalogResponse.ok) {
          throw new Error('Failed to fetch rules catalog');
        }
        const catalogData = await catalogResponse.json();
        const ruleData = catalogData.rules[ruleName];

        if (!ruleData) {
          throw new Error('Rule not found');
        }

        setRule(ruleData);

        // Fetch rule content (markdown)
        try {
          const contentResponse = await fetch(`${basePath}/rules/${ruleName}.md`);
          if (contentResponse.ok) {
            const content = await contentResponse.text();
            setRuleContent(content);
          }
        } catch (contentError) {
          console.warn('Could not fetch rule content:', contentError);
        }

        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchRuleDetails();
  }, [ruleName]);

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
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const parseMarkdownContent = (content) => {
    // Simple markdown parsing for display
    return content
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code>$1</code>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.+)$/gm, '<p>$1</p>')
      .replace(/<p><h/g, '<h')
      .replace(/<\/h([1-6])><\/p>/g, '</h$1>');
  };

  if (loading) {
    return (
      <div className="rule-detail">
        <div className="container">
          <div className="loading-container">
            <div className="loading"></div>
            <p>Loading rule details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rule-detail">
        <div className="container">
          <div className="error-container">
            <h2>Error Loading Rule</h2>
            <p>{error}</p>
            <Link to="/" className="btn btn-primary">
              Back to Rules
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rule-detail">
      <div className="container">
        <div className="breadcrumb">
          <Link to="/">Rules</Link>
          <span className="breadcrumb-separator">›</span>
          <span>{rule.title}</span>
        </div>

        <div className="rule-header">
          <div className="rule-header-main">
            <div className="rule-category-badge" style={{ color: getCategoryColor(rule.category) }}>
              {rule.category.toUpperCase()}
            </div>
            <h1 className="rule-title">{rule.title}</h1>
            <p className="rule-description">{rule.description}</p>
          </div>
          
          <div className="rule-header-meta">
            <div className="rule-version">v{rule.version}</div>
            {rule.updated_at && (
              <div className="rule-date">
                Updated {formatDate(rule.updated_at)}
              </div>
            )}
          </div>
        </div>

        <div className="rule-content-grid">
          <div className="rule-main-content">
            {ruleContent && (
              <div className="rule-content">
                <h2>Rule Content</h2>
                <div 
                  className="markdown-content"
                  dangerouslySetInnerHTML={{ __html: parseMarkdownContent(ruleContent) }}
                />
              </div>
            )}

            {rule.examples && rule.examples.length > 0 && (
              <div className="rule-examples-section">
                <h2>Examples</h2>
                <div className="examples-list">
                  {rule.examples.map((example, index) => (
                    <div key={index} className="example-item">
                      <span className="example-bullet">▸</span>
                      <span className="example-text">{example}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="rule-sidebar">
            <div className="rule-info-card">
              <h3>Rule Information</h3>
              
              {rule.author && (
                <div className="info-item">
                  <span className="info-label">Author:</span>
                  <span className="info-value">{rule.author}</span>
                </div>
              )}
              
              <div className="info-item">
                <span className="info-label">Category:</span>
                <span className="info-value" style={{ color: getCategoryColor(rule.category) }}>
                  {rule.category}
                </span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Version:</span>
                <span className="info-value">{rule.version}</span>
              </div>

              {rule.min_python_version && (
                <div className="info-item">
                  <span className="info-label">Min Python:</span>
                  <span className="info-value">{rule.min_python_version}</span>
                </div>
              )}

              {rule.supported_languages && rule.supported_languages.length > 0 && (
                <div className="info-item">
                  <span className="info-label">Languages:</span>
                  <div className="info-tags">
                    {rule.supported_languages.map(lang => (
                      <span key={lang} className="info-tag">{lang}</span>
                    ))}
                  </div>
                </div>
              )}

              {rule.aws_services && rule.aws_services.length > 0 && (
                <div className="info-item">
                  <span className="info-label">AWS Services:</span>
                  <div className="info-tags">
                    {rule.aws_services.map(service => (
                      <span key={service} className="info-tag">{service}</span>
                    ))}
                  </div>
                </div>
              )}

              {rule.terraform_providers && rule.terraform_providers.length > 0 && (
                <div className="info-item">
                  <span className="info-label">Terraform Providers:</span>
                  <div className="info-tags">
                    {rule.terraform_providers.map(provider => (
                      <span key={provider} className="info-tag">{provider}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {rule.tags && rule.tags.length > 0 && (
              <div className="rule-tags-card">
                <h3>Tags</h3>
                <div className="tags-list">
                  {rule.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}

            {(rule.dependencies?.length > 0 || rule.conflicts?.length > 0) && (
              <div className="rule-relations-card">
                <h3>Dependencies & Conflicts</h3>
                
                {rule.dependencies?.length > 0 && (
                  <div className="relation-section">
                    <h4 className="dependency-title">Dependencies</h4>
                    <div className="relation-list">
                      {rule.dependencies.map(dep => (
                        <Link key={dep} to={`/rule/${dep}`} className="relation-link dependency">
                          {dep}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                {rule.conflicts?.length > 0 && (
                  <div className="relation-section">
                    <h4 className="conflict-title">Conflicts</h4>
                    <div className="relation-list">
                      {rule.conflicts.map(conflict => (
                        <Link key={conflict} to={`/rule/${conflict}`} className="relation-link conflict">
                          {conflict}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="rule-actions-card">
              <h3>Actions</h3>
              <div className="action-buttons">
                {rule.source_url && (
                  <a 
                    href={rule.source_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                  >
                    View Source
                  </a>
                )}
                {rule.documentation_url && (
                  <a 
                    href={rule.documentation_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                  >
                    Documentation
                  </a>
                )}
                <Link to="/" className="btn btn-secondary">
                  Back to Rules
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RuleDetail;
