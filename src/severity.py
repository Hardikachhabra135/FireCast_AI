"""
FireCast AI — Severity Band Classification & Operational Risk Analytics
"""

from typing import Dict, Any, Optional
from src.utils import load_config

DEFAULT_BANDS = {
    "low": {
        "name": "Low Severity",
        "min_ha": 0.0,
        "max_ha": 2.5,
        "percentile_ref": "< 50th percentile of non-zero fires",
        "color": "#35D39A",
        "bg_color": "rgba(53, 211, 154, 0.12)",
        "border_color": "#35D39A",
        "summary": "Localized surface burn with limited horizontal spread potential under current conditions."
    },
    "moderate": {
        "name": "Moderate Severity",
        "min_ha": 2.5,
        "max_ha": 10.0,
        "percentile_ref": "50th – 75th percentile of non-zero fires",
        "color": "#FF9F43",
        "bg_color": "rgba(255, 159, 67, 0.12)",
        "border_color": "#FF9F43",
        "summary": "Medium flame length; capable of moderate flank expansion in dry forest fuel beds."
    },
    "high": {
        "name": "High Severity",
        "min_ha": 10.0,
        "max_ha": 35.0,
        "percentile_ref": "75th – 90th percentile of non-zero fires",
        "color": "#FF6B35",
        "bg_color": "rgba(255, 107, 53, 0.15)",
        "border_color": "#FF6B35",
        "summary": "Substantial perimeter expansion; high resistance to direct perimeter containment."
    },
    "extreme": {
        "name": "Extreme Severity",
        "min_ha": 35.0,
        "max_ha": 99999.0,
        "percentile_ref": "≥ 90th percentile of non-zero fires",
        "color": "#FF4757",
        "bg_color": "rgba(255, 71, 87, 0.18)",
        "border_color": "#FF4757",
        "summary": "Crown fire potential, rapid ember spotting, and multi-sector flank advancement."
    }
}


def classify_severity(burned_area_ha: float, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Classifies a predicted burned area in hectares into analytical severity bands
    calibrated against empirical non-zero wildfire distributions from Montesinho Park.
    """
    if config and "severity_bands" in config:
        bands = config["severity_bands"]
    else:
        bands = DEFAULT_BANDS

    burned_area_ha = max(0.0, float(burned_area_ha))
    
    if burned_area_ha < bands["low"]["max_ha"]:
        selected_key = "low"
    elif burned_area_ha < bands["moderate"]["max_ha"]:
        selected_key = "moderate"
    elif burned_area_ha < bands["high"]["max_ha"]:
        selected_key = "high"
    else:
        selected_key = "extreme"
        
    band_info = bands[selected_key].copy()
    band_info["key"] = selected_key
    band_info["burned_area_ha"] = round(burned_area_ha, 2)
    band_info["disclaimer"] = (
        "IMPORTANT: This is an analytical severity categorization based on conditional burned area "
        "if a fire occurs. It does NOT predict ignition probability or replace official civil protection warnings."
    )
    return band_info
