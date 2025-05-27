#!/usr/bin/env python3
"""
Amazon Q Rules Manager

This script manages Amazon Q rules files for projects by providing functionality to:
- Install rules from a source directory to a project's .amazonq/rules directory
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
from pathlib import Path
from typing import List, Optional
import threading
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Default source directory can be overridden by AMAZONQ_RULES_SOURCE env var
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


def get_source_rules_path() -> Path:
    """Get the path to the source rules directory."""
    return Path(DEFAULT_SOURCE_DIR).expanduser().resolve()


def list_rules(source_dir: Path, project_dir: Optional[str] = None) -> None:
    """List available rules in the source directory and optionally in a project."""
    print("Available rules in source directory:")
    if source_dir.exists():
        rules = [f.stem for f in source_dir.glob("*.md")]
        if rules:
            for rule in sorted(rules):
                print(f"  - {rule}")
        else:
            print("  No rules found")
    else:
        print(f"  Source directory {source_dir} does not exist")

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
    source_dir = get_source_rules_path()

    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return

    rules = list(source_dir.glob("*.md"))

    if not rules:
        print("No rules available for installation")
        return

    print(f"Available rules for installation from {source_dir}:\n")

    for rule_file in sorted(rules):
        rule_name = rule_file.stem
        print(f"=== {rule_name} ===")

        try:
            with open(rule_file, "r") as f:
                content = f.read().strip()

            # Print first 3 lines as a preview
            lines = content.split("\n")
            preview = "\n".join(lines[:3])
            if len(lines) > 3:
                preview += "\n..."

            print(f"{preview}\n")
        except Exception as e:
            print(f"Error reading rule file: {e}\n")

    print(
        "To install a rule, use: python manage_rules.py install <rule_name> <project_dir>"
    )


def install_rule(rule_name: str, project_dir: str) -> None:
    """Install a rule from the source directory to a project."""
    source_dir = get_source_rules_path()
    source_file = source_dir / f"{rule_name}.md"

    if not source_file.exists():
        print(f"Error: Rule '{rule_name}' not found in {source_dir}")
        return

    project_rules_dir = get_rules_path(project_dir)
    ensure_directory_exists(project_rules_dir)

    target_file = project_rules_dir / f"{rule_name}.md"

    try:
        shutil.copy2(source_file, target_file)
        print(f"Successfully installed rule '{rule_name}' to {project_dir}")
    except Exception as e:
        print(f"Error installing rule: {e}")


def update_rule(rule_name: str, project_dir: str) -> None:
    """Update a source rule with the version from a project."""
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
        print(f"Successfully updated source rule '{rule_name}' from {project_dir}")
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
