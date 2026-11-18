"""Path configuration for local, offline research artifacts."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Project paths; no directory is created as a side effect."""

    root: Path

    @property
    def raw_data(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def processed_data(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def models(self) -> Path:
        return self.root / "artifacts" / "models"

    @property
    def reports(self) -> Path:
        return self.root / "artifacts" / "reports"


def get_project_paths() -> ProjectPaths:
    """Resolve project root from environment or this source checkout."""
    configured = os.getenv("NIDS_PROJECT_ROOT")
    root = Path(configured).expanduser() if configured else Path(__file__).resolve().parents[2]
    return ProjectPaths(root=root.resolve())
