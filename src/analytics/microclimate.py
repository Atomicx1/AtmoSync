
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DATASET = ROOT / "smart_logistics_dataset.csv"
OUTPUT = ROOT / "reports" / "microclimate"


def calculate_mvi(df):
    """
    Calculate a standardized temperature-humidity
    deviation index using the supplied dataset.

    Baseline statistics are calculated across the
    supplied observations. This is exploratory MVI,
    not a validated spoilage-risk score.
    """

    required = ["Temperature", "Humidity"]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    data = df.copy()

    for col in required:
        data[col] = pd.to_numeric(
            data[col], errors="coerce"
        )

    data = data.dropna(subset=required)

    if len(data) < 2:
        raise ValueError(
            "At least two valid observations are required."
        )

    # Calculate baseline statistics.
    temp_mean = data["Temperature"].mean()
    temp_std = data["Temperature"].std()

    humidity_mean = data["Humidity"].mean()
    humidity_std = data["Humidity"].std()

    if temp_std == 0 or humidity_std == 0:
        raise ValueError(
            "Cannot calculate MVI when a variable "
            "has zero standard deviation."
        )

    # Standardized deviations.
    data["temperature_z"] = (
        data["Temperature"] - temp_mean
    ) / temp_std

    data["humidity_z"] = (
        data["Humidity"] - humidity_mean
    ) / humidity_std

    # Combined index.
    data["MVI"] = (
        data["temperature_z"].abs()
        + data["humidity_z"].abs()
    ) / 2

    return data


def classify_mvi(value):

    if value < 1:
        return "Normal"

    elif value < 2:
        return "Moderate"

    else:
        return "High"


def run_analysis():

    if not DATASET.exists():
        raise FileNotFoundError(DATASET)

    OUTPUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATASET)

    result = calculate_mvi(df)

    result["MVI_Status"] = result["MVI"].apply(
        classify_mvi
    )

    output_file = OUTPUT / "microclimate_results.csv"

    result.to_csv(output_file, index=False)

    print("\nATMO SYNC MICRO-CLIMATE ANALYSIS")
    print("=" * 50)

    print("\nBaseline:")
    print("Temperature mean:", result["Temperature"].mean())
    print("Humidity mean:", result["Humidity"].mean())

    print("\nMVI statistics:")
    print(result["MVI"].describe())

    print("\nMVI classification:")
    print(result["MVI_Status"].value_counts())

    print("\nSaved report:", output_file)


if __name__ == "__main__":
    run_analysis()
