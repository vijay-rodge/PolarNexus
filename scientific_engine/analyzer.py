import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from config.constants import ALLOWED_SCIENTIFIC_OPERATIONS

class ScientificDataAnalyzer:
    @classmethod
    def resolve_parameter_column(cls, df: pd.DataFrame, parameter_name: str) -> Optional[str]:
        param_norm = parameter_name.lower().strip()
        for col in df.columns:
            if col.lower() == param_norm:
                return col
                
        aliases = {
            "temperature": ["temp", "temperature", "air_temperature", "dry_bulb", "t_air"],
            "wind_speed": ["wind_speed", "wind_spd", "wspd", "wind_vel", "velocity"],
            "wind_direction": ["wind_direction", "wind_dir", "wdir", "azimuth"],
            "pressure": ["pressure", "atmospheric_pressure", "baro", "slp", "barometric_pressure"],
            "humidity": ["humidity", "relative_humidity", "rh"],
            "solar_radiation": ["solar", "radiation", "flux", "srad", "irradiance"]
        }
        for canonical, alias_list in aliases.items():
            if param_norm in alias_list or any(a in param_norm for a in alias_list):
                for col in df.columns:
                    col_lower = col.lower()
                    if any(a in col_lower for a in alias_list):
                        return col
        return None

    @classmethod
    def filter_by_time(cls, df: pd.DataFrame, year: Optional[int] = None, 
                       start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        date_cols = [c for c in df.columns if any(t in str(c).lower() for t in ["timestamp", "date", "time"])]
        if not date_cols:
            return df
            
        time_col = date_cols[0]
        temp_df = df.copy()
        temp_df["__datetime"] = pd.to_datetime(temp_df[time_col], errors="coerce")
        temp_df = temp_df.dropna(subset=["__datetime"])

        if year:
            temp_df = temp_df[temp_df["__datetime"].dt.year == int(year)]

        if start_date:
            try:
                start_dt = pd.to_datetime(start_date)
                temp_df = temp_df[temp_df["__datetime"] >= start_dt]
            except Exception:
                pass

        if end_date:
            try:
                end_dt = pd.to_datetime(end_date)
                temp_df = temp_df[temp_df["__datetime"] <= end_dt]
            except Exception:
                pass

        return temp_df

    @classmethod
    def execute_analysis(
        cls,
        df: pd.DataFrame,
        parameter: str,
        operation: str = "mean",
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        station_name: str = "Unknown",
        dataset_title: str = "NCPOR Polar Dataset"
    ) -> Dict[str, Any]:
        operation = operation.lower().strip()
        if operation not in ALLOWED_SCIENTIFIC_OPERATIONS:
            return {
                "success": False,
                "error": f"Operation '{operation}' not permitted. Allowed: {ALLOWED_SCIENTIFIC_OPERATIONS}"
            }

        col = cls.resolve_parameter_column(df, parameter)
        if not col:
            return {
                "success": False,
                "error": f"Parameter '{parameter}' not found in dataset columns: {list(df.columns)}"
            }

        filtered_df = cls.filter_by_time(df, year=year, start_date=start_date, end_date=end_date)
        if len(filtered_df) == 0:
            return {
                "success": False,
                "error": f"No records found for station '{station_name}' parameter '{parameter}' in period: year={year}, range=({start_date} to {end_date})"
            }

        series = pd.to_numeric(filtered_df[col], errors="coerce").dropna()
        if len(series) == 0:
            return {
                "success": False,
                "error": f"No valid numerical values for column '{col}' after cleaning"
            }

        value = None
        details = {}

        if operation == "mean":
            value = round(float(series.mean()), 3)
            details = {
                "std": round(float(series.std()), 3),
                "min": round(float(series.min()), 3),
                "max": round(float(series.max()), 3),
                "sample_count": len(series)
            }
        elif operation == "median":
            value = round(float(series.median()), 3)
            details = {"sample_count": len(series)}
        elif operation == "min":
            value = round(float(series.min()), 3)
            min_idx = series.idxmin()
            if "__datetime" in filtered_df.columns:
                details["timestamp_recorded"] = str(filtered_df.loc[min_idx, "__datetime"])
        elif operation == "max":
            value = round(float(series.max()), 3)
            max_idx = series.idxmax()
            if "__datetime" in filtered_df.columns:
                details["timestamp_recorded"] = str(filtered_df.loc[max_idx, "__datetime"])
        elif operation == "std":
            value = round(float(series.std()), 3)
            details = {"variance": round(float(series.var()), 3), "sample_count": len(series)}
        elif operation == "count":
            value = len(series)
        elif operation == "monthly_average":
            if "__datetime" in filtered_df.columns:
                monthly = filtered_df.groupby(filtered_df["__datetime"].dt.strftime("%Y-%m"))[col].mean().round(2).to_dict()
                value = monthly
            else:
                value = round(float(series.mean()), 3)
        elif operation == "yearly_average":
            if "__datetime" in filtered_df.columns:
                yearly = filtered_df.groupby(filtered_df["__datetime"].dt.year)[col].mean().round(2).to_dict()
                value = yearly
            else:
                value = round(float(series.mean()), 3)
        elif operation == "trend_slope":
            x = np.arange(len(series))
            slope, intercept = np.polyfit(x, series.values, 1)
            value = round(float(slope * 1000), 4)
            details = {"direction": "warming/increasing" if slope > 0 else "cooling/decreasing", "raw_slope": float(slope)}

        unit = "N/A"
        col_lower = col.lower()
        if "temp" in col_lower:
            unit = "°C"
        elif "press" in col_lower:
            unit = "hPa"
        elif "wind" in col_lower and "speed" in col_lower:
            unit = "m/s"
        elif "humid" in col_lower:
            unit = "%"
        elif "rad" in col_lower:
            unit = "W/m²"

        return {
            "success": True,
            "station": station_name,
            "dataset_title": dataset_title,
            "parameter": col,
            "canonical_parameter": parameter,
            "unit": unit,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "operation": operation,
            "calculated_value": value,
            "sample_size": len(series),
            "details": details,
            "source_provenance": {
                "source_name": "National Polar Data Center (NPDC) / NCPOR AWS Archive",
                "verified_computation": True,
                "method": "Programmatic Pandas Vectorized Calculation (Non-LLM)"
            }
        }
