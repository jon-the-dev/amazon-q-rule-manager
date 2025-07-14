# Deployment Guide

This guide covers how to deploy the Amazon Q Rule Manager to PyPI and set up the development environment.

## Prerequisites

- Python 3.12 or higher
- Git
- PyPI account (for publishing)
- TestPyPI account (for testing)

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zerodaysec/amazonq-rules.git
   cd amazonq-rules
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Testing

Run the test suite:
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=amazon_q_rule_manager

# Run linting
flake8 amazon_q_rule_manager

# Run type checking
mypy amazon_q_rule_manager

# Format code
black amazon_q_rule_manager
```

## Building the Package

1. **Clean previous builds:**
   ```bash
   make clean
   ```

2. **Build the package:**
   ```bash
   make build
   # or manually:
   python -m build
   ```

This creates both wheel and source distributions in the `dist/` directory.

## Publishing to PyPI

### Test PyPI (Recommended First)

1. **Install twine:**
   ```bash
   pip install twine
   ```

2. **Upload to Test PyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   ```

3. **Test installation from Test PyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ amazon-q-rule-manager
   ```

### Production PyPI

1. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

2. **Verify installation:**
   ```bash
   pip install amazon-q-rule-manager
   ```

## GitHub Actions CI/CD

The repository includes GitHub Actions workflows for:

- **Continuous Integration:** Runs tests, linting, and type checking on Python 3.12 and 3.13
- **Automated Publishing:** Publishes to PyPI when a release is created

### Setting up PyPI Token

1. Go to PyPI → Account Settings → API Tokens
2. Create a new token with scope for this project
3. Add the token as `PYPI_API_TOKEN` in GitHub repository secrets

### Creating a Release

1. **Update version in `amazon_q_rule_manager/__init__.py`**
2. **Update CHANGELOG in README.md**
3. **Commit and push changes**
4. **Create a GitHub release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
5. **Create release on GitHub UI with release notes**

The GitHub Action will automatically build and publish to PyPI.

## Package Name Availability

The package name `amazon-q-rule-manager` should be checked for availability on PyPI:

```bash
pip search amazon-q-rule-manager
```

If not available, consider alternatives:
- `amazonq-rule-manager`
- `amazon-q-rules-manager`
- `aq-rule-manager`

## Configuration

### Environment Variables

- `AMAZONQ_RULES_URL`: Override default remote catalog URL
- `AMAZONQ_RULES_SOURCE`: Override default local source directory

### Directory Structure

The tool uses platform-specific directories:
- **Linux:** `~/.config/amazon-q-rule-manager/`
- **macOS:** `~/Library/Application Support/amazon-q-rule-manager/`
- **Windows:** `%APPDATA%\amazon-q-rule-manager\`

## Migration from Legacy Version

For users upgrading from the original script:

1. **Run migration script:**
   ```bash
   python migrate_to_new_version.py --register-workspaces --create-catalog
   ```

2. **Install new version:**
   ```bash
   pip install amazon-q-rule-manager
   ```

3. **Update catalog:**
   ```bash
   amazon-q-rule-manager catalog update
   ```

## Troubleshooting

### Common Issues

1. **Import errors:** Ensure all dependencies are installed
2. **Permission errors:** Check file permissions in config directories
3. **Network errors:** Verify internet connection for catalog updates

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export AMAZONQ_DEBUG=1
amazon-q-rule-manager catalog list
```

## Support

- **Issues:** [GitHub Issues](https://github.com/zerodaysec/amazonq-rules/issues)
- **Documentation:** [README.md](README.md)
- **Contributing:** See [Contributing Guidelines](README.md#contributing)
