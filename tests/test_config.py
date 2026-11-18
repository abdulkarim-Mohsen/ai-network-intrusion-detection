"""Phase 1 configuration tests."""

from pathlib import Path

from nids.config import get_project_paths


def test_default_root_resolves_to_checkout(monkeypatch):
    monkeypatch.delenv("NIDS_PROJECT_ROOT", raising=False)
    paths = get_project_paths()
    assert (paths.root / "README.md").is_file()
    assert paths.models == paths.root / "artifacts" / "models"


def test_root_override(monkeypatch, tmp_path):
    monkeypatch.setenv("NIDS_PROJECT_ROOT", str(tmp_path))
    paths = get_project_paths()
    assert paths.root == Path(tmp_path).resolve()
    assert paths.processed_data == tmp_path / "data" / "processed"
