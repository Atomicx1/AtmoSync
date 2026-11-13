
import pandas as pd
import pytest

from src.analytics.correlation import (
    prepare_climate_data,
    aggregate_weekly_climate,
    calculate_zone_correlations
)


def sample_data():

    records = []

    for week in range(4):
        for zone, latitude, longitude in [
            ("A", 5, 5),
            ("B", 15, 15),
            ("C", 25, 25)
        ]:

            records.append({
                "Timestamp": (
                    pd.Timestamp("2026-01-05")
                    + pd.Timedelta(weeks=week)
                ),
                "Latitude": latitude,
                "Longitude": longitude,
                "Temperature": 20 + week * 2 + ord(zone) % 5,
                "Humidity": 60 + week * 3 + ord(zone) % 4
            })

    return pd.DataFrame(records)


def test_zone_assignment():

    result = prepare_climate_data(sample_data())

    assert result["zone_id"].nunique() == 3


def test_weekly_aggregation():

    climate = prepare_climate_data(sample_data())
    weekly = aggregate_weekly_climate(climate)

    assert len(weekly) == 12
    assert "temperature_mean" in weekly.columns
    assert "humidity_mean" in weekly.columns


def test_correlation_calculation():

    climate = prepare_climate_data(sample_data())
    weekly = aggregate_weekly_climate(climate)

    pivot, correlation = calculate_zone_correlations(
        weekly,
        "temperature_mean",
        method="pearson",
        min_periods=3
    )

    assert pivot.shape == (4, 3)
    assert correlation.shape == (3, 3)
    assert correlation.notna().any().any()


def test_missing_required_column():

    invalid = sample_data().drop(columns=["Humidity"])

    with pytest.raises(ValueError):
        prepare_climate_data(invalid)
