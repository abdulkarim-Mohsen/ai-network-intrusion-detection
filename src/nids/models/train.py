"""Reproducible offline baseline training for official UNSW-NB15 partitions.

Only the official training split (further divided into fit/validation) is used
for fitting. The provider's official test set is NEVER passed to model.fit().
Model artifacts are local only; never load untrusted joblib files.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from nids.data.load import (
    TEST_FILENAME,
    TRAIN_FILENAME,
    OfficialDataset,
    load_official_split,
)
from nids.features.preprocess import (
    DEFAULT_SEED,
    DataPartitions,
    build_preprocessor,
    partition_data,
)


@dataclass(frozen=True)
class TrainingConfig:
    """Baseline settings that are written to the reproducibility manifest."""

    seed: int = DEFAULT_SEED
    validation_fraction: float = 0.2
    logistic_max_iter: int = 1000
    forest_trees: int = 100

    def __post_init__(self) -> None:
        if not 0 < self.validation_fraction < 1:
            raise ValueError("validation_fraction must be strictly between 0 and 1")
        if self.logistic_max_iter <= 0 or self.forest_trees <= 0:
            raise ValueError("logistic_max_iter and forest_trees must be positive")
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError("seed must be a nonnegative integer")


@dataclass(frozen=True)
class TrainingRun:
    """In-memory fitted pipelines and non-sensitive experiment manifest."""

    models: Mapping[str, Pipeline]
    manifest: dict[str, object]


def _class_counts(labels: pd.Series) -> dict[str, int]:
    return {str(key): int(value) for key, value in labels.value_counts().sort_index().items()}


def _train_partitions(parts: DataPartitions, config: TrainingConfig) -> TrainingRun:
    """Fit each model on X_train only; no validation/test transforms are fitted."""
    if parts.y_train.nunique() != 2:
        raise ValueError("At least two classes are required to train a classifier")
    if len(parts.X_train) != len(parts.y_train):
        raise ValueError("Training features and labels have different row counts")
    if parts.y_valid.nunique() != 2:
        raise ValueError("Validation split must contain both classes")

    estimators = {
        "logistic_regression": LogisticRegression(
            solver="lbfgs",
            max_iter=config.logistic_max_iter,
            class_weight="balanced",
            random_state=config.seed,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=config.forest_trees,
            max_depth=18,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=config.seed,
            n_jobs=1,
        ),
    }
    fitted: dict[str, Pipeline] = {}
    for name, estimator in estimators.items():
        # Every estimator receives a *different* initially unfitted transformer.
        pipeline = Pipeline(
            steps=[
                ("preprocess", build_preprocessor(parts.features)),
                ("classifier", estimator),
            ]
        )
        pipeline.fit(parts.X_train, parts.y_train)
        fitted[name] = pipeline

    manifest: dict[str, object] = {
        "stage": "phase3_training",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": "label",
        "positive_class": 1,
        "dataset": "UNSW-NB15 (provider-defined training/testing CSV partitions)",
        "training_config": asdict(config),
        "training_rows": int(len(parts.X_train)),
        "validation_rows": int(len(parts.X_valid)),
        "official_test_rows": int(len(parts.X_test)),
        "training_label_counts": _class_counts(parts.y_train),
        "validation_label_counts": _class_counts(parts.y_valid),
        "feature_names": list(parts.features),
        "excluded_features": ["id", "attack_cat", "label"],
        "models": {
            name: {"classifier": type(pipeline.named_steps["classifier"]).__name__,
                   "parameters": pipeline.named_steps["classifier"].get_params()}
            for name, pipeline in fitted.items()
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
        },
        "official_test_used_in_training": False,
        "validation_used_in_training": False,
        "held_out_evaluation_performed": False,
        "validation_metrics_computed": False,
        "measured_model_performance": None,
        "status": "fitted_models_without_evaluation",
    }
    return TrainingRun(models=fitted, manifest=manifest)


def train_baselines(dataset: OfficialDataset, config: TrainingConfig = TrainingConfig()) -> TrainingRun:
    """Fit Logistic Regression and Random Forest, without reading the test labels.

    The split and preprocessor are provided by Phase 2 and both baselines use
    identical partitions. The returned pipelines are fitted but *not evaluated*.
    """
    partitions = partition_data(
        dataset, seed=config.seed, validation_fraction=config.validation_fraction
    )
    return _train_partitions(partitions, config)


def sha256_file(path: str | Path) -> str:
    """Stream a local dataset file to record exactly which bytes were used."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomically(path: Path, payload: dict[str, object]) -> None:
    """Avoid exposing a partially written manifest if the process is stopped."""
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, suffix=".json.tmp", delete=False
        ) as temp:
            tmp_path = Path(temp.name)
            json.dump(payload, temp, indent=2, ensure_ascii=False, allow_nan=False)
            temp.write("\n")
        os.replace(tmp_path, path)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def save_training_run(run: TrainingRun, output_dir: str | Path) -> dict[str, str]:
    """Write *trusted local* joblib pipelines and a JSON manifest.

    These binaries must not be committed or loaded from unknown third parties.
    Avoid writing predictions, traffic records, or private data to GitHub.
    """
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for name, pipeline in run.models.items():
        if name not in {"logistic_regression", "random_forest"}:
            raise ValueError("Unsupported model artifact name")
        destination = output / f"{name}.joblib"
        with tempfile.NamedTemporaryFile(dir=output, suffix=".joblib.tmp", delete=False) as f:
            temp_path = Path(f.name)
        try:
            joblib.dump(pipeline, temp_path)
            os.replace(temp_path, destination)
        finally:
            temp_path.unlink(missing_ok=True)
        written[name] = str(destination)
    manifest_path = output / "training_manifest.json"
    _write_json_atomically(manifest_path, run.manifest)
    written["manifest"] = str(manifest_path)
    return written


def train_from_directory(
    data_dir: str | Path,
    output_dir: str | Path,
    config: TrainingConfig = TrainingConfig(),
) -> dict[str, object]:
    """End-to-end *offline* training from locally provided official CSV files."""
    directory = Path(data_dir).expanduser().resolve()
    dataset = load_official_split(directory)
    run = train_baselines(dataset, config)
    run.manifest["source_files_sha256"] = {
        TRAIN_FILENAME: sha256_file(directory / TRAIN_FILENAME),
        TEST_FILENAME: sha256_file(directory / TEST_FILENAME),
    }
    written = save_training_run(run, output_dir)
    return {
        "status": "trained_no_evaluation",
        "model_paths": {key: value for key, value in written.items() if key != "manifest"},
        "manifest_path": written["manifest"],
        "official_test_used_in_training": False,
        "evaluated_on_official_test": False,
    }
