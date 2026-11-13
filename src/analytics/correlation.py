
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DATASET = ROOT / "smart_logistics_dataset.csv"
OUTPUT = ROOT / "reports" / "correlation"

REQUIRED_COLUMNS = [
    "Timestamp",
    "Latitude",
    "Longitude",
    "Temperature",
    "Humidity"
]


def prepare_climate_data(df, grid_degrees=10):
    """Validate climate records and assign exploratory grid zones."""

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    data = df[REQUIRED_COLUMNS].copy()

    data["Timestamp"] = pd.to_datetime(
        data["Timestamp"],
        errors="coerce"
    )

    numeric_columns = [
        "Latitude",
        "Longitude",
        "Temperature",
        "Humidity"
    ]

    for col in numeric_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    # Remove invalid timestamps and climate measurements.
    data = data.dropna(subset=REQUIRED_COLUMNS)

    # Validate geographic coordinates.
    valid_coordinates = (
        data["Latitude"].between(-90, 90)
        & data["Longitude"].between(-180, 180)
    )

    data = data[valid_coordinates].copy()

    if data.empty:
        raise ValueError(
            "No valid climate records available."
        )

    if grid_degrees <= 0:
        raise ValueError("grid_degrees must be positive.")

    # Assign geographic grid cells.
    data["lat_bin"] = (
        np.floor(data["Latitude"] / grid_degrees)
        * grid_degrees
    ).astype(int)

    data["lon_bin"] = (
        np.floor(data["Longitude"] / grid_degrees)
        * grid_degrees
    ).astype(int)

    data["zone_id"] = (
        "LAT_" + data["lat_bin"].astype(str)
        + "_LON_" + data["lon_bin"].astype(str)
    )

    # Aggregate readings by week.
    data["week"] = (
        data["Timestamp"]
        .dt.to_period("W")
        .astype(str)
    )

    return data


def aggregate_weekly_climate(data):
    """Calculate weekly average climate values per zone."""

    weekly = (
        data.groupby(["week", "zone_id"], as_index=False)
        .agg(
            temperature_mean=("Temperature", "mean"),
            humidity_mean=("Humidity", "mean"),
            observation_count=("Temperature", "size")
        )
    )

    return weekly


def calculate_zone_correlations(
    weekly,
    metric,
    method="pearson",
    min_periods=3
):
    """Calculate correlations between zones using aligned weeks."""

    pivot = weekly.pivot(
        index="week",
        columns="zone_id",
        values=metric
    )

    # Correlation is calculated only for sufficiently
    # overlapping weekly observations.
    correlation = pivot.corr(
        method=method,
        min_periods=min_periods
    )

    return pivot, correlation


def save_heatmap(correlation, filename, title):
    """Save a correlation heatmap."""

    if correlation.empty:
        print(f"Skipping heatmap: {title}")
        return

    if len(correlation.columns) < 2:
        print(f"Not enough zones for heatmap: {title}")
        return

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 8))

    image = ax.imshow(
        correlation,
        cmap="coolwarm",
        vmin=-1,
        vmax=1
    )

    ax.set_xticks(range(len(correlation.columns)))
    ax.set_yticks(range(len(correlation.index)))

    ax.set_xticklabels(
        correlation.columns,
        rotation=90,
        fontsize=7
    )

    ax.set_yticklabels(
        correlation.index,
        fontsize=7
    )

    ax.set_title(title)

    fig.colorbar(image, ax=ax, label="Correlation")

    fig.tight_layout()

    fig.savefig(filename, dpi=150)
    plt.close(fig)


def run_cross_zone_analysis(
    dataset_path=DATASET,
    output_dir=OUTPUT,
    grid_degrees=10,
    min_periods=3
):
    """Execute the complete cross-zone analysis."""

    dataset_path = Path(dataset_path)
    output_dir = Path(output_dir)

    if not dataset_path.exists():
        raise FileNotFoundError(dataset_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(dataset_path)

    print("\nATMO SYNC CROSS-ZONE ANALYSIS")
    print("=" * 55)

    print("Original records:", len(raw))

    climate = prepare_climate_data(
        raw,
        grid_degrees=grid_degrees
    )

    print("Valid climate records:", len(climate))
    print("Geographic zones:", climate["zone_id"].nunique())

    weekly = aggregate_weekly_climate(climate)

    weekly.to_csv(
        output_dir / "weekly_zone_climate.csv",
        index=False
    )

    results = {
        "climate": climate,
        "weekly": weekly,
        "correlations": {}
    }

    for metric in [
        "temperature_mean",
        "humidity_mean"
    ]:

        for method in [
            "pearson",
            "spearman"
        ]:

            pivot, correlation = calculate_zone_correlations(
                weekly,
                metric,
                method=method,
                min_periods=min_periods
            )

            name = f"{metric}_{method}"

            correlation.to_csv(
                output_dir / f"{name}.csv"
            )

            save_heatmap(
                correlation,
                output_dir / f"{name}_heatmap.png",
                f"{metric} - {method.title()} correlation"
            )

            results["correlations"][name] = correlation

            print(f"\n{name}")
            print(correlation)

    print("\nAnalysis completed.")
    print("Output directory:", output_dir)

    return results


if __name__ == "__main__":
    run_cross_zone_analysis()
