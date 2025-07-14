"""Core rule manager functionality."""

import hashlib
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from urllib.request import urlopen
import requests
import appdirs

from .models import (
    GlobalConfig,
    Rule,
    RuleCatalog,
    RuleMetadata,
    RuleSource,
    WorkspaceConfig,
)


class RuleManagerError(Exception):
    """Base exception for rule manager errors."""
    pass


class RuleNotFoundError(RuleManagerError):
    """Raised when a rule is not found."""
    pass


class WorkspaceNotFoundError(RuleManagerError):
    """Raised when a workspace is not found."""
    pass


class RuleConflictError(RuleManagerError):
    """Raised when there are rule conflicts."""
    pass


class RuleManager:
    """Robust manager for Amazon Q Developer rules."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the rule manager.
        
        Args:
            config_dir: Optional custom configuration directory
        """
        # Set up directories
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path(appdirs.user_config_dir("amazon-q-rule-manager"))
        
        self.cache_dir = Path(appdirs.user_cache_dir("amazon-q-rule-manager"))
        self.global_rules_dir = self.config_dir / "global_rules"
        
        # Ensure directories exist
        for directory in [self.config_dir, self.cache_dir, self.global_rules_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration
        self.config_file = self.config_dir / "config.json"
        self.catalog_file = self.cache_dir / "catalog.json"
        
        self._load_config()
        self._load_catalog()

    def _load_config(self) -> None:
        """Load global configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                self.config = GlobalConfig(**config_data)
        else:
            # Create default configuration
            self.config = GlobalConfig(
                default_remote_url="https://raw.githubusercontent.com/zerodaysec/amazonq-rules/main/amazon_q_rule_manager/data/rules_catalog.json",
                cache_directory=self.cache_dir,
                global_rules_directory=self.global_rules_dir,
            )
            self._save_config()

    def _save_config(self) -> None:
        """Save global configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config.dict(), f, indent=2, default=str)

    def _load_catalog(self) -> None:
        """Load rule catalog."""
        if self.catalog_file.exists():
            with open(self.catalog_file, 'r') as f:
                catalog_data = json.load(f)
                self.catalog = RuleCatalog(**catalog_data)
        else:
            # Try to fetch from remote
            try:
                self.update_catalog()
            except Exception:
                # Create empty catalog if remote fetch fails
                self.catalog = RuleCatalog()
                self._save_catalog()

    def _save_catalog(self) -> None:
        """Save rule catalog."""
        with open(self.catalog_file, 'w') as f:
            json.dump(self.catalog.dict(), f, indent=2, default=str)

    def update_catalog(self, force: bool = False) -> bool:
        """Update rule catalog from remote source.
        
        Args:
            force: Force update even if recently updated
            
        Returns:
            True if catalog was updated, False otherwise
        """
        # Check if update is needed
        if not force and self.config.last_update_check:
            time_since_update = datetime.now() - self.config.last_update_check
            if time_since_update.total_seconds() < self.config.auto_update_interval:
                return False

        try:
            response = requests.get(str(self.config.default_remote_url), timeout=30)
            response.raise_for_status()
            
            catalog_data = response.json()
            new_catalog = RuleCatalog(**catalog_data)
            
            # Update catalog if it's newer
            if new_catalog.last_updated > self.catalog.last_updated:
                self.catalog = new_catalog
                self._save_catalog()
                
                self.config.last_update_check = datetime.now()
                self._save_config()
                return True
                
        except Exception as e:
            raise RuleManagerError(f"Failed to update catalog: {e}")
        
        return False

    def list_available_rules(self, category: Optional[str] = None, 
                           tag: Optional[str] = None) -> List[RuleMetadata]:
        """List available rules with optional filtering.
        
        Args:
            category: Filter by category
            tag: Filter by tag
            
        Returns:
            List of rule metadata
        """
        if category:
            return self.catalog.get_rules_by_category(category)
        elif tag:
            return self.catalog.get_rules_by_tag(tag)
        else:
            return list(self.catalog.rules.values())

    def search_rules(self, query: str) -> List[RuleMetadata]:
        """Search rules by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching rule metadata
        """
        return self.catalog.search_rules(query)

    def get_rule_metadata(self, rule_name: str) -> RuleMetadata:
        """Get metadata for a specific rule.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            Rule metadata
            
        Raises:
            RuleNotFoundError: If rule is not found
        """
        if rule_name not in self.catalog.rules:
            raise RuleNotFoundError(f"Rule '{rule_name}' not found")
        
        return self.catalog.rules[rule_name]

    def get_rule_content(self, rule_name: str, source: RuleSource = RuleSource.REMOTE) -> str:
        """Get content for a specific rule.
        
        Args:
            rule_name: Name of the rule
            source: Source to get rule from
            
        Returns:
            Rule content
            
        Raises:
            RuleNotFoundError: If rule is not found
        """
        metadata = self.get_rule_metadata(rule_name)
        
        if source == RuleSource.GLOBAL:
            # Check global rules directory
            global_rule_path = self.global_rules_dir / f"{rule_name}.md"
            if global_rule_path.exists():
                return global_rule_path.read_text()
        
        elif source == RuleSource.LOCAL:
            # Check current directory rules
            local_rule_path = Path.cwd() / "rules" / f"{rule_name}.md"
            if local_rule_path.exists():
                return local_rule_path.read_text()
        
        # Try local rules directory first (for development/testing)
        local_rules_dir = Path(__file__).parent.parent / "rules"
        local_rule_file = local_rules_dir / f"{rule_name}.md"
        if local_rule_file.exists():
            return local_rule_file.read_text()
        
        # Fallback to remote
        if metadata.source_url:
            try:
                response = requests.get(str(metadata.source_url), timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                raise RuleManagerError(f"Failed to fetch rule content: {e}")
        
        raise RuleNotFoundError(f"Rule content for '{rule_name}' not found")

    def install_rule_globally(self, rule_name: str, force: bool = False) -> None:
        """Install a rule globally.
        
        Args:
            rule_name: Name of the rule to install
            force: Force installation even if rule exists
            
        Raises:
            RuleNotFoundError: If rule is not found
            RuleManagerError: If installation fails
        """
        metadata = self.get_rule_metadata(rule_name)
        content = self.get_rule_content(rule_name, RuleSource.REMOTE)
        
        global_rule_path = self.global_rules_dir / f"{rule_name}.md"
        
        if global_rule_path.exists() and not force:
            raise RuleManagerError(f"Rule '{rule_name}' already installed globally. Use --force to overwrite.")
        
        # Check dependencies
        self._check_dependencies(metadata.dependencies)
        
        # Check conflicts
        self._check_conflicts(metadata.conflicts, RuleSource.GLOBAL)
        
        # Install rule
        global_rule_path.write_text(content)
        
        print(f"Successfully installed rule '{rule_name}' globally")

    def uninstall_rule_globally(self, rule_name: str) -> None:
        """Uninstall a rule globally.
        
        Args:
            rule_name: Name of the rule to uninstall
            
        Raises:
            RuleNotFoundError: If rule is not found
        """
        global_rule_path = self.global_rules_dir / f"{rule_name}.md"
        
        if not global_rule_path.exists():
            raise RuleNotFoundError(f"Rule '{rule_name}' not installed globally")
        
        global_rule_path.unlink()
        print(f"Successfully uninstalled rule '{rule_name}' globally")

    def list_global_rules(self) -> List[str]:
        """List globally installed rules.
        
        Returns:
            List of globally installed rule names
        """
        return [f.stem for f in self.global_rules_dir.glob("*.md")]

    def register_workspace(self, workspace_path: Union[str, Path], 
                          name: Optional[str] = None) -> WorkspaceConfig:
        """Register a workspace.
        
        Args:
            workspace_path: Path to the workspace
            name: Optional workspace name
            
        Returns:
            Workspace configuration
        """
        workspace_path = Path(workspace_path).resolve()
        
        if not name:
            name = workspace_path.name
        
        workspace_config = WorkspaceConfig(
            name=name,
            path=workspace_path,
        )
        
        self.config.workspaces[name] = workspace_config
        self._save_config()
        
        return workspace_config

    def unregister_workspace(self, name: str) -> None:
        """Unregister a workspace.
        
        Args:
            name: Workspace name
            
        Raises:
            WorkspaceNotFoundError: If workspace is not found
        """
        if name not in self.config.workspaces:
            raise WorkspaceNotFoundError(f"Workspace '{name}' not found")
        
        del self.config.workspaces[name]
        self._save_config()

    def list_workspaces(self) -> List[WorkspaceConfig]:
        """List registered workspaces.
        
        Returns:
            List of workspace configurations
        """
        return list(self.config.workspaces.values())

    def install_rule_to_workspace(self, rule_name: str, workspace_name: str, 
                                 force: bool = False) -> None:
        """Install a rule to a workspace.
        
        Args:
            rule_name: Name of the rule to install
            workspace_name: Name of the workspace
            force: Force installation even if rule exists
            
        Raises:
            RuleNotFoundError: If rule is not found
            WorkspaceNotFoundError: If workspace is not found
            RuleManagerError: If installation fails
        """
        if workspace_name not in self.config.workspaces:
            raise WorkspaceNotFoundError(f"Workspace '{workspace_name}' not found")
        
        workspace = self.config.workspaces[workspace_name]
        metadata = self.get_rule_metadata(rule_name)
        content = self.get_rule_content(rule_name, RuleSource.REMOTE)
        
        # Ensure .amazonq/rules directory exists
        rules_dir = workspace.path / ".amazonq" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        rule_path = rules_dir / f"{rule_name}.md"
        
        if rule_path.exists() and not force:
            raise RuleManagerError(f"Rule '{rule_name}' already installed in workspace '{workspace_name}'. Use --force to overwrite.")
        
        # Check dependencies
        self._check_dependencies(metadata.dependencies)
        
        # Check conflicts
        self._check_conflicts(metadata.conflicts, RuleSource.WORKSPACE, workspace_name)
        
        # Install rule
        rule_path.write_text(content)
        
        # Update workspace configuration
        if rule_name not in workspace.installed_rules:
            workspace.installed_rules.append(rule_name)
            workspace.updated_at = datetime.now()
            self._save_config()
        
        print(f"Successfully installed rule '{rule_name}' to workspace '{workspace_name}'")

    def uninstall_rule_from_workspace(self, rule_name: str, workspace_name: str) -> None:
        """Uninstall a rule from a workspace.
        
        Args:
            rule_name: Name of the rule to uninstall
            workspace_name: Name of the workspace
            
        Raises:
            RuleNotFoundError: If rule is not found
            WorkspaceNotFoundError: If workspace is not found
        """
        if workspace_name not in self.config.workspaces:
            raise WorkspaceNotFoundError(f"Workspace '{workspace_name}' not found")
        
        workspace = self.config.workspaces[workspace_name]
        rules_dir = workspace.path / ".amazonq" / "rules"
        rule_path = rules_dir / f"{rule_name}.md"
        
        if not rule_path.exists():
            raise RuleNotFoundError(f"Rule '{rule_name}' not installed in workspace '{workspace_name}'")
        
        rule_path.unlink()
        
        # Update workspace configuration
        if rule_name in workspace.installed_rules:
            workspace.installed_rules.remove(rule_name)
            workspace.updated_at = datetime.now()
            self._save_config()
        
        # Clean up empty directories
        if not any(rules_dir.iterdir()):
            rules_dir.rmdir()
            amazonq_dir = rules_dir.parent
            if not any(amazonq_dir.iterdir()):
                amazonq_dir.rmdir()
        
        print(f"Successfully uninstalled rule '{rule_name}' from workspace '{workspace_name}'")

    def list_workspace_rules(self, workspace_name: str) -> List[str]:
        """List rules installed in a workspace.
        
        Args:
            workspace_name: Name of the workspace
            
        Returns:
            List of installed rule names
            
        Raises:
            WorkspaceNotFoundError: If workspace is not found
        """
        if workspace_name not in self.config.workspaces:
            raise WorkspaceNotFoundError(f"Workspace '{workspace_name}' not found")
        
        workspace = self.config.workspaces[workspace_name]
        rules_dir = workspace.path / ".amazonq" / "rules"
        
        if not rules_dir.exists():
            return []
        
        return [f.stem for f in rules_dir.glob("*.md")]

    def _check_dependencies(self, dependencies: List[str]) -> None:
        """Check if rule dependencies are satisfied.
        
        Args:
            dependencies: List of dependency rule names
            
        Raises:
            RuleManagerError: If dependencies are not satisfied
        """
        missing_deps = []
        
        for dep in dependencies:
            if dep not in self.catalog.rules:
                missing_deps.append(dep)
        
        if missing_deps:
            raise RuleManagerError(f"Missing dependencies: {', '.join(missing_deps)}")

    def _check_conflicts(self, conflicts: List[str], source: RuleSource, 
                        workspace_name: Optional[str] = None) -> None:
        """Check for rule conflicts.
        
        Args:
            conflicts: List of conflicting rule names
            source: Source to check conflicts in
            workspace_name: Workspace name if checking workspace conflicts
            
        Raises:
            RuleConflictError: If conflicts are found
        """
        if not conflicts:
            return
        
        existing_rules = set()
        
        if source == RuleSource.GLOBAL:
            existing_rules = set(self.list_global_rules())
        elif source == RuleSource.WORKSPACE and workspace_name:
            existing_rules = set(self.list_workspace_rules(workspace_name))
        
        conflicting_rules = set(conflicts) & existing_rules
        
        if conflicting_rules:
            raise RuleConflictError(f"Conflicting rules found: {', '.join(conflicting_rules)}")

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA256 checksum of content.
        
        Args:
            content: Content to checksum
            
        Returns:
            Hexadecimal checksum
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def export_workspace_rules(self, workspace_name: str, export_path: Path) -> None:
        """Export workspace rules to a directory.
        
        Args:
            workspace_name: Name of the workspace
            export_path: Path to export rules to
            
        Raises:
            WorkspaceNotFoundError: If workspace is not found
        """
        if workspace_name not in self.config.workspaces:
            raise WorkspaceNotFoundError(f"Workspace '{workspace_name}' not found")
        
        workspace = self.config.workspaces[workspace_name]
        rules_dir = workspace.path / ".amazonq" / "rules"
        
        if not rules_dir.exists():
            print(f"No rules found in workspace '{workspace_name}'")
            return
        
        export_path.mkdir(parents=True, exist_ok=True)
        
        for rule_file in rules_dir.glob("*.md"):
            shutil.copy2(rule_file, export_path / rule_file.name)
        
        print(f"Exported rules from workspace '{workspace_name}' to {export_path}")

    def import_workspace_rules(self, workspace_name: str, import_path: Path, 
                              force: bool = False) -> None:
        """Import rules to a workspace from a directory.
        
        Args:
            workspace_name: Name of the workspace
            import_path: Path to import rules from
            force: Force import even if rules exist
            
        Raises:
            WorkspaceNotFoundError: If workspace is not found
            RuleManagerError: If import fails
        """
        if workspace_name not in self.config.workspaces:
            raise WorkspaceNotFoundError(f"Workspace '{workspace_name}' not found")
        
        if not import_path.exists():
            raise RuleManagerError(f"Import path '{import_path}' does not exist")
        
        workspace = self.config.workspaces[workspace_name]
        rules_dir = workspace.path / ".amazonq" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        imported_count = 0
        
        for rule_file in import_path.glob("*.md"):
            rule_name = rule_file.stem
            target_path = rules_dir / rule_file.name
            
            if target_path.exists() and not force:
                print(f"Skipping '{rule_name}' (already exists, use --force to overwrite)")
                continue
            
            shutil.copy2(rule_file, target_path)
            
            if rule_name not in workspace.installed_rules:
                workspace.installed_rules.append(rule_name)
            
            imported_count += 1
        
        if imported_count > 0:
            workspace.updated_at = datetime.now()
            self._save_config()
        
        print(f"Imported {imported_count} rules to workspace '{workspace_name}'")
