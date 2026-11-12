
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "reports" / "eda"


def analyze_dataset(filename):
    path = ROOT / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")

    df = pd.read_csv(path)
    dataset_name = path.stem

    folder = OUTPUT / dataset_name
    folder.mkdir(parents=True, exist_ok=True)

    print(f"\nAnalyzing: {filename}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    # Missing values and data types
    quality = pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str).values,
        "missing_count": df.isna().sum().values,
        "missing_pct": df.isna().mean().values * 100
    })

    quality.to_csv(folder / "quality.csv", index=False)

    # Descriptive statistics
    summary = df.describe(include="all").transpose()
    summary.to_csv(folder / "statistics.csv")

    # Numeric correlation
    numeric = df.select_dtypes(include="number")

    if numeric.shape[1] >= 2:
        corr = numeric.corr()
        corr.to_csv(folder / "correlation.csv")

        fig, ax = plt.subplots(figsize=(10, 8))
        image = ax.imshow(
            corr.to_numpy(),
            cmap="coolwarm",
            vmin=-1,
            vmax=1
        )

        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))

        ax.set_xticklabels(
            corr.columns,
            rotation=90,
            fontsize=8
        )
        ax.set_yticklabels(corr.columns, fontsize=8)

        fig.colorbar(image, ax=ax)
        fig.tight_layout()
        fig.savefig(folder / "correlation_heatmap.png", dpi=150)
        plt.close(fig)

    # Numeric distributions
    for column in numeric.columns:
        values = numeric[column].dropna()

        if values.empty:
            continue

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(values, bins=30)
        ax.set_title(f"{dataset_name}: {column}")
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
        fig.tight_layout()

        safe_name = "".join(
            c if c.isalnum() or c == "_" else "_"
            for c in column
        )

        fig.savefig(
            folder / f"distribution_{safe_name}.png",
            dpi=150
        )
        plt.close(fig)

    print(f"EDA reports saved: {folder}")
    return quality


def main():
    for filename in [
        "avocado.csv",
        "smart_logistics_dataset.csv"
    ]:
        analyze_dataset(filename)


if __name__ == "__main__":
    main()
