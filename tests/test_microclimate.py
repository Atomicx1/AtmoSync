
import pandas as pd
import pytest

from src.analytics.microclimate import (
    calculate_mvi,
    classify_mvi
)


def test_mvi_calculation():

    df = pd.DataFrame({
        "Temperature": [20, 21, 22, 23, 24],
        "Humidity": [50, 55, 60, 65, 70]
    })

    result = calculate_mvi(df)

    assert "MVI" in result.columns
    assert result["MVI"].notna().all()
    assert (result["MVI"] >= 0).all()


def test_missing_values():

    df = pd.DataFrame({
        "Temperature": [20, None, 22, 23],
        "Humidity": [50, 55, None, 65]
    })

    result = calculate_mvi(df)

    assert result["MVI"].notna().all()


def test_invalid_data():

    df = pd.DataFrame({
        "Temperature": [20, 20, 20],
        "Humidity": [50, 60, 70]
    })

    with pytest.raises(ValueError):
        calculate_mvi(df)


def test_mvi_classification():

    assert classify_mvi(0.5) == "Normal"
    assert classify_mvi(1.5) == "Moderate"
    assert classify_mvi(2.5) == "High"
