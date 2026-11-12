
from pathlib import Path
import pandas as pd
from src.analytics import eda


def test_eda_with_sample_data(tmp_path, monkeypatch):
    monkeypatch.setattr(eda, "ROOT", tmp_path)
    monkeypatch.setattr(eda, "OUTPUT", tmp_path / "reports")

    sample = pd.DataFrame({
        "temperature_c": [20, 22, 24, 26],
        "humidity_percent": [60, 65, 70, 75],
        "zone": ["A", "A", "B", "B"]
    })

    sample.to_csv(tmp_path / "sample.csv", index=False)

    result = eda.analyze_dataset("sample.csv")

    assert len(result) == 3
    assert (tmp_path / "reports" / "sample" / "quality.csv").exists()
    assert (tmp_path / "reports" / "sample" / "correlation.csv").exists()
    assert (tmp_path / "reports" / "sample" / "correlation_heatmap.png").exists()
