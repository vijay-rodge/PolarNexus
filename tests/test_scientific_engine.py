import pytest
import pandas as pd
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scientific_engine.analyzer import ScientificDataAnalyzer
from scientific_engine.schema_detector import SchemaDetector
from scientific_engine.validator import DataValidator
from config.settings import settings

def test_maitri_2012_temperature_calculation():
    csv_path = settings.RAW_DATA_DIR / "aws" / "maitri_aws_2012.csv"
    assert csv_path.exists(), "Maitri 2012 AWS CSV must exist"

    df = pd.read_csv(csv_path)
    result = ScientificDataAnalyzer.execute_analysis(
        df=df,
        parameter="air_temperature",
        operation="mean",
        year=2012,
        station_name="Maitri"
    )

    assert result["success"] is True
    assert result["station"] == "Maitri"
    assert result["operation"] == "mean"
    assert result["unit"] == "°C"
    assert -12.0 < result["calculated_value"] < -9.0
    assert result["sample_size"] == 8784

def test_security_disallows_arbitrary_code():
    df = pd.DataFrame({"air_temperature": [-10, -12, -8], "timestamp": ["2012-01-01", "2012-01-02", "2012-01-03"]})
    malicious_op = "__import__('os').system('dir')"
    result = ScientificDataAnalyzer.execute_analysis(
        df=df,
        parameter="air_temperature",
        operation=malicious_op
    )
    assert result["success"] is False
    assert "not permitted" in result["error"]

def test_schema_detector_identifies_timestamp_and_units():
    df = pd.DataFrame({
        "timestamp": ["2012-01-01 00:00:00", "2012-01-01 01:00:00"],
        "air_temperature": [-15.2, -14.8],
        "wind_speed": [8.5, 9.2]
    })
    schema = SchemaDetector.detect_schema(df)
    assert schema["timestamp_column"] == "timestamp"
    assert "air_temperature" in schema["numerical_columns"]
    assert schema["column_details"]["air_temperature"]["unit"] == "°C"
    assert schema["column_details"]["wind_speed"]["unit"] == "m/s"

def test_data_validator_identifies_outliers_and_hygiene():
    df = pd.DataFrame({
        "timestamp": ["2012-01-01 00:00:00", "2012-01-01 01:00:00"],
        "air_temperature": [-15.0, 75.0]
    })
    val_res = DataValidator.validate_dataset(df)
    assert val_res["is_valid"] is True
    assert "air_temperature" in val_res["outliers_detected"]
    assert val_res["outliers_detected"]["air_temperature"]["count"] == 1
