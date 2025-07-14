#!/usr/bin/env python3
"""
Script to sync catalog and rules data to frontend public directory.
This ensures the frontend always has the latest data.
"""

import os
import shutil
import json
from pathlib import Path

def sync_frontend_data():
    """Sync catalog and rules data to frontend public directory."""
    
    # Define paths
    project_root = Path(__file__).parent.parent
    catalog_source = project_root / "amazon_q_rule_manager" / "data" / "rules_catalog.json"
    rules_source = project_root / "rules"
    
    frontend_public = project_root / "frontend" / "public"
    catalog_dest = frontend_public / "rules_catalog.json"
    rules_dest = frontend_public / "rules"
    
    # Ensure frontend public directory exists
    frontend_public.mkdir(parents=True, exist_ok=True)
    
    # Copy catalog file
    if catalog_source.exists():
        print(f"Copying catalog: {catalog_source} -> {catalog_dest}")
        shutil.copy2(catalog_source, catalog_dest)
        
        # Verify the JSON is valid
        try:
            with open(catalog_dest, 'r') as f:
                json.load(f)
            print("✓ Catalog JSON is valid")
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in catalog: {e}")
            return False
    else:
        print(f"✗ Catalog source not found: {catalog_source}")
        return False
    
    # Copy rules directory
    if rules_source.exists() and rules_source.is_dir():
        print(f"Copying rules: {rules_source} -> {rules_dest}")
        
        # Remove existing rules directory and recreate
        if rules_dest.exists():
            shutil.rmtree(rules_dest)
        
        shutil.copytree(rules_source, rules_dest)
        
        # Count copied files
        rule_files = list(rules_dest.glob("*.md"))
        print(f"✓ Copied {len(rule_files)} rule files")
    else:
        print(f"✗ Rules source not found: {rules_source}")
        return False
    
    print("✓ Frontend data sync completed successfully")
    return True

if __name__ == "__main__":
    success = sync_frontend_data()
    exit(0 if success else 1)
