"""Data models for Amazon Q Rule Manager."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, validator, field_validator


class RuleSource(str, Enum):
    """Source types for rules."""
    REMOTE = "remote"
    LOCAL = "local"
    GLOBAL = "global"
    WORKSPACE = "workspace"


class RuleCategory(str, Enum):
    """Categories for rules."""
    AWS = "aws"
    PYTHON = "python"
    TERRAFORM = "terraform"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    REACT = "react"
    RUBY = "ruby"
    SERVERLESS = "serverless"
    GENERAL = "general"


class RuleMetadata(BaseModel):
    """Metadata for a rule."""
    name: str = Field(..., description="Rule name (without .md extension)")
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Brief description of the rule")
    category: RuleCategory = Field(..., description="Rule category")
    version: str = Field(default="1.0.0", description="Rule version")
    author: Optional[str] = Field(None, description="Rule author")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    dependencies: List[str] = Field(default_factory=list, description="Rule dependencies")
    conflicts: List[str] = Field(default_factory=list, description="Conflicting rules")
    min_python_version: Optional[str] = Field(None, description="Minimum Python version")
    supported_languages: List[str] = Field(default_factory=list, description="Supported programming languages")
    aws_services: List[str] = Field(default_factory=list, description="Related AWS services")
    terraform_providers: List[str] = Field(default_factory=list, description="Related Terraform providers")
    examples: List[str] = Field(default_factory=list, description="Usage examples")
    documentation_url: Optional[HttpUrl] = Field(None, description="Documentation URL")
    source_url: Optional[HttpUrl] = Field(None, description="Source code URL")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class Rule(BaseModel):
    """A complete rule with metadata and content."""
    metadata: RuleMetadata
    content: str = Field(..., description="Rule content in Markdown format")
    source: RuleSource = Field(..., description="Source of the rule")
    local_path: Optional[Path] = Field(None, description="Local file path if applicable")
    remote_url: Optional[HttpUrl] = Field(None, description="Remote URL if applicable")
    checksum: Optional[str] = Field(None, description="Content checksum for integrity")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat(),
        }

    @field_validator('local_path', mode='before')
    @classmethod
    def validate_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v


class RuleCatalog(BaseModel):
    """Catalog of available rules with enhanced metadata."""
    version: str = Field(default="2.0.0", description="Catalog version")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    rules: Dict[str, RuleMetadata] = Field(default_factory=dict, description="Available rules")
    categories: Dict[str, List[str]] = Field(default_factory=dict, description="Rules by category")
    tags: Dict[str, List[str]] = Field(default_factory=dict, description="Rules by tag")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def add_rule(self, rule_metadata: RuleMetadata) -> None:
        """Add a rule to the catalog."""
        self.rules[rule_metadata.name] = rule_metadata
        
        # Update categories
        category = rule_metadata.category
        if category not in self.categories:
            self.categories[category] = []
        if rule_metadata.name not in self.categories[category]:
            self.categories[category].append(rule_metadata.name)
        
        # Update tags
        for tag in rule_metadata.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            if rule_metadata.name not in self.tags[tag]:
                self.tags[tag].append(rule_metadata.name)
        
        self.last_updated = datetime.now()

    def remove_rule(self, rule_name: str) -> None:
        """Remove a rule from the catalog."""
        if rule_name not in self.rules:
            return
        
        rule_metadata = self.rules[rule_name]
        
        # Remove from categories
        category = rule_metadata.category
        if category in self.categories and rule_name in self.categories[category]:
            self.categories[category].remove(rule_name)
            if not self.categories[category]:
                del self.categories[category]
        
        # Remove from tags
        for tag in rule_metadata.tags:
            if tag in self.tags and rule_name in self.tags[tag]:
                self.tags[tag].remove(rule_name)
                if not self.tags[tag]:
                    del self.tags[tag]
        
        # Remove rule
        del self.rules[rule_name]
        self.last_updated = datetime.now()

    def get_rules_by_category(self, category: RuleCategory) -> List[RuleMetadata]:
        """Get all rules in a specific category."""
        return [self.rules[name] for name in self.categories.get(category, [])]

    def get_rules_by_tag(self, tag: str) -> List[RuleMetadata]:
        """Get all rules with a specific tag."""
        return [self.rules[name] for name in self.tags.get(tag, [])]

    def search_rules(self, query: str) -> List[RuleMetadata]:
        """Search rules by name, title, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for rule in self.rules.values():
            if (query_lower in rule.name.lower() or
                query_lower in rule.title.lower() or
                query_lower in rule.description.lower() or
                any(query_lower in tag.lower() for tag in rule.tags)):
                results.append(rule)
        
        return results


class WorkspaceConfig(BaseModel):
    """Configuration for a workspace."""
    name: str = Field(..., description="Workspace name")
    path: Path = Field(..., description="Workspace path")
    installed_rules: List[str] = Field(default_factory=list, description="Installed rule names")
    rule_overrides: Dict[str, str] = Field(default_factory=dict, description="Rule content overrides")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat(),
        }

    @field_validator('path', mode='before')
    @classmethod
    def validate_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v


class GlobalConfig(BaseModel):
    """Global configuration for the rule manager."""
    version: str = Field(default="1.0.0", description="Config version")
    default_remote_url: HttpUrl = Field(..., description="Default remote catalog URL")
    cache_directory: Path = Field(..., description="Cache directory path")
    global_rules_directory: Path = Field(..., description="Global rules directory")
    auto_update_interval: int = Field(default=86400, description="Auto-update interval in seconds")
    last_update_check: Optional[datetime] = Field(None, description="Last update check timestamp")
    workspaces: Dict[str, WorkspaceConfig] = Field(default_factory=dict, description="Registered workspaces")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat(),
        }

    @field_validator('cache_directory', 'global_rules_directory', mode='before')
    @classmethod
    def validate_paths(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v
