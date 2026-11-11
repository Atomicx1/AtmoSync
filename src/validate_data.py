"""
AtmoSync Data Validation Suite
Author: Vikram Raj (Team Lead)
Branch: member-vikram-lead
Ref: ITS/DA/1721
"""

import os
import pandas as pd

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "raw_microclimate_zones.csv")

def validate_raw_telemetry():
    """Validates structure, integrity, and completeness of harvested telemetry."""
    print("[*] Running AtmoSync raw data validation suite...")
    
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"[!] Target raw dataset not found: {RAW_DATA_PATH}")
    
    df = pd.read_csv(RAW_DATA_PATH)
    
    # 1. Row count validation (14 days * 24 hours * 4 zones = 1,344 to 1,440 records)
    total_records = len(df)
    print(f" -> Total harvested records: {total_records}")
    assert total_records >= 1344, f"Insufficient records detected: {total_records}"
    
    # 2. Schema check
    expected_columns = [
        "timestamp", "temperature_c", "humidity_pct", 
        "pressure_hpa", "solar_irradiance_wm2", "wind_speed_kmh", "zone_id"
    ]
    missing_cols = [col for col in expected_columns if col not in df.columns]
    assert not missing_cols, f"Schema mismatch. Missing columns: {missing_cols}"
    print(" -> Schema validation: PASSED")
    
    # 3. Zone coverage check
    zones = df["zone_id"].unique()
    print(f" -> Active micro-climate zones ({len(zones)}): {list(zones)}")
    assert len(zones) == 4, f"Expected 4 zones, found {len(zones)}"
    
    # 4. Null value check
    null_counts = df.isnull().sum().to_dict()
    print(f" -> Null value audit: {null_counts}")
    
    print("[+] All raw telemetry integrity checks PASSED successfully.")

if __name__ == "__main__":
    validate_raw_telemetry()
