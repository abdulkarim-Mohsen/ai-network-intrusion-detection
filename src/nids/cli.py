"""CLI entry point; status does not access live networks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from nids.config import ProjectPaths, get_project_paths


def _has_files(folder: Path, suffixes: tuple[str, ...]) -> bool:
    """Check only direct children; avoid recursive traversal of datasets."""
    return folder.is_dir() and any(
        p.is_file() and p.suffix.lower() in suffixes for p in folder.iterdir()
    )


def project_status(paths: ProjectPaths) -> dict[str, object]:
    """Report local artifact presence; never claim model validity."""
    return {
        "phase": 1,
        "project_root": str(paths.root),
        "dataset_files_present": _has_files(paths.raw_data, (".csv", ".parquet")),
        "trained_model_files_present": _has_files(paths.models, (".joblib", ".pkl")),
        "evaluation_files_present": _has_files(paths.reports, (".json",)),
        "model_training_completed_by_this_command": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline NIDS research utilities")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("status", help="Report presence of local research artifacts")
    args = parser.parse_args(argv)
    if args.command == "status":
        print(json.dumps(project_status(get_project_paths()), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
