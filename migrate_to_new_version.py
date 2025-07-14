#!/usr/bin/env python3
"""Migration script for existing users to upgrade to the new version."""

import argparse
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any

from amazon_q_rule_manager.core import RuleManager
from amazon_q_rule_manager.models import RuleMetadata, RuleCategory


def find_existing_rule_directories() -> List[Path]:
    """Find existing .amazonq/rules directories in the current directory tree."""
    current_dir = Path.cwd()
    rule_dirs = []
    
    # Search for .amazonq/rules directories
    for amazonq_dir in current_dir.rglob(".amazonq"):
        rules_dir = amazonq_dir / "rules"
        if rules_dir.exists() and rules_dir.is_dir():
            rule_dirs.append(rules_dir.parent.parent)  # Project root
    
    return rule_dirs


def migrate_project_rules(project_path: Path, manager: RuleManager, 
                         register_workspace: bool = True) -> None:
    """Migrate rules from a project to the new system."""
    print(f"Migrating rules from: {project_path}")
    
    rules_dir = project_path / ".amazonq" / "rules"
    if not rules_dir.exists():
        print(f"  No rules directory found in {project_path}")
        return
    
    # Register workspace if requested
    workspace_name = project_path.name
    if register_workspace:
        try:
            manager.register_workspace(project_path, workspace_name)
            print(f"  Registered workspace: {workspace_name}")
        except Exception as e:
            print(f"  Warning: Could not register workspace: {e}")
    
    # List existing rules
    rule_files = list(rules_dir.glob("*.md"))
    if not rule_files:
        print(f"  No rule files found in {project_path}")
        return
    
    print(f"  Found {len(rule_files)} rule files:")
    for rule_file in rule_files:
        print(f"    - {rule_file.stem}")
    
    print(f"  Rules are already in the correct location for workspace '{workspace_name}'")


def create_enhanced_catalog() -> Dict[str, Any]:
    """Create an enhanced catalog from existing rules."""
    rules_dir = Path("rules")
    if not rules_dir.exists():
        print("No local rules directory found")
        return {}
    
    catalog = {
        "version": "2.0.0",
        "last_updated": "2024-07-14T05:00:00Z",
        "rules": {},
        "categories": {},
        "tags": {}
    }
    
    # Map rule names to categories (you may need to adjust these)
    rule_categories = {
        "aws": RuleCategory.AWS,
        "python": RuleCategory.PYTHON,
        "terraform": RuleCategory.TERRAFORM,
        "react": RuleCategory.JAVASCRIPT,
        "ruby": RuleCategory.RUBY,
        "sls-framework": RuleCategory.SERVERLESS,
    }
    
    for rule_file in rules_dir.glob("*.md"):
        rule_name = rule_file.stem
        content = rule_file.read_text()
        
        # Create basic metadata
        category = rule_categories.get(rule_name, RuleCategory.GENERAL)
        
        metadata = {
            "name": rule_name,
            "title": rule_name.replace("-", " ").title(),
            "description": f"Rules for {rule_name}",
            "category": category,
            "version": "1.0.0",
            "tags": [rule_name],
            "dependencies": [],
            "conflicts": [],
            "supported_languages": [],
            "examples": content.split('\n')[:3] if content else [],
        }
        
        catalog["rules"][rule_name] = metadata
        
        # Update categories and tags
        if category not in catalog["categories"]:
            catalog["categories"][category] = []
        catalog["categories"][category].append(rule_name)
        
        for tag in metadata["tags"]:
            if tag not in catalog["tags"]:
                catalog["tags"][tag] = []
            catalog["tags"][tag].append(rule_name)
    
    return catalog


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate to Amazon Q Rule Manager v2.0")
    parser.add_argument("--register-workspaces", action="store_true",
                       help="Automatically register found projects as workspaces")
    parser.add_argument("--create-catalog", action="store_true",
                       help="Create enhanced catalog from existing rules")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    print("Amazon Q Rule Manager Migration Tool")
    print("=" * 40)
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()
    
    # Initialize rule manager
    try:
        manager = RuleManager()
        print("✓ Rule manager initialized")
    except Exception as e:
        print(f"✗ Failed to initialize rule manager: {e}")
        return
    
    # Find existing rule directories
    print("\nSearching for existing rule directories...")
    project_dirs = find_existing_rule_directories()
    
    if not project_dirs:
        print("No existing .amazonq/rules directories found")
    else:
        print(f"Found {len(project_dirs)} projects with rules:")
        for project_dir in project_dirs:
            print(f"  - {project_dir}")
        
        if args.register_workspaces and not args.dry_run:
            print("\nMigrating projects...")
            for project_dir in project_dirs:
                migrate_project_rules(project_dir, manager, register_workspace=True)
    
    # Create enhanced catalog
    if args.create_catalog:
        print("\nCreating enhanced catalog...")
        catalog = create_enhanced_catalog()
        
        if catalog and not args.dry_run:
            catalog_file = Path("amazon_q_rule_manager/data/rules_catalog.json")
            catalog_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(catalog_file, 'w') as f:
                json.dump(catalog, f, indent=2)
            
            print(f"✓ Enhanced catalog created: {catalog_file}")
        elif catalog:
            print(f"✓ Would create enhanced catalog with {len(catalog['rules'])} rules")
    
    print("\nMigration complete!")
    print("\nNext steps:")
    print("1. Install the new package: pip install -e .")
    print("2. Update catalog: amazon-q-rule-manager catalog update")
    print("3. List workspaces: amazon-q-rule-manager workspace list")
    print("4. Explore new features: amazon-q-rule-manager --help")


if __name__ == "__main__":
    main()
