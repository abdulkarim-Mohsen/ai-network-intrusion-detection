"""The CLI validates local files without printing individual network records."""

import json

import pandas as pd

from nids.cli import main
from nids.data.load import TEST_FILENAME, TRAIN_FILENAME


def test_inspect_data_reports_aggregate_counts(tmp_path, capsys):
    sample = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "proto": ["tcp", "udp", "tcp", "udp"],
        "service": ["-", "dns", "-", "dns"],
        "state": ["FIN", "INT", "FIN", "INT"],
        "dur": [1, 2, 3, 4],
        "attack_cat": ["Normal", "Generic", "Normal", "Generic"],
        "label": [0, 1, 0, 1],
    })
    for filename in (TRAIN_FILENAME, TEST_FILENAME):
        sample.to_csv(tmp_path / filename, index=False)
    assert main(["inspect-data", "--data-dir", str(tmp_path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["official_train_rows"] == 4
    assert output["training_label_counts"] == {"0": 2, "1": 2}
    assert "tcp" not in json.dumps(output)
    assert output["any_model_trained"] is False
