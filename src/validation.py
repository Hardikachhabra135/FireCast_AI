"""
FireCast AI — Pydantic Input Validation & Domain Boundary Verification
Validates all 12 input features including spatial coordinates X and Y
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from src.preprocessing import MONTHS, DAYS, ALL_FEATURES
from src.utils import load_config


class FirePredictionInput(BaseModel):
    """
    Validated telemetry input schema for FireCast AI inference engine.
    Ensures correct types, domain limits, and categorical normalization.
    """
    X: int = Field(default=7, ge=1, le=9, description="Spatial X coordinate in Montesinho park grid (1 to 9)")
    Y: int = Field(default=4, ge=2, le=9, description="Spatial Y coordinate in Montesinho park grid (2 to 9)")
    month: str = Field(default="aug", description="Month of the year (3-letter abbreviation)")
    day: str = Field(default="sun", description="Day of the week (3-letter abbreviation)")
    temp: float = Field(default=21.0, ge=-10.0, le=60.0, description="Ambient air temperature in °C")
    RH: float = Field(default=38.0, ge=0.0, le=100.0, description="Relative humidity in %")
    wind: float = Field(default=4.5, ge=0.0, le=50.0, description="Wind speed in km/h")
    rain: float = Field(default=0.0, ge=0.0, le=100.0, description="Outside rainfall in mm")
    FFMC: float = Field(default=91.5, ge=10.0, le=100.0, description="Fine Fuel Moisture Code")
    DMC: float = Field(default=110.0, ge=0.0, le=400.0, description="Duff Moisture Code")
    DC: float = Field(default=650.0, ge=0.0, le=1000.0, description="Drought Code")
    ISI: float = Field(default=8.5, ge=0.0, le=80.0, description="Initial Spread Index")

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: str) -> str:
        v_clean = str(v).lower().strip()
        if v_clean not in MONTHS:
            raise ValueError(f"Invalid month '{v}'. Expected one of: {MONTHS}")
        return v_clean

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: str) -> str:
        v_clean = str(v).lower().strip()
        if v_clean not in DAYS:
            raise ValueError(f"Invalid day '{v}'. Expected one of: {DAYS}")
        return v_clean

    def to_dataframe_row(self):
        """Convert input to a single-row pandas DataFrame matching exact 12-feature schema order."""
        import pandas as pd
        return pd.DataFrame([{
            "X": int(self.X),
            "Y": int(self.Y),
            "month": self.month,
            "day": self.day,
            "FFMC": float(self.FFMC),
            "DMC": float(self.DMC),
            "DC": float(self.DC),
            "ISI": float(self.ISI),
            "temp": float(self.temp),
            "RH": float(self.RH),
            "wind": float(self.wind),
            "rain": float(self.rain)
        }])[ALL_FEATURES]


def check_training_boundary_warnings(input_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Checks if input parameters extrapolate beyond the historical boundaries
    observed in the Montesinho Natural Park training records (Cortez & Morais, 2007).
    Does NOT clip user queries, but alerts the user of potential out-of-distribution extrapolation.
    """
    if config is None:
        config = load_config()
    
    ranges = config.get("input_ranges", {})
    warnings = []

    for feature, bounds in ranges.items():
        if feature in input_data and "training_min" in bounds and "training_max" in bounds:
            val = float(input_data[feature])
            t_min = float(bounds["training_min"])
            t_max = float(bounds["training_max"])
            unit = bounds.get("unit", "")
            lbl = bounds.get("label", feature)
            
            if val < t_min:
                warnings.append(
                    f"**{lbl}** ({val} {unit}) is below the Montesinho historical record minimum ({t_min} {unit})."
                )
            elif val > t_max:
                warnings.append(
                    f"**{lbl}** ({val} {unit}) exceeds the Montesinho historical record maximum ({t_max} {unit}). "
                    f"Inference in this regime constitutes model extrapolation."
                )
                
    return warnings
