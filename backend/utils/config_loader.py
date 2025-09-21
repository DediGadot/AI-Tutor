#!/usr/bin/env python3
"""
Configuration Loader Utility
Loads and validates the config.yaml file with environment variable substitution.
"""

import os
import yaml
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from YAML file with environment variable substitution."""
    if config_path is None:
        # Look for config.yaml in the project root
        config_path = Path(__file__).parent.parent.parent / "config.yaml"

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_content = file.read()

        # Substitute environment variables
        config_content = substitute_env_vars(config_content)

        # Parse YAML
        config = yaml.safe_load(config_content)

        # Apply environment-specific overrides
        env = os.getenv('ENVIRONMENT', 'development')
        if 'environments' in config and env in config['environments']:
            config = merge_config(config, config['environments'][env])

        logger.info(f"✅ Configuration loaded successfully from {config_path}")
        return config

    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {e}")
        raise


def substitute_env_vars(content: str) -> str:
    """Substitute environment variables in the format ${VAR_NAME} or ${VAR_NAME:-default}."""
    import re

    def replace_var(match):
        var_expr = match.group(1)

        if ':-' in var_expr:
            # Handle default values: ${VAR_NAME:-default}
            var_name, default_value = var_expr.split(':-', 1)
            return os.getenv(var_name, default_value)
        else:
            # Simple variable: ${VAR_NAME}
            return os.getenv(var_expr, match.group(0))  # Return original if not found

    # Pattern to match ${VAR_NAME} or ${VAR_NAME:-default}
    pattern = r'\$\{([^}]+)\}'
    return re.sub(pattern, replace_var, content)


def merge_config(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge override configuration into base configuration."""
    merged = base_config.copy()

    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = value

    return merged


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate that required configuration sections exist."""
    required_sections = [
        'system',
        'llm',
        'agent',
        'gamification',
        'accessibility',
        'themes'
    ]

    for section in required_sections:
        if section not in config:
            logger.error(f"❌ Missing required configuration section: {section}")
            return False

    logger.info("✅ Configuration validation passed")
    return True


def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get a configuration value using dot notation path."""
    keys = path.split('.')
    current = config

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current