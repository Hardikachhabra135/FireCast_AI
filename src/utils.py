"""
FireCast AI — Utility Functions & Configuration Helpers
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("FireCastAI")


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load and parse the central YAML configuration file."""
    if not os.path.isabs(config_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, config_path)
    
    if not os.path.exists(config_path):
        logger.warning(f"Config file not found at {config_path}. Searching workspace root.")
        if os.path.exists("config.yaml"):
            config_path = "config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def get_plotly_theme(theme_mode: str = "dark") -> Dict[str, Any]:
    """
    Returns custom theme layout properties for Plotly charts matching
    the FireCast AI design system via active theme tokens.
    """
    from theme import get_plotly_spatial_theme
    return get_plotly_spatial_theme(theme_mode)


def format_hectares(ha: float) -> str:
    """Format burned area in hectares with appropriate precision."""
    if ha < 0.001:
        return "0.00 ha"
    elif ha < 10.0:
        return f"{ha:.2f} ha"
    elif ha < 100.0:
        return f"{ha:.1f} ha"
    else:
        return f"{ha:,.1f} ha"


def clean_html(html_str: str) -> str:
    """Removes all leading/trailing whitespace and empty lines to prevent Streamlit from interpreting indentation as code blocks."""
    return "".join(line.strip() for line in html_str.splitlines() if line.strip())

