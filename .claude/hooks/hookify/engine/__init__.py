# .claude/hookify/engine/__init__.py
"""Hookify engine module for Wythm project.

Self-managed copy migrated from global hookify plugin.

Note: Uses absolute imports for compatibility with standalone script execution.
"""
# For package imports when engine is used as a module
try:
    from .config_loader import load_rules, Rule, Condition
    from .rule_engine import RuleEngine
except ImportError:
    # Fallback for standalone script execution
    from config_loader import load_rules, Rule, Condition
    from rule_engine import RuleEngine

__all__ = ['load_rules', 'Rule', 'Condition', 'RuleEngine']
