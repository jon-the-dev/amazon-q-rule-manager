# Amazon Q Rule Manager

A robust manager for Amazon Q Developer rules with global and workspace support.

[![PyPI version](https://badge.fury.io/py/amazon-q-rule-manager.svg)](https://badge.fury.io/py/amazon-q-rule-manager)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Amazon Q Rule Manager is a comprehensive tool for managing Amazon Q Developer rules across your development environment. It supports both global rules (available system-wide) and workspace-specific rules, with rich metadata, dependency management, and conflict resolution.

## Features

- **Global Rule Management**: Install and manage rules system-wide
- **Workspace Support**: Manage rules per project/workspace
- **Rich Metadata**: Detailed rule information including categories, tags, dependencies
- **Conflict Resolution**: Automatic detection and handling of rule conflicts
- **Dependency Management**: Ensure rule dependencies are satisfied
- **Search & Discovery**: Find rules by category, tags, or search queries
- **Import/Export**: Backup and share rule configurations
- **Modern CLI**: Beautiful command-line interface with progress indicators
- **Backward Compatibility**: Supports legacy command structure

## Installation

### From PyPI (Recommended)

```bash
pip install amazon-q-rule-manager
```

### From Source

```bash
git clone https://github.com/zerodaysec/amazonq-rules.git
cd amazonq-rules
pip install -e .
```

## Quick Start

### 1. Update Rule Catalog

```bash
# Update the rule catalog from remote source
amazon-q-rule-manager catalog update
```

### 2. Browse Available Rules

```bash
# List all available rules
amazon-q-rule-manager catalog list

# Filter by category
amazon-q-rule-manager catalog list --category python

# Search rules
amazon-q-rule-manager catalog list --search "aws lambda"

# Show detailed information about a rule
amazon-q-rule-manager catalog show aws
```

### 3. Install Rules Globally

```bash
# Install a rule globally (available to all projects)
amazon-q-rule-manager global-rules install python

# List globally installed rules
amazon-q-rule-manager global-rules list

# Uninstall a global rule
amazon-q-rule-manager global-rules uninstall python
```

### 4. Manage Workspaces

```bash
# Register a workspace
amazon-q-rule-manager workspace register /path/to/project --name my-project

# List registered workspaces
amazon-q-rule-manager workspace list

# Install rules to a workspace
amazon-q-rule-manager workspace install aws my-project
amazon-q-rule-manager workspace install terraform my-project

# List rules in a workspace
amazon-q-rule-manager workspace list-rules my-project

# Export workspace rules
amazon-q-rule-manager workspace export my-project /path/to/backup

# Import rules to workspace
amazon-q-rule-manager workspace import my-project /path/to/rules
```

## Command Reference

### Catalog Commands

- `catalog update [--force]` - Update rule catalog from remote source
- `catalog list [--category CATEGORY] [--tag TAG] [--search QUERY]` - List available rules
- `catalog show RULE_NAME` - Show detailed rule information

### Global Rules Commands

- `global-rules install RULE_NAME [--force]` - Install rule globally
- `global-rules uninstall RULE_NAME` - Uninstall global rule
- `global-rules list` - List globally installed rules

### Workspace Commands

- `workspace register PATH [--name NAME]` - Register a workspace
- `workspace unregister NAME` - Unregister a workspace
- `workspace list` - List registered workspaces
- `workspace install RULE_NAME WORKSPACE_NAME [--force]` - Install rule to workspace
- `workspace uninstall RULE_NAME WORKSPACE_NAME` - Uninstall rule from workspace
- `workspace list-rules WORKSPACE_NAME` - List workspace rules
- `workspace export WORKSPACE_NAME PATH` - Export workspace rules
- `workspace import WORKSPACE_NAME PATH [--force]` - Import rules to workspace

## Rule Categories

The manager supports the following rule categories:

- **AWS**: Guidelines for AWS resources, monitoring, and best practices
- **Python**: Python development standards and coding practices
- **Terraform**: Infrastructure as Code best practices and security
- **JavaScript/TypeScript**: Frontend and Node.js development guidelines
- **React**: React-specific development patterns and practices
- **Ruby**: Ruby development standards and conventions
- **Serverless**: Serverless framework and Lambda best practices

## Available Rules

### AWS Rules
- **aws**: Guidelines for AWS resources including alarms, tagging, and default values
- **sls-framework**: Serverless Framework development and deployment guidelines

### Python Rules
- **python**: Standards for Python development including version requirements and coding practices

### Terraform Rules
- **terraform**: Best practices for Terraform including version requirements and security principles

### Frontend Rules
- **react**: React development guidelines including component structure and best practices

### Ruby Rules
- **ruby**: Ruby development standards including style guide and best practices

## Web Interface

The Amazon Q Rule Manager includes a modern React frontend for browsing the rules catalog online:

🌐 **Live Demo**: [https://zerodaysec.github.io/amazonq-rules](https://zerodaysec.github.io/amazonq-rules)

### Features

- **Matrix-inspired Design**: Dark theme with neon green accents
- **Advanced Search**: Search rules by name, description, tags, or category  
- **Category Filtering**: Filter by programming language or technology
- **Detailed Rule Pages**: Comprehensive information about each rule
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Automatically synced with the latest catalog

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend is automatically deployed to GitHub Pages when changes are pushed to the main branch.

## Configuration

The tool stores configuration in platform-specific directories:

- **Linux**: `~/.config/amazon-q-rule-manager/`
- **macOS**: `~/Library/Application Support/amazon-q-rule-manager/`
- **Windows**: `%APPDATA%\amazon-q-rule-manager\`

### Environment Variables

- `AMAZONQ_RULES_URL`: Override default remote catalog URL
- `AMAZONQ_RULES_SOURCE`: Override default local source directory

## Rule Structure

Rules are stored as Markdown files with rich metadata:

```json
{
  "name": "python",
  "title": "Python Development Standards",
  "description": "Standards for Python development including version requirements and coding practices",
  "category": "python",
  "version": "1.1.0",
  "tags": ["python", "development", "standards"],
  "dependencies": [],
  "conflicts": [],
  "min_python_version": "3.12",
  "supported_languages": ["python"],
  "examples": [
    "Use threading for parallel operations",
    "Always use argparse for CLI tools"
  ]
}
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/zerodaysec/amazonq-rules.git
cd amazonq-rules

# Complete development setup (installs deps, hooks, syncs data)
make setup-dev

# Or manually:
pip install -e ".[dev]"
make install-hooks
make sync-frontend
```

### Development Workflow

The project includes automated syncing between the backend catalog and frontend:

1. **Automatic Sync**: When you modify `amazon_q_rule_manager/data/rules_catalog.json` or any rule files in `rules/`, the pre-commit hook automatically syncs the data to `frontend/public/`

2. **Manual Sync**: Run `make sync-frontend` to manually sync data

3. **Frontend Development**: 
   ```bash
   make dev-frontend  # Starts development server with latest data
   ```

4. **GitHub Actions**: The frontend deployment only triggers when:
   - Frontend files change (`frontend/**`)
   - Catalog data changes (`amazon_q_rule_manager/data/rules_catalog.json`)
   - Rule files change (`rules/*.md`)

### Available Make Commands

```bash
make help           # Show all available commands
make sync-frontend  # Sync catalog and rules to frontend
make install-hooks  # Install Git hooks
make dev-frontend   # Start frontend dev server
make build-frontend # Build frontend for production
make test          # Run Python tests
make lint          # Run linting
make format        # Format code
make clean         # Clean build artifacts
```

### Run Tests

```bash
pytest
pytest --cov=amazon_q_rule_manager
```

### Code Formatting

```bash
make format  # Format all code
# Or manually:
black amazon_q_rule_manager/
flake8 amazon_q_rule_manager/
mypy amazon_q_rule_manager/
```

### Build Package

```bash
python -m build
```

## Backward Compatibility

The tool maintains backward compatibility with the original script:

```bash
# Legacy commands (deprecated but supported)
amazon-q-rule-manager install python /path/to/project
amazon-q-rule-manager list /path/to/project
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/zerodaysec/amazonq-rules/issues)
- **Documentation**: [GitHub Repository](https://github.com/zerodaysec/amazonq-rules)

## Changelog

### Version 1.0.0
- Initial release with global and workspace rule management
- Rich metadata support with categories, tags, and dependencies
- Modern CLI interface with progress indicators
- Conflict resolution and dependency management
- Import/export functionality
- Backward compatibility with legacy commands
