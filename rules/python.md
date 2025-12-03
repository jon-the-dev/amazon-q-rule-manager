---
inclusion: fileMatch
fileMatchPattern: ['**/*.py', '**/Pipfile', '**/pyproject.toml', '**/requirements.txt']
---

# Python Development Guidelines

## Dependency Management

- Use pipenv for dependency management (preferred over poetry)
- Create Pipfile and Pipfile.lock for reproducible environments
- Avoid using bare requirements.txt unless necessary for compatibility

## Command-Line Interface

- Use argparse for CLI argument parsing
- Include comprehensive help text with --help flag
- Provide clear descriptions for all arguments and subcommands
- Use argument groups to organize related options

## Logging

- Use Python's logging module (not print statements for application output)
- Set up proper log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include a --log-file flag to optionally write logs to a file
- Use appropriate formatters with timestamps and log levels

## Configuration Management

- Store configuration in .env files using python-dotenv
- Never hardcode sensitive values (API keys, passwords, database URLs)
- Use .env for default values, allow CLI arguments to override when appropriate
- Add .env to .gitignore and provide .env.example as a template

## Code Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Write docstrings for modules, classes, and functions

## Other Notes

- Use threading for parallel operations when it makes sense
- Always code for python >=3.12
- When generating output filenames include account ids or other key info
- Refactor files once they are larger then 400 lines
