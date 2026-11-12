# AtmoSync System Architecture & Telemetry Data Dictionary
**Project Reference:** ITS/DA/1721  
**Team Lead:** Vikram Raj (`member-vikram-lead`)

---

## 1. Pipeline Architecture

AtmoSync follows a four-stage modular analytics workflow:
1. **Telemetry Ingestion (`src/ingestion.py`):** Pulls hourly weather records from the Open-Meteo Archive API across four distinct micro-climate coordinates.
2. **Data Validation (`src/validate_data.py`):** Audits schema integrity, verifies row counts, and checks null distributions prior to downstream processing.
3. **Feature Engineering (`src/preprocessing.py`):** Imputes missing sensor values and computes micro-climate spreads ($\Delta T$) relative to the Urban Core baseline.
4. **Arbitrage Engine & UI (`src/arbitrage_engine.py`, `app.py`):** Computes rolling Z-scores to trigger thermal arbitrage alerts and displays interactive visual trends via Streamlit.

---

## 2. Raw Telemetry Data Dictionary (`data/raw/raw_microclimate_zones.csv`)

| Column Name | Data Type | Unit / Format | Description |
| :--- | :--- | :--- | :--- |
| `timestamp` | `datetime64[ns, UTC]` | ISO-8601 UTC | Hourly measurement timestamp |
| `temperature_c` | `float64` | °C | Ambient air temperature at 2m elevation |
| `humidity_pct` | `float64` | % | Relative humidity at 2m elevation |
| `pressure_hpa` | `float64` | hPa | Surface atmospheric pressure |
| `solar_irradiance_wm2` | `float64` | W/m² | Shortwave solar radiation |
| `wind_speed_kmh` | `float64` | km/h | Wind velocity at 10m elevation |
| `zone_id` | `string` | Categorical | Micro-climate identifier (`Zone_Urban_Core`, `Zone_Suburban_East`, `Zone_Tech_Corridor`, `Zone_Rural_Boundary`) |
