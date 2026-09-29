import pandas as pd
from typing import Dict, Any, List

class SchemaDetector:
    UNIT_HINTS = {
        "temp": "°C",
        "temperature": "°C",
        "press": "hPa",
        "pressure": "hPa",
        "wind_spd": "m/s",
        "wind_speed": "m/s",
        "humidity": "%",
        "rh": "%",
        "solar": "W/m²",
        "radiation": "W/m²",
        "depth": "m",
        "salinity": "PSU"
    }

    @classmethod
    def detect_schema(cls, df: pd.DataFrame) -> Dict[str, Any]:
        schema = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "timestamp_column": None,
            "numerical_columns": [],
            "categorical_columns": [],
            "column_details": {},
            "date_range": None
        }

        for col in df.columns:
            col_lower = str(col).lower()
            if any(term in col_lower for term in ["time", "date", "timestamp", "datetime", "year"]):
                try:
                    sample_series = pd.to_datetime(df[col].dropna().head(100), errors='coerce')
                    valid_count = sample_series.notnull().sum()
                    if valid_count > 0 and (valid_count / len(sample_series)) >= 0.8:
                        schema["timestamp_column"] = col
                        break
                except Exception:
                    pass

        if schema["timestamp_column"]:
            try:
                dt_series = pd.to_datetime(df[schema["timestamp_column"]], errors='coerce')
                valid_dt = dt_series.dropna()
                if not valid_dt.empty:
                    schema["date_range"] = {
                        "start": valid_dt.min().isoformat(),
                        "end": valid_dt.max().isoformat()
                    }
            except Exception:
                pass

        for col in df.columns:
            dtype_str = str(df[col].dtype)
            missing_count = int(df[col].isnull().sum())
            missing_pct = round((missing_count / len(df)) * 100, 2) if len(df) > 0 else 0

            inferred_unit = "N/A"
            for hint_key, hint_unit in cls.UNIT_HINTS.items():
                if hint_key in str(col).lower():
                    inferred_unit = hint_unit
                    break

            if pd.api.types.is_numeric_dtype(df[col]):
                schema["numerical_columns"].append(col)
                schema["column_details"][col] = {
                    "type": "numeric",
                    "dtype": dtype_str,
                    "unit": inferred_unit,
                    "missing_count": missing_count,
                    "missing_percentage": missing_pct,
                    "min": float(df[col].min()) if df[col].notnull().any() else None,
                    "max": float(df[col].max()) if df[col].notnull().any() else None,
                    "mean": round(float(df[col].mean()), 3) if df[col].notnull().any() else None
                }
            else:
                schema["categorical_columns"].append(col)
                schema["column_details"][col] = {
                    "type": "categorical",
                    "dtype": dtype_str,
                    "unit": inferred_unit,
                    "missing_count": missing_count,
                    "missing_percentage": missing_pct,
                    "unique_values": int(df[col].nunique())
                }

        return schema
