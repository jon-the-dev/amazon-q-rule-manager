"""Amazon Q Rule Manager - A robust manager for Amazon Q Developer rules."""

__version__ = "1.0.0"
__author__ = "Amazon Q Rules Team"
__email__ = "support@example.com"
__description__ = "A robust manager for Amazon Q Developer rules with global and workspace support"

from .core import RuleManager
from .models import Rule, RuleMetadata, RuleSource

__all__ = ["RuleManager", "Rule", "RuleMetadata", "RuleSource"]
