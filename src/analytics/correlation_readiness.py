
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATASET = ROOT / "smart_logistics_dataset.csv"


def inspect_correlation_readiness():

    df = pd.read_csv(DATASET)

    # Convert timestamps
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce"
    )

    # Required columns
    required = [
        "Timestamp",
        "Asset_ID",
        "Latitude",
        "Longitude",
        "Temperature",
        "Humidity"
    ]

    print("\nCORRELATION READINESS REPORT")
    print("=" * 55)

    print("\nDataset shape:", df.shape)

    print("\nMissing values:")
    print(df[required].isnull().sum())

    print("\nUnique assets:")
    print(df["Asset_ID"].nunique())

    print(df["Asset_ID"].value_counts())

    print("\nTimestamp range:")
    print("Start:", df["Timestamp"].min())
    print("End:", df["Timestamp"].max())

    print("\nDuplicate timestamps:")
    print(df["Timestamp"].duplicated().sum())

    print("\nGeographic coordinate summary:")
    print(
        df[["Latitude", "Longitude"]].describe()
    )

    print("\nTemperature summary:")
    print(df["Temperature"].describe())

    print("\nHumidity summary:")
    print(df["Humidity"].describe())

    print("\nRecords per asset:")
    print(
        df.groupby("Asset_ID").size()
    )

    print("\nFirst 10 records:")
    print(df[required].head(10).to_string(index=False))


if __name__ == "__main__":
    inspect_correlation_readiness()
