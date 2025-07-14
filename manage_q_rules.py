#!/usr/bin/env python3
"""
Amazon Q Rules Manager

This script manages Amazon Q rules files for projects by providing functionality to:
- Install rules from a remote repository or local directory to a project's .amazonq/rules directory
- Update source rules with local modifications
- Uninstall rules from a project
- Show installable rules with details

Usage:
    python manage_rules.py install <rule_name> <project_dir>
    python manage_rules.py update <rule_name> <project_dir>
    python manage_rules.py uninstall <rule_name> <project_dir>
    python manage_rules.py list [<project_dir>]
    python manage_rules.py show-installable
"""

import argparse
import os
import shutil
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import threading
from urllib.request import urlopen
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Default rules JSON URL can be overridden by AMAZONQ_RULES_URL env var
DEFAULT_RULES_URL = os.environ.get(
    "AMAZONQ_RULES_URL", "https://raw.githubusercontent.com/zerodaysec/amazonq-rules/refs/heads/main/rules.json"
)

# Default local source directory can be overridden by AMAZONQ_RULES_SOURCE env var
DEFAULT_SOURCE_DIR = os.environ.get(
    "AMAZONQ_RULES_SOURCE", "/Users/jon/code/amazonq-rules/rules"
)


def setup_argparser() -> argparse.ArgumentParser:
    """Set up and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Manage Amazon Q rules files for projects"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Install command
    install_parser = subparsers.add_parser(
        "install", help="Install a rule to a project"
    )
    install_parser.add_argument(
        "rule_name", help="Name of the rule to install (without .md extension)"
    )
    install_parser.add_argument("project_dir", help="Path to the project directory")

    # Update command
    update_parser = subparsers.add_parser(
        "update", help="Update source rule with local modifications"
    )
    update_parser.add_argument(
        "rule_name", help="Name of the rule to update (without .md extension)"
    )
    update_parser.add_argument(
        "project_dir", help="Path to the project directory containing the modified rule"
    )

    # Uninstall command
    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Remove a rule from a project"
    )
    uninstall_parser.add_argument(
        "rule_name", help="Name of the rule to uninstall (without .md extension)"
    )
    uninstall_parser.add_argument("project_dir", help="Path to the project directory")

    # List command
    list_parser = subparsers.add_parser("list", help="List available rules")
    list_parser.add_argument(
        "project_dir",
        nargs="?",
        help="Optional: Path to project to list installed rules",
        default=".",
    )

    # Show-installable command
    subparsers.add_parser(
        "show-installable", help="Show detailed information about available rules"
    )

    return parser


def ensure_directory_exists(directory: Path) -> None:
    """Ensure that the specified directory exists."""
    if not directory.exists():
        directory.mkdir(parents=True)
        print(f"Created directory: {directory}")


def get_rules_path(project_dir: str) -> Path:
    """Get the path to the .amazonq/rules directory in the project."""
    project_path = Path(project_dir).expanduser().resolve()
    return project_path / ".amazonq" / "rules"


def get_rules_json() -> Dict:
    """Fetch and return the rules JSON from the remote URL or local file."""
    try:
        # Try to fetch from URL first
        with urlopen(DEFAULT_RULES_URL) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Warning: Could not fetch rules from URL: {e}")
        print("Falling back to local source directory...")
        
        # Fall back to local source directory
        local_json_path = Path(DEFAULT_SOURCE_DIR).parent / "rules.json"
        if local_json_path.exists():
            with open(local_json_path, 'r') as f:
                return json.loads(f.read())
        else:
            print(f"Warning: Local rules.json not found at {local_json_path}")
            return {"rules": {}}


def get_source_rules_path() -> Path:
    """Get the path to the source rules directory."""
    return Path(DEFAULT_SOURCE_DIR).expanduser().resolve()


def get_rule_content(rule_name: str) -> Optional[str]:
    """Get the content of a rule from the remote URL or local file."""
    rules_json = get_rules_json()
    
    if "rules" not in rules_json or rule_name not in rules_json["rules"]:
        # Rule not found in JSON, try local file
        local_path = get_source_rules_path() / f"{rule_name}.md"
        if local_path.exists():
            with open(local_path, 'r') as f:
                return f.read()
        return None
    
    rule_info = rules_json["rules"][rule_name]
    
    if "url" in rule_info:
        try:
            with urlopen(rule_info["url"]) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching rule from URL: {e}")
    
    if "content" in rule_info:
        return rule_info["content"]
    
    return None


def list_rules(source_dir: Path, project_dir: Optional[str] = None) -> None:
    """List available rules from the JSON source and optionally in a project."""
    print("Available rules:")
    
    # Get rules from JSON
    rules_json = get_rules_json()
    remote_rules = []
    
    if "rules" in rules_json:
        remote_rules = list(rules_json["rules"].keys())
    
    # Get rules from local directory
    local_rules = []
    if source_dir.exists():
        local_rules = [f.stem for f in source_dir.glob("*.md")]
    
    # Combine and deduplicate rules
    all_rules = sorted(set(remote_rules + local_rules))
    
    if all_rules:
        for rule in all_rules:
            source = []
            if rule in remote_rules:
                source.append("remote")
            if rule in local_rules:
                source.append("local")
            print(f"  - {rule} ({', '.join(source)})")
    else:
        print("  No rules found")

    if project_dir:
        project_rules_dir = get_rules_path(project_dir)
        print(f"\nInstalled rules in project {project_dir}:")
        if project_rules_dir.exists():
            rules = [f.stem for f in project_rules_dir.glob("*.md")]
            if rules:
                for rule in sorted(rules):
                    print(f"  - {rule}")
            else:
                print("  No rules installed")
        else:
            print(f"  Rules directory {project_rules_dir} does not exist")


def show_installable_rules() -> None:
    """Show detailed information about available rules for installation."""
    # Get rules from JSON
    rules_json = get_rules_json()
    remote_rules = {}
    
    if "rules" in rules_json:
        remote_rules = rules_json["rules"]
    
    # Get rules from local directory
    source_dir = get_source_rules_path()
    local_rule_files = []
    if source_dir.exists():
        local_rule_files = list(source_dir.glob("*.md"))
    
    # Combine rules
    all_rules = set(remote_rules.keys()).union({f.stem for f in local_rule_files})
    
    if not all_rules:
        print("No rules available for installation")
        return

    print("Available rules for installation:\n")

    # Process remote rules from JSON
    for rule_name in sorted(all_rules):
        print(f"=== {rule_name} ===")
        
        content = get_rule_content(rule_name)
        if content:
            # Print first 3 lines as a preview
            lines = content.strip().split("\n")
            preview = "\n".join(lines[:3])
            if len(lines) > 3:
                preview += "\n..."
            
            print(f"{preview}\n")
        else:
            print("Error: Could not retrieve rule content\n")

    print(
        "To install a rule, use: python manage_rules.py install <rule_name> <project_dir>"
    )


def install_rule(rule_name: str, project_dir: str) -> None:
    """Install a rule from the remote JSON or local source directory to a project."""
    # Get rule content
    content = get_rule_content(rule_name)
    
    if not content:
        print(f"Error: Rule '{rule_name}' not found in remote or local sources")
        return

    project_rules_dir = get_rules_path(project_dir)
    ensure_directory_exists(project_rules_dir)

    target_file = project_rules_dir / f"{rule_name}.md"

    try:
        with open(target_file, 'w') as f:
            f.write(content)
        print(f"Successfully installed rule '{rule_name}' to {project_dir}")
    except Exception as e:
        print(f"Error installing rule: {e}")


def update_rule(rule_name: str, project_dir: str) -> None:
    """Update a local source rule with the version from a project."""
    project_rules_dir = get_rules_path(project_dir)
    project_file = project_rules_dir / f"{rule_name}.md"

    if not project_file.exists():
        print(f"Error: Rule '{rule_name}' not found in project {project_dir}")
        return

    source_dir = get_source_rules_path()
    ensure_directory_exists(source_dir)

    target_file = source_dir / f"{rule_name}.md"

    try:
        shutil.copy2(project_file, target_file)
        print(f"Successfully updated local source rule '{rule_name}' from {project_dir}")
        print(f"Note: This only updates your local copy. To contribute this change to the remote repository,")
        print(f"you'll need to submit a pull request with your changes.")
    except Exception as e:
        print(f"Error updating rule: {e}")


def uninstall_rule(rule_name: str, project_dir: str) -> None:
    """Remove a rule from a project."""
    project_rules_dir = get_rules_path(project_dir)
    rule_file = project_rules_dir / f"{rule_name}.md"

    if not rule_file.exists():
        print(f"Error: Rule '{rule_name}' not found in project {project_dir}")
        return

    try:
        rule_file.unlink()
        print(f"Successfully uninstalled rule '{rule_name}' from {project_dir}")

        # Check if rules directory is empty and remove if it is
        if not any(project_rules_dir.iterdir()):
            project_rules_dir.rmdir()
            print(f"Removed empty rules directory: {project_rules_dir}")

            # Check if .amazonq directory is empty and remove if it is
            amazonq_dir = project_rules_dir.parent
            if amazonq_dir.exists() and not any(amazonq_dir.iterdir()):
                amazonq_dir.rmdir()
                print(f"Removed empty .amazonq directory: {amazonq_dir}")
    except Exception as e:
        print(f"Error uninstalling rule: {e}")


def main() -> None:
    """Main function to parse arguments and execute commands."""
    parser = setup_argparser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    source_dir = get_source_rules_path()

    if args.command == "list":
        list_rules(source_dir, args.project_dir)
    elif args.command == "install":
        install_rule(args.rule_name, args.project_dir)
    elif args.command == "update":
        update_rule(args.rule_name, args.project_dir)
    elif args.command == "uninstall":
        uninstall_rule(args.rule_name, args.project_dir)
    elif args.command == "show-installable":
        show_installable_rules()


if __name__ == "__main__":
    main()
