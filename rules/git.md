---
inclusion: always
---

# Git Workflow

## Changelog Management

When making code changes, update the CHANGELOG file:

- Document all edits, fixes, features, and breaking changes
- If no version is specified, add entries under an "UNRELEASED" or "Unreleased" section
- Use clear, concise descriptions of what changed and why
- Follow existing changelog format conventions in the file

## Pre-commit Hooks

If pre-commit hooks are configured in the repository:

- Run pre-commit checks before committing code
- Address all issues flagged by pre-commit hooks
- Do not bypass or skip pre-commit checks unless explicitly instructed
