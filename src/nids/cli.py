"""CLI entry point; status does not access live networks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from nids.config import ProjectPaths, get_project_paths
from nids.data.load import dataset_summary, load_official_split
from nids.models.train import TrainingConfig, train_from_directory
from nids.models.evaluate import evaluate_from_directory


def _has_files(folder: Path, suffixes: tuple[str, ...]) -> bool:
    """Check only direct children; avoid recursive traversal of datasets."""
    return folder.is_dir() and any(
        p.is_file() and p.suffix.lower() in suffixes for p in folder.iterdir()
    )


def project_status(paths: ProjectPaths) -> dict[str, object]:
    """Report local artifact presence; never claim model validity."""
    return {
        "phase": 5,
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
    inspector = subs.add_parser("inspect-data", help="Validate and summarize official local UNSW-NB15 CSVs")
    inspector.add_argument("--data-dir", type=Path, default=None, help="Folder with official training/testing CSVs")
    trainer = subs.add_parser("train", help="Train two baselines offline on the official training split")
    trainer.add_argument("--data-dir", type=Path, default=None, help="Directory containing official CSVs")
    trainer.add_argument("--output-dir", type=Path, default=None, help="Local folder for trained models")
    trainer.add_argument("--seed", type=int, default=42)
    trainer.add_argument("--validation-fraction", type=float, default=0.2)
    trainer.add_argument("--trees", type=int, default=100, help="Number of Random Forest trees")
    trainer.add_argument("--max-iter", type=int, default=1000, help="Logistic Regression max iterations")
    evaluator = subs.add_parser(
        "evaluate", help="Offline validation selection and held-out evaluation"
    )
    evaluator.add_argument("--data-dir", type=Path, default=None)
    evaluator.add_argument("--output-dir", type=Path, default=None)
    evaluator.add_argument("--seed", type=int, default=42)
    evaluator.add_argument("--validation-fraction", type=float, default=0.2)
    evaluator.add_argument("--trees", type=int, default=100)
    evaluator.add_argument("--max-iter", type=int, default=1000)
    evaluator.add_argument("--no-plots", action="store_true", help="Skip PNG figures")
    args = parser.parse_args(argv)
    if args.command == "status":
        print(json.dumps(project_status(get_project_paths()), indent=2))
        return 0
    if args.command == "inspect-data":
        directory = args.data_dir if args.data_dir is not None else get_project_paths().raw_data
        print(json.dumps(dataset_summary(load_official_split(directory)), indent=2))
        return 0
    if args.command == "train":
        paths = get_project_paths()
        config = TrainingConfig(
            seed=args.seed,
            validation_fraction=args.validation_fraction,
            forest_trees=args.trees,
            logistic_max_iter=args.max_iter,
        )
        output = train_from_directory(
            args.data_dir if args.data_dir is not None else paths.raw_data,
            args.output_dir if args.output_dir is not None else paths.models,
            config,
        )
        print(json.dumps(output, indent=2))
        return 0
    if args.command == "evaluate":
        paths = get_project_paths()
        config = TrainingConfig(
            seed=args.seed,
            validation_fraction=args.validation_fraction,
            forest_trees=args.trees,
            logistic_max_iter=args.max_iter,
        )
        result = evaluate_from_directory(
            args.data_dir if args.data_dir is not None else paths.raw_data,
            args.output_dir if args.output_dir is not None else paths.reports,
            config,
            make_plots=not args.no_plots,
        )
        print(json.dumps(result, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
