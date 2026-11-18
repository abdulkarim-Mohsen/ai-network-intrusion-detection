"""Offline, aggregate plots for held-out evaluation (no raw packet data)."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless CI / server operation
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay


def plot_confusion_matrix(matrix: np.ndarray, path: str | Path, *, title: str) -> None:
    """Save a confusion matrix; rows are true and columns predicted [0, 1]."""
    cm = np.asarray(matrix)
    if cm.shape != (2, 2) or not np.isfinite(cm).all():
        raise ValueError("Expected a finite 2x2 confusion matrix")
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    try:
        ConfusionMatrixDisplay(cm, display_labels=["normal (0)", "attack (1)"]).plot(
            ax=ax, values_format="d", cmap="Blues", colorbar=False
        )
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(Path(path), dpi=160, bbox_inches="tight")
    finally:
        plt.close(fig)


def plot_roc_curve(y_true, scores, path: str | Path, *, title: str) -> None:
    """Save ROC curve only when both binary classes are present."""
    truth = np.asarray(y_true)
    if set(np.unique(truth)) != {0, 1}:
        raise ValueError("ROC curve requires both classes")
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    try:
        RocCurveDisplay.from_predictions(truth, scores, pos_label=1, ax=ax)
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Chance")
        ax.set_title(title)
        ax.legend(loc="lower right")
        fig.tight_layout()
        fig.savefig(Path(path), dpi=160, bbox_inches="tight")
    finally:
        plt.close(fig)
