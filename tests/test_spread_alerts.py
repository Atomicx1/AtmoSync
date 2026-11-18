
import pandas as pd
import pytest

from src.analytics.spread_alerts import calculate_spread_alerts


def test_output_contains_threshold_columns():
    df = pd.DataFrame({"spread": [10, 12, 11, 13, 12, 14]})

    result = calculate_spread_alerts(df)

    assert "dynamic_threshold" in result.columns
    assert "alert" in result.columns
    assert "alert_status" in result.columns


def test_invalid_window():
    df = pd.DataFrame({"spread": [10, 12, 11]})

    with pytest.raises(ValueError):
        calculate_spread_alerts(df, window=1)


def test_missing_spread_column():
    df = pd.DataFrame({"price": [10, 12, 11]})

    with pytest.raises(ValueError):
        calculate_spread_alerts(df)


def test_alert_column_is_boolean():
    df = pd.DataFrame({"spread": [10, 12, 11, 13, 12, 14, 15, 40]})

    result = calculate_spread_alerts(df)

    assert result["alert"].dtype == bool
