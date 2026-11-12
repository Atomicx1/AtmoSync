import pandas as pd
from pathlib import Path

datasets = [
    "avocado.csv",
    "smart_logistics_dataset.csv"
]

for file in datasets:

    print("\n" + "=" * 60)
    print("DATASET:", file)
    print("=" * 60)

    path = Path(file)

    if not path.exists():
        print("Dataset not found!")
        continue

    df = pd.read_csv(path)

    print("\nDataset Shape:", df.shape)
    print("\nColumns:", df.columns.tolist())
    print("\nFirst 5 Records:")
    print(df.head())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Records:")
    print(df.duplicated().sum())

    print("\nStatistical Summary:")
    print(df.describe(include="all"))