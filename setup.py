#!/usr/bin/env python3
"""Setup script for amazon-q-rule-manager package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read version from __init__.py
def get_version():
    """Get version from __init__.py file."""
    init_file = this_directory / "amazon_q_rule_manager" / "__init__.py"
    with open(init_file) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="amazon-q-rule-manager",
    version=get_version(),
    author="Amazon Q Rules Team",
    author_email="support@example.com",
    description="A robust manager for Amazon Q Developer rules with global and workspace support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zerodaysec/amazonq-rules",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "appdirs>=1.4.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "amazon-q-rule-manager=amazon_q_rule_manager.cli:main",
            "aqrm=amazon_q_rule_manager.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "amazon_q_rule_manager": ["data/*.json", "templates/*.md"],
    },
    keywords="amazon-q developer rules code-quality aws terraform python",
    project_urls={
        "Bug Reports": "https://github.com/zerodaysec/amazonq-rules/issues",
        "Source": "https://github.com/zerodaysec/amazonq-rules",
        "Documentation": "https://github.com/zerodaysec/amazonq-rules/blob/main/README.md",
    },
)
