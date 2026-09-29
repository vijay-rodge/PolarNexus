import pandas as pd
import numpy as np
from typing import Dict, Any, List

class DataValidator:
    PHYSICAL_BOUNDS = {
        "air_temperature": (-95.0, 35.0),
        "temperature": (-95.0, 35.0),
        "temp": (-95.0, 35.0),
        "wind_speed": (0.0, 110.0),
        "wind_spd": (0.0, 110.0),
        "atmospheric_pressure": (800.0, 1085.0),
        "pressure": (800.0, 1085.0),
        "relative_humidity": (0.0, 100.0),
        "humidity": (0.0, 100.0),
        "solar_radiation": (0.0, 1500.0)
    }

    @classmethod
    def validate_dataset(cls, df: pd.DataFrame) -> Dict[str, Any]:
        total_rows = len(df)
        if total_rows == 0:
            return {
                "is_valid": False,
                "error": "Dataset is empty",
                "row_count": 0,
                "quality_score": 0.0
            }

        duplicate_rows = int(df.duplicated().sum())
        total_cells = df.size
        missing_cells = int(df.isnull().sum().sum())
        missing_percentage = round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0

        outliers_detected = {}
        for col in df.columns:
            col_lower = str(col).lower()
            matched_bound = None
            for param_key, bounds in cls.PHYSICAL_BOUNDS.items():
                if param_key in col_lower:
                    matched_bound = bounds
                    break
            
            if matched_bound and pd.api.types.is_numeric_dtype(df[col]):
                low, high = matched_bound
                invalid_mask = (df[col] < low) | (df[col] > high)
                outlier_count = int(invalid_mask.sum())
                if outlier_count > 0:
                    outliers_detected[col] = {
                        "count": outlier_count,
                        "percentage": round((outlier_count / total_rows) * 100, 2),
                        "bounds": matched_bound
                    }

        continuity_score = 1.0
        date_cols = [c for c in df.columns if any(t in str(c).lower() for t in ["time", "date", "timestamp"])]
        if date_cols:
            try:
                dt_series = pd.to_datetime(df[date_cols[0]], errors='coerce').dropna().sort_values()
                if len(dt_series) > 10:
                    time_diffs = dt_series.diff().dropna()
                    median_diff = time_diffs.median()
                    matching_diffs = (time_diffs >= median_diff * 0.8) & (time_diffs <= median_diff * 1.2)
                    continuity_score = round(float(matching_diffs.mean()), 3)
            except Exception:
                continuity_score = 0.9

        penalty = (missing_percentage / 100.0) * 0.4 + (duplicate_rows / total_rows) * 0.3
        quality_score = max(0.0, min(1.0, round(continuity_score * (1.0 - penalty), 3)))

        return {
            "is_valid": True,
            "row_count": total_rows,
            "column_count": len(df.columns),
            "missing_cells": missing_cells,
            "missing_percentage": missing_percentage,
            "duplicate_rows": duplicate_rows,
            "outliers_detected": outliers_detected,
            "date_continuity_score": continuity_score,
            "quality_score": quality_score
        }
