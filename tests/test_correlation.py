import pandas as pd
import pytest

from src.analytics.correlation import (
    prepare_climate_data,
    aggregate_daily_climate,
    calculate_zone_correlations,
)


def sample_data():
    return pd.DataFrame({
        "timestamp": [
            "2026-01-01", "2026-01-02",
            "2026-01-03", "2026-01-04",
            "2026-01-01", "2026-01-02",
            "2026-01-03", "2026-01-04",
        ],
        "zone_id": [
            "Zone_A", "Zone_A", "Zone_A", "Zone_A",
            "Zone_B", "Zone_B", "Zone_B", "Zone_B",
        ],
        "temperature_c": [20, 22, 24, 26, 21, 23, 25, 27],
        "humidity_pct": [60, 62, 64, 66, 61, 63, 65, 67],
    })


def test_actual_zone_identification():
    climate = prepare_climate_data(sample_data())

    assert climate["zone_id"].nunique() == 2
    assert set(climate["zone_id"]) == {"Zone_A", "Zone_B"}


def test_daily_aggregation():
    climate = prepare_climate_data(sample_data())
    daily = aggregate_daily_climate(climate)

    assert len(daily) == 8
    assert "temperature_mean" in daily.columns
    assert "humidity_mean" in daily.columns
    assert "observation_count" in daily.columns


def test_correlation_calculation():
    climate = prepare_climate_data(sample_data())
    daily = aggregate_daily_climate(climate)

    pivot, correlation = calculate_zone_correlations(
        daily,
        metric="temperature_mean",
        method="pearson",
        min_periods=3,
    )

    assert correlation.shape == (2, 2)
    assert correlation.loc["Zone_A", "Zone_B"] == pytest.approx(1.0)


def test_missing_required_column():
    df = sample_data().drop(columns=["temperature_c"])

    with pytest.raises(ValueError, match="Missing required columns"):
        prepare_climate_data(df)

