"""Tests for data models."""

import pytest
from datetime import datetime
from pathlib import Path

from amazon_q_rule_manager.models import (
    RuleMetadata,
    RuleCategory,
    RuleSource,
    Rule,
    RuleCatalog,
    WorkspaceConfig,
    GlobalConfig,
)


def test_rule_metadata_creation():
    """Test creating rule metadata."""
    metadata = RuleMetadata(
        name="test-rule",
        title="Test Rule",
        description="A test rule",
        category=RuleCategory.PYTHON,
        tags=["test", "python"],
    )
    
    assert metadata.name == "test-rule"
    assert metadata.title == "Test Rule"
    assert metadata.category == RuleCategory.PYTHON
    assert "test" in metadata.tags
    assert "python" in metadata.tags


def test_rule_creation():
    """Test creating a complete rule."""
    metadata = RuleMetadata(
        name="test-rule",
        title="Test Rule",
        description="A test rule",
        category=RuleCategory.PYTHON,
    )
    
    rule = Rule(
        metadata=metadata,
        content="# Test Rule\n\nThis is a test rule.",
        source=RuleSource.LOCAL,
    )
    
    assert rule.metadata.name == "test-rule"
    assert rule.source == RuleSource.LOCAL
    assert "test rule" in rule.content.lower()


def test_rule_catalog():
    """Test rule catalog functionality."""
    catalog = RuleCatalog()
    
    metadata = RuleMetadata(
        name="test-rule",
        title="Test Rule",
        description="A test rule",
        category=RuleCategory.PYTHON,
        tags=["test"],
    )
    
    catalog.add_rule(metadata)
    
    assert "test-rule" in catalog.rules
    assert RuleCategory.PYTHON in catalog.categories
    assert "test-rule" in catalog.categories[RuleCategory.PYTHON]
    assert "test" in catalog.tags
    assert "test-rule" in catalog.tags["test"]


def test_workspace_config():
    """Test workspace configuration."""
    workspace = WorkspaceConfig(
        name="test-workspace",
        path=Path("/tmp/test"),
        installed_rules=["rule1", "rule2"],
    )
    
    assert workspace.name == "test-workspace"
    assert workspace.path == Path("/tmp/test")
    assert len(workspace.installed_rules) == 2
    assert "rule1" in workspace.installed_rules


def test_global_config():
    """Test global configuration."""
    config = GlobalConfig(
        default_remote_url="https://example.com/catalog.json",
        cache_directory=Path("/tmp/cache"),
        global_rules_directory=Path("/tmp/rules"),
    )
    
    assert str(config.default_remote_url) == "https://example.com/catalog.json"
    assert config.cache_directory == Path("/tmp/cache")
    assert config.global_rules_directory == Path("/tmp/rules")
