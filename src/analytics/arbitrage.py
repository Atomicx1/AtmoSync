"""
AtmoSync Urban Heat Island (UHI) Thermal Arbitrage & Load-Shifting Engine
Author: Vikram Raj (Team Lead)
Branch: member-vikram-lead
Ref: ITS/DA/1721
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Ensure src/ is importable whether invoked from repo root or src/
SRC_DIR = str(Path(__file__).resolve().parents[1])
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config import PROCESSED_DATA_FILE, BASE_DIR, MICROCLIMATE_ZONES


ARBITRAGE_REPORT_FILE = os.path.join(BASE_DIR, "reports", "arbitrage_recommendations.csv")


def compute_thermal_arbitrage(
    input_path: str = PROCESSED_DATA_FILE,
    output_path: str = ARBITRAGE_REPORT_FILE,
    uhi_threshold_c: float = 2.5,
) -> pd.DataFrame:
    """
    Identifies peak Urban Heat Island (UHI) stress hours across zones and pairs
    overheated zones with the coolest available sink zone for thermal load-shifting
    or micro-grid cooling dispatch.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Processed telemetry file not found at {input_path}")

    df = pd.read_csv(input_path)
    required_cols = {"timestamp", "zone_id", "temperature_c", "humidity_pct", "uhi_delta_c"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in processed dataset: {missing}")

    if "zone_name" not in df.columns:
        df["zone_name"] = df["zone_id"].map(
            lambda z: MICROCLIMATE_ZONES.get(z, {}).get("name", z)
        )

    # Find the coolest reference zone at each hourly timestamp
    coolest_per_hour = (
        df.sort_values("temperature_c")
        .groupby("timestamp", as_index=False)
        .first()[["timestamp", "zone_id", "zone_name", "temperature_c"]]
        .rename(
            columns={
                "zone_id": "sink_zone_id",
                "zone_name": "sink_zone_name",
                "temperature_c": "sink_temp_c",
            }
        )
    )

    merged = df.merge(coolest_per_hour, on="timestamp", how="left")
    merged["thermal_spread_c"] = (merged["temperature_c"] - merged["sink_temp_c"]).round(2)

    # Filter high-stress hours where UHI delta exceeds threshold and another zone is cooler
    opportunities = merged[
        (merged["uhi_delta_c"] >= uhi_threshold_c)
        & (merged["zone_id"] != merged["sink_zone_id"])
    ].copy()

    opportunities["severity"] = pd.cut(
        opportunities["uhi_delta_c"],
        bins=[2.49, 3.5, 5.0, float("inf")],
        labels=["MODERATE", "HIGH", "CRITICAL"],
    )

    # Estimate cooling energy saving potential (~4.5% HVAC efficiency gain per deg C thermal spread)
    opportunities["est_cooling_saving_pct"] = (opportunities["thermal_spread_c"] * 4.5).round(1)

    report_cols = [
        "timestamp",
        "zone_id",
        "zone_name",
        "temperature_c",
        "uhi_delta_c",
        "sink_zone_id",
        "sink_temp_c",
        "thermal_spread_c",
        "severity",
        "est_cooling_saving_pct",
    ]
    report_df = opportunities[report_cols].sort_values(
        ["thermal_spread_c", "timestamp"], ascending=[False, True]
    ).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report_df.to_csv(output_path, index=False)
    return report_df


if __name__ == "__main__":
    arbitrage_df = compute_thermal_arbitrage()
    print(f"Identified {len(arbitrage_df)} thermal arbitrage windows -> {ARBITRAGE_REPORT_FILE}")
    if not arbitrage_df.empty:
        print("\nTop 5 Peak Thermal Arbitrage Windows:")
        print(arbitrage_df.head(5).to_string(index=False))
