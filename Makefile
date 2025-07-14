.PHONY: help install install-dev test lint format type-check build clean publish-test publish

help:
	@echo "Available commands:"
	@echo "  install      Install package in development mode"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black"
	@echo "  type-check   Run type checking with mypy"
	@echo "  build        Build package for distribution"
	@echo "  clean        Clean build artifacts"
	@echo "  publish-test Publish to Test PyPI"
	@echo "  publish      Publish to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest --cov=amazon_q_rule_manager --cov-report=term-missing --cov-report=html

lint:
	flake8 amazon_q_rule_manager
	black --check amazon_q_rule_manager

format:
	black amazon_q_rule_manager

type-check:
	mypy amazon_q_rule_manager

build: clean
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish-test: build
	twine upload --repository testpypi dist/*

publish: build
	twine upload dist/*

pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

# Legacy rule update (deprecated)
update-rules:
	@echo "This command is deprecated. Use 'amazon-q-rule-manager catalog update' instead."
