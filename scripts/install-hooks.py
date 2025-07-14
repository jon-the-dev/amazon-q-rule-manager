#!/usr/bin/env python3
"""
Install Git hooks for the Amazon Q Rule Manager project.
"""

import os
import stat
from pathlib import Path

def install_pre_commit_hook():
    """Install pre-commit hook to sync frontend data."""
    
    project_root = Path(__file__).parent.parent
    hooks_dir = project_root / ".git" / "hooks"
    hook_file = hooks_dir / "pre-commit"
    
    # Ensure hooks directory exists
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    hook_content = r'''#!/bin/bash
# Pre-commit hook to update catalog and sync frontend data when rules change

# Check if rules have changed
if git diff --cached --name-only | grep -E "rules/.*\.md"; then
    echo "📋 Rules changed, updating catalog..."
    
    # Update the catalog
    python3 update_json.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Catalog updated successfully"
        # Add the updated catalog to the commit
        git add amazon_q_rule_manager/data/rules_catalog.json
    else
        echo "✗ Failed to update catalog"
        exit 1
    fi
fi

# Check if catalog or rules have changed (including the newly updated catalog)
if git diff --cached --name-only | grep -E "(amazon_q_rule_manager/data/rules_catalog.json|rules/.*\.md)"; then
    echo "🔄 Syncing frontend data..."
    
    # Run the sync script
    python3 scripts/sync-frontend-data.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Frontend data synced successfully"
        # Add the updated frontend files to the commit
        git add frontend/public/rules_catalog.json frontend/public/rules/
    else
        echo "✗ Failed to sync frontend data"
        exit 1
    fi
fi
'''
    
    # Write the hook
    with open(hook_file, 'w') as f:
        f.write(hook_content)
    
    # Make it executable
    hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
    
    print(f"✓ Pre-commit hook installed at {hook_file}")

if __name__ == "__main__":
    install_pre_commit_hook()
