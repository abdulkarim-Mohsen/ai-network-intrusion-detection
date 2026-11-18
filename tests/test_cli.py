"""Phase 1 CLI contract tests; no network activity."""

import json

from nids.cli import main, project_status
from nids.config import ProjectPaths


def test_fresh_project_has_no_experiment_artifacts(tmp_path):
    status = project_status(ProjectPaths(tmp_path))
    assert status["phase"] == 2
    assert status["dataset_files_present"] is False
    assert status["trained_model_files_present"] is False
    assert status["evaluation_files_present"] is False
    assert status["model_training_completed_by_this_command"] is False


def test_status_detects_local_files_without_opening_them(tmp_path):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "academic.csv").write_text("", encoding="utf-8")
    model = tmp_path / "artifacts" / "models"
    model.mkdir(parents=True)
    (model / "test.joblib").write_text("not a model", encoding="utf-8")
    status = project_status(ProjectPaths(tmp_path))
    assert status["dataset_files_present"] is True
    assert status["trained_model_files_present"] is True
    assert status["model_training_completed_by_this_command"] is False


def test_cli_prints_parseable_status(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("NIDS_PROJECT_ROOT", str(tmp_path))
    assert main(["status"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["phase"] == 2
    assert printed["project_root"] == str(tmp_path)
