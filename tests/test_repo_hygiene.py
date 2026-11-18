"""Defensive release-policy tests, without real traffic or secrets."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.check_repo_hygiene import check_tracked_paths, list_tracked_files, main


@pytest.mark.parametrize("item", [
    "data/raw/network.csv",
    "data/processed/flows.parquet",
    "artifacts/models/random_forest.joblib",
    "artifacts/reports/evaluation.json",
    "data/raw/folder/.gitkeep",
    ".env",
    ".env.production",
    "config/api.key",
    "keys/id_rsa",
    ".streamlit/secrets.toml",
    "experiments/phase5_git_payload.json",
    "src/nids/__pycache__/module.pyc",
    "notes/../private.pem",
])
def test_private_and_generated_paths_are_rejected(item):
    assert check_tracked_paths([item]) == [item]


@pytest.mark.parametrize("item", [
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
    "artifacts/models/.gitkeep",
    "artifacts/reports/.gitkeep",
    "src/nids/models/train.py",
    "tests/test_repo_hygiene.py",
    "docs/research_report.md",
    ".env.example",
    ".gitignore",
])
def test_safe_source_and_placeholder_paths_are_allowed(item):
    assert check_tracked_paths([item]) == []


def test_scanner_returns_all_offending_paths():
    assert check_tracked_paths(["README.md", "data/raw/secret.csv", ".env"]) == [
        "data/raw/secret.csv", ".env"
    ]


def test_cli_detects_forcibly_staged_raw_data(tmp_path, capsys):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "private.csv").write_text("synthetic-test-header\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "data/raw/private.csv"], check=True)
    assert main(["--root", str(tmp_path)]) == 1
    assert "data/raw/private.csv" in capsys.readouterr().err


def test_cli_passes_only_safe_tracked_files(tmp_path, capsys):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "README.md").write_text("# Sample\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README.md"], check=True)
    assert list_tracked_files(tmp_path) == ["README.md"]
    assert main(["--root", str(tmp_path)]) == 0
    assert "passed" in capsys.readouterr().out


def test_no_git_index_is_reported_as_error(tmp_path, capsys):
    assert main(["--root", str(tmp_path)]) == 2
    assert "Could not list" in capsys.readouterr().err
