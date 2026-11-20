"""
Unit Tests for AtmoSync UHI Thermal Arbitrage Engine
Author: Vikram Raj (Team Lead)
Branch: member-vikram-lead
Ref: ITS/DA/1721
"""

import sys
from pathlib import Path
import pandas as pd
import pytest

SRC_DIR = str(Path(__file__).resolve().parents[1] / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from analytics.arbitrage import compute_thermal_arbitrage


@pytest.fixture
def sample_telemetry_csv(tmp_path):
    """Creates a controlled 2-hour, 3-zone processed telemetry CSV for deterministic testing."""
    data = [
        # Hour 1: Urban Core is +4.2 C hotter than Rural Boundary -> HIGH severity arbitrage window
        {
            "timestamp": "2026-11-01 14:00:00",
            "zone_id": "Zone_Urban_Core",
            "temperature_c": 32.4,
            "humidity_pct": 42.0,
            "uhi_delta_c": 4.2,
        },
        {
            "timestamp": "2026-11-01 14:00:00",
            "zone_id": "Zone_Tech_Corridor",
            "temperature_c": 30.8,
            "humidity_pct": 45.0,
            "uhi_delta_c": 2.6,
        },
        {
            "timestamp": "2026-11-01 14:00:00",
            "zone_id": "Zone_Rural_Boundary",
            "temperature_c": 28.2,
            "humidity_pct": 54.0,
            "uhi_delta_c": 0.0,
        },
        # Hour 2: Mild nighttime spread (+1.1 C) -> below 2.5 C threshold, should be excluded
        {
            "timestamp": "2026-11-01 03:00:00",
            "zone_id": "Zone_Urban_Core",
            "temperature_c": 21.1,
            "humidity_pct": 70.0,
            "uhi_delta_c": 1.1,
        },
        {
            "timestamp": "2026-11-01 03:00:00",
            "zone_id": "Zone_Rural_Boundary",
            "temperature_c": 20.0,
            "humidity_pct": 75.0,
            "uhi_delta_c": 0.0,
        },
    ]
    input_csv = tmp_path / "processed_test.csv"
    output_csv = tmp_path / "arbitrage_test_out.csv"
    pd.DataFrame(data).to_csv(input_csv, index=False)
    return str(input_csv), str(output_csv)


def test_compute_thermal_arbitrage_identifies_peak_windows(sample_telemetry_csv):
    input_csv, output_csv = sample_telemetry_csv
    result = compute_thermal_arbitrage(
        input_path=input_csv,
        output_path=output_csv,
        uhi_threshold_c=2.5,
    )

    assert len(result) == 2
    assert Path(output_csv).exists()

    top_row = result.iloc[0]
    assert top_row["zone_id"] == "Zone_Urban_Core"
    assert top_row["sink_zone_id"] == "Zone_Rural_Boundary"
    assert top_row["thermal_spread_c"] == 4.2
    assert top_row["severity"] == "HIGH"
    assert top_row["est_cooling_saving_pct"] == 18.9


def test_compute_thermal_arbitrage_missing_file():
    with pytest.raises(FileNotFoundError):
        compute_thermal_arbitrage(input_path="non_existent_telemetry.csv")


def test_compute_thermal_arbitrage_missing_columns(tmp_path):
    bad_csv = tmp_path / "bad_schema.csv"
    pd.DataFrame({"timestamp": ["2026-11-01 00:00:00"], "temperature_c": [25.0]}).to_csv(bad_csv, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        compute_thermal_arbitrage(input_path=str(bad_csv))
