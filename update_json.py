#!/usr/bin/env python3
"""
Script to generate a JSON file containing available Amazon Q rules.
This script scans the ./rules directory and creates a dictionary of available rules
and their filenames, which can be used by client applications.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List


def get_rules(rules_dir: str = "./rules") -> Dict[str, str]:
    """
    Scan the rules directory and create a dictionary of available rules.

    Args:
        rules_dir: Path to the directory containing rule files

    Returns:
        Dictionary with rule names as keys and filenames as values
    """
    rules = {}

    # Ensure the rules directory exists
    rules_path = Path(rules_dir)
    if not rules_path.exists() or not rules_path.is_dir():
        print(f"Rules directory not found: {rules_dir}")
        return rules

    # Scan for rule files
    for file_path in rules_path.iterdir():
        if file_path.is_file():
            # Use the filename without extension as the rule name
            rule_name = file_path.stem
            rules[rule_name] = file_path.name

    return rules


def save_rules_json(rules: Dict[str, str], output_file: str = "rules.json") -> None:
    """
    Save the rules dictionary to a JSON file.

    Args:
        rules: Dictionary of rules to save
        output_file: Path to the output JSON file
    """
    with open(output_file, "w") as f:
        json.dump({"rules": rules}, f, indent=2)

    print(f"Rules saved to {output_file}")


def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description="Generate a JSON file containing available Amazon Q rules."
    )
    parser.add_argument(
        "--rules-dir",
        default="./rules",
        help="Directory containing rule files (default: ./rules)",
    )
    parser.add_argument(
        "--output",
        default="rules.json",
        help="Output JSON file path (default: rules.json)",
    )

    args = parser.parse_args()

    # Get available rules
    rules = get_rules(args.rules_dir)

    if not rules:
        print("No rules found.")
        return

    # Save rules to JSON file
    save_rules_json(rules, args.output)
    print(f"Found {len(rules)} rules: {', '.join(rules.keys())}")


if __name__ == "__main__":
    main()
