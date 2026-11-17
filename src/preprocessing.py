"""
AtmoSync Telemetry Data Cleaning, Validation & Feature Preprocessing
Author: Vikram Raj (Team Lead)
Branch: member-vikram-lead
Ref: ITS/DA/1721
"""

import os
import pandas as pd
import numpy as np
from config import RAW_DATA_FILE, PROCESSED_DATA_FILE, MICROCLIMATE_ZONES


def load_and_clean_telemetry(
    input_path: str = RAW_DATA_FILE,
    output_path: str = PROCESSED_DATA_FILE,
) -> pd.DataFrame:
    """
    Loads raw micro-climate zone telemetry, validates schema and zone IDs,
    interpolates missing numeric readings, and computes Urban Heat Island (UHI) deltas.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Raw telemetry dataset not found at {input_path}")

    df = pd.read_csv(input_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values(["zone_id", "timestamp"]).reset_index(drop=True)

    valid_zones = set(MICROCLIMATE_ZONES.keys())
    df = df[df["zone_id"].isin(valid_zones)].copy()

    numeric_cols = [
        "temperature_c",
        "humidity_pct",
        "pressure_hpa",
        "solar_irradiance_wm2",
        "wind_speed_kmh",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df.groupby("zone_id")[col].transform(lambda s: s.interpolate(limit_direction="both"))

    # Compute hourly rural baseline temperature to quantify Urban Heat Island (UHI) delta
    rural_baseline = (
        df[df["zone_id"] == "Zone_Rural_Boundary"][["timestamp", "temperature_c"]]
        .rename(columns={"temperature_c": "rural_baseline_temp_c"})
    )
    df = df.merge(rural_baseline, on="timestamp", how="left")
    df["uhi_delta_c"] = (df["temperature_c"] - df["rural_baseline_temp_c"]).round(2)

    # Flag thermal spike anomalies using per-zone Z-score > 2.5
    zone_means = df.groupby("zone_id")["temperature_c"].transform("mean")
    zone_stds = df.groupby("zone_id")["temperature_c"].transform("std").replace(0, np.nan)
    df["temp_zscore"] = ((df["temperature_c"] - zone_means) / zone_stds).fillna(0.0).round(3)
    df["is_heat_anomaly"] = df["temp_zscore"] > 2.5

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    cleaned_df = load_and_clean_telemetry()
    anomaly_count = int(cleaned_df["is_heat_anomaly"].sum())
    print(f"Processed {len(cleaned_df)} clean records ({anomaly_count} heat anomalies flagged) -> {PROCESSED_DATA_FILE}")
