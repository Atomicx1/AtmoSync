"""
AtmoSync Centralized Configuration & Zone Coordinates
Author: Vikram Raj (Team Lead)
Branch: member-vikram-lead
Ref: ITS/DA/1721
"""

import os

# Base Project Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_FILE = os.path.join(BASE_DIR, "data", "raw", "raw_microclimate_zones.csv")
PROCESSED_DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "processed_microclimate_zones.csv")

# Micro-Climate Monitoring Zones (Coordinates & Baseline Metadata)
MICROCLIMATE_ZONES = {
    "Zone_Urban_Core": {
        "name": "Urban Core (Baseline)",
        "lat": 28.6139,
        "lon": 77.2090,
        "description": "High-density concrete heat island baseline"
    },
    "Zone_Suburban_East": {
        "name": "Suburban East",
        "lat": 28.6304,
        "lon": 77.3721,
        "description": "Mixed residential and moderate vegetation corridor"
    },
    "Zone_Tech_Corridor": {
        "name": "Tech Corridor",
        "lat": 28.4595,
        "lon": 77.0266,
        "description": "Commercial glass-tower zone with high solar reflection"
    },
    "Zone_Rural_Boundary": {
        "name": "Rural Boundary",
        "lat": 28.8386,
        "lon": 77.1025,
        "description": "Open agricultural land with rapid nocturnal cooling"
    }
}

# Arbitrage & Anomaly Thresholds
ROLLING_WINDOW_HOURS = 24
Z_SCORE_ALERT_THRESHOLD = 2.0
MIN_EXPECTED_RECORDS = 1344
