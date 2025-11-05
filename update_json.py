#!/usr/bin/env python3
"""
Script to generate a comprehensive rules catalog JSON file for the Amazon Q Rule Manager.
This script scans the ./rules directory and creates a rich catalog with metadata,
categories, and tags that can be used by the Python package and frontend.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime, timezone
import re


def extract_rule_metadata(rule_path: Path) -> Dict:
    """
    Extract metadata from a rule file by analyzing its content.

    Args:
        rule_path: Path to the rule markdown file

    Returns:
        Dictionary containing rule metadata
    """
    rule_name = rule_path.stem

    # Default metadata
    metadata = {
        "name": rule_name,
        "title": rule_name.replace("-", " ").replace("_", " ").title(),
        "description": f"Guidelines and best practices for {rule_name}",
        "category": "general",
        "version": "1.0.0",
        "author": "Amazon Q Rules Team",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tags": [rule_name],
        "dependencies": [],
        "conflicts": [],
        "supported_languages": [],
        "examples": [],
        "documentation_url": None,
        "source_url": f"https://github.com/zerodaysec/amazonq-rules/blob/main/rules/{rule_path.name}",
    }

    # Try to read the file content for better metadata
    try:
        content = rule_path.read_text(encoding="utf-8")

        # Extract examples from content
        examples = []
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and len(line) > 10:
                examples.append(line)
        metadata["examples"] = examples[:3]  # Limit to 3 examples

        # Set category based on rule name
        if rule_name in ["aws", "sls-framework", "aws-sam"]:
            metadata["category"] = "aws"
            metadata["tags"].extend(["aws", "cloud"])
            metadata["supported_languages"] = ["yaml", "json", "terraform"]
            if rule_name == "aws":
                metadata["title"] = "AWS Best Practices"
                metadata["description"] = (
                    "Guidelines for AWS resources including alarms, tagging, and default values"
                )
                metadata["tags"].extend(["monitoring", "tagging", "alarms"])
                metadata["aws_services"] = ["CloudWatch", "SNS", "EC2", "S3", "Lambda"]
                metadata["documentation_url"] = "https://docs.aws.amazon.com/wellarchitected/"
            elif rule_name == "sls-framework":
                metadata["title"] = "Serverless Framework Guidelines"
                metadata["description"] = (
                    "Guidelines for Serverless Framework development and deployment"
                )
                metadata["category"] = "serverless"
                metadata["tags"] = ["serverless", "aws", "lambda", "deployment"]
                metadata["dependencies"] = ["aws"]
                metadata["aws_services"] = ["Lambda", "API Gateway", "CloudFormation", "S3"]
                metadata["documentation_url"] = "https://www.serverless.com/framework/docs/"

        elif rule_name == "python":
            metadata["category"] = "python"
            metadata["title"] = "Python Development Standards"
            metadata["description"] = (
                "Standards for Python development including version requirements and coding practices"
            )
            metadata["tags"] = ["python", "development", "standards", "threading", "argparse"]
            metadata["min_python_version"] = "3.12"
            metadata["supported_languages"] = ["python"]
            metadata["documentation_url"] = "https://docs.python.org/3/"

        elif rule_name == "terraform":
            metadata["category"] = "terraform"
            metadata["title"] = "Terraform Best Practices"
            metadata["description"] = (
                "Best practices for Terraform including version requirements and security principles"
            )
            metadata["tags"] = ["terraform", "infrastructure", "iac", "security", "versioning"]
            metadata["supported_languages"] = ["hcl", "terraform"]
            metadata["terraform_providers"] = ["aws", "azurerm", "google"]
            metadata["documentation_url"] = "https://developer.hashicorp.com/terraform/docs"

        elif rule_name == "react":
            metadata["category"] = "javascript"
            metadata["title"] = "React Development Guidelines"
            metadata["description"] = (
                "Guidelines for React development including component structure and best practices"
            )
            metadata["tags"] = ["react", "javascript", "frontend", "components", "hooks"]
            metadata["supported_languages"] = ["javascript", "typescript", "jsx", "tsx"]
            metadata["documentation_url"] = "https://react.dev/"

        elif rule_name == "ruby":
            metadata["category"] = "ruby"
            metadata["title"] = "Ruby Development Standards"
            metadata["description"] = (
                "Standards for Ruby development including style guide and best practices"
            )
            metadata["tags"] = ["ruby", "development", "style", "conventions"]
            metadata["supported_languages"] = ["ruby"]
            metadata["documentation_url"] = "https://ruby-doc.org/"

        elif rule_name == "runway":
            metadata["category"] = "aws"
            metadata["title"] = "Runway Deployment Guidelines"
            metadata["description"] = "Guidelines for using Runway for infrastructure deployment"
            metadata["tags"] = ["runway", "deployment", "infrastructure", "aws"]
            metadata["supported_languages"] = ["yaml", "python"]

    except Exception as e:
        print(f"Warning: Could not read content from {rule_path}: {e}")

    return metadata


def build_categories_and_tags(rules: Dict) -> tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Build categories and tags mappings from rules.

    Args:
        rules: Dictionary of rule metadata

    Returns:
        Tuple of (categories, tags) dictionaries
    """
    categories = {}
    tags = {}

    for rule_name, rule_data in rules.items():
        category = rule_data.get("category", "general")
        rule_tags = rule_data.get("tags", [])

        # Add to categories
        if category not in categories:
            categories[category] = []
        categories[category].append(rule_name)

        # Add to tags
        for tag in rule_tags:
            if tag not in tags:
                tags[tag] = []
            if rule_name not in tags[tag]:
                tags[tag].append(rule_name)

    return categories, tags


def get_rules_catalog(rules_dir: str = "./rules") -> Dict:
    """
    Scan the rules directory and create a comprehensive rules catalog.

    Args:
        rules_dir: Path to the directory containing rule files

    Returns:
        Dictionary containing the complete rules catalog
    """
    rules = {}

    # Ensure the rules directory exists
    rules_path = Path(rules_dir)
    if not rules_path.exists() or not rules_path.is_dir():
        print(f"Rules directory not found: {rules_dir}")
        return {
            "version": "2.0.0",
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rules": {},
            "categories": {},
            "tags": {},
        }

    # Scan for rule files
    for file_path in rules_path.iterdir():
        if file_path.is_file() and file_path.suffix == ".md":
            rule_name = file_path.stem
            rules[rule_name] = extract_rule_metadata(file_path)

    # Build categories and tags
    categories, tags = build_categories_and_tags(rules)

    # Create the complete catalog
    catalog = {
        "version": "2.0.0",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rules": rules,
        "categories": categories,
        "tags": tags,
    }

    return catalog


def save_rules_catalog(catalog: Dict, output_file: str) -> None:
    """
    Save the rules catalog to a JSON file.

    Args:
        catalog: Complete rules catalog dictionary
        output_file: Path to the output JSON file
    """
    # Ensure the output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"Rules catalog saved to {output_file}")


def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description="Generate a comprehensive rules catalog JSON file for Amazon Q Rule Manager."
    )
    parser.add_argument(
        "--rules-dir",
        default="./rules",
        help="Directory containing rule files (default: ./rules)",
    )
    parser.add_argument(
        "--output",
        default="amazon_q_rule_manager/data/rules_catalog.json",
        help="Output JSON file path (default: amazon_q_rule_manager/data/rules_catalog.json)",
    )

    args = parser.parse_args()

    # Get rules catalog
    catalog = get_rules_catalog(args.rules_dir)

    if not catalog["rules"]:
        print("No rules found.")
        return

    # Save catalog to JSON file
    save_rules_catalog(catalog, args.output)
    print(f"Found {len(catalog['rules'])} rules: {', '.join(catalog['rules'].keys())}")
    print(f"Categories: {', '.join(catalog['categories'].keys())}")
    print(f"Tags: {len(catalog['tags'])} unique tags")


if __name__ == "__main__":
    main()
