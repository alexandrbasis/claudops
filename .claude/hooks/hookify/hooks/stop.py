#!/usr/bin/env python3
"""Stop hook executor for hookify (project-local version).

This script is called by Claude Code when agent wants to stop.
It reads .claude/hookify/rules/*.local.md files and evaluates stop rules.
"""

import os
import sys
import json

# Add engine directory to Python path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'engine')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

try:
    from config_loader import load_rules
    from rule_engine import RuleEngine
except ImportError as e:
    error_msg = {"systemMessage": f"Hookify import error: {e}"}
    print(json.dumps(error_msg), file=sys.stdout)
    sys.exit(0)


def main():
    """Main entry point for Stop hook."""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Get project directory from input
        cwd = input_data.get('cwd')

        # Load stop rules
        rules = load_rules(event='stop', cwd=cwd)

        # Evaluate rules
        engine = RuleEngine()
        result = engine.evaluate_rules(rules, input_data)

        # Always output JSON (even if empty)
        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        # On any error, allow the operation
        error_output = {
            "systemMessage": f"Hookify error: {str(e)}"
        }
        print(json.dumps(error_output), file=sys.stdout)

    finally:
        # ALWAYS exit 0
        sys.exit(0)


if __name__ == '__main__':
    main()
