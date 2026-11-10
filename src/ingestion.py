"""
AtmoSync Data Ingestion Engine
Author: Vikram Raj (Team Lead)
Branch: member-vikram-lead
Ref: ITS/DA/1721
"""

import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)

# 4 distinct micro-climate monitoring zones (Urban Core vs Tech Corridor vs Rural Periphery)
ZONES = {
    "Zone_Urban_Core": {"lat": 12.9716, "lon": 77.5946},
    "Zone_Suburban_East": {"lat": 12.9698, "lon": 77.7500},
    "Zone_Tech_Corridor": {"lat": 12.8452, "lon": 77.6602},
    "Zone_Rural_Boundary": {"lat": 12.7409, "lon": 77.8253}
}

def fetch_microclimate_data(zone_name: str, lat: float, lon: float, days_back: int = 14) -> pd.DataFrame:
    """Fetches hourly historical micro-climate variables from Open-Meteo API."""
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days_back)
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "direct_normal_irradiance",
            "wind_speed_10m"
        ],
        "timezone": "Asia/Kolkata"
    }
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()
    
    hourly = payload.get("hourly", {})
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(hourly.get("time")),
        "temperature_c": hourly.get("temperature_2m"),
        "humidity_pct": hourly.get("relative_humidity_2m"),
        "pressure_hpa": hourly.get("surface_pressure"),
        "solar_irradiance_wm2": hourly.get("direct_normal_irradiance"),
        "wind_speed_kmh": hourly.get("wind_speed_10m")
    })
    
    df["zone_id"] = zone_name
    return df

def run_ingestion_pipeline():
    all_frames = []
    print("[*] Starting AtmoSync micro-climate ingestion...")
    for zone, coords in ZONES.items():
        print(f" -> Harvesting telemetry for {zone}...")
        zone_df = fetch_microclimate_data(zone, coords["lat"], coords["lon"])
        all_frames.append(zone_df)
    
    combined_df = pd.concat(all_frames, ignore_index=True)
    raw_path = os.path.join(DATA_DIR, "raw_microclimate_zones.csv")
    combined_df.to_csv(raw_path, index=False)
    print(f"[+] Ingestion complete. Saved {len(combined_df)} records to: {raw_path}")

if __name__ == "__main__":
    run_ingestion_pipeline()
