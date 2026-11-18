"""Safely summarize an *existing* offline evaluation report as academic Markdown.

This tool neither downloads datasets nor trains models. It validates aggregate
metric arithmetic before displaying supplied figures and explicitly keeps
source provenance separate from computing a local SHA-256 checksum.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


class InvalidEvaluation(ValueError):
    """Report has inconsistent metrics or an unsupported schema."""


def _integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise InvalidEvaluation(f"{label} must be a nonnegative integer")
    return value


def _probability(value: object, label: str, *, nullable: bool = False) -> float | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidEvaluation(f"{label} must be a finite number between 0 and 1")
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise InvalidEvaluation(f"{label} must be between 0 and 1")
    return value


def _close(actual: float | None, expected: float | None, label: str) -> None:
    if (actual is None) != (expected is None):
        raise InvalidEvaluation(f"{label} inconsistent with confusion matrix")
    if actual is not None and expected is not None and not math.isclose(
        actual, expected, rel_tol=0, abs_tol=1e-9
    ):
        raise InvalidEvaluation(f"{label} inconsistent with confusion matrix")


def _metric_section(section: object, label: str) -> dict[str, object]:
    if not isinstance(section, dict):
        raise InvalidEvaluation(f"{label} must be an object")
    try:
        matrix = section["confusion_matrix"]
        if not isinstance(matrix, list) or len(matrix) != 2 or any(
            not isinstance(row, list) or len(row) != 2 for row in matrix
        ):
            raise InvalidEvaluation(f"{label}: confusion matrix must be 2 by 2")
        tn, fp = (_integer(x, f"{label} confusion matrix") for x in matrix[0])
        fn, tp = (_integer(x, f"{label} confusion matrix") for x in matrix[1])
        n = _integer(section["sample_count"], f"{label} sample count")
        if n == 0 or n != tn + fp + fn + tp:
            raise InvalidEvaluation(f"{label}: confusion-matrix total differs from sample count")
        for key, val in {
            "true_negatives": tn, "false_positives": fp,
            "false_negatives": fn, "true_positives": tp,
        }.items():
            if _integer(section[key], f"{label} {key}") != val:
                raise InvalidEvaluation(f"{label}: {key} disagrees with confusion matrix")
        counts = section["class_counts"]
        if not isinstance(counts, dict) or counts.get("0") != tn + fp or counts.get("1") != fn + tp:
            raise InvalidEvaluation(f"{label}: class counts disagree with confusion matrix")
        attack = section["per_class"]["1"]
        if attack["support"] != fn + tp:
            raise InvalidEvaluation(f"{label}: attack support disagrees with confusion matrix")
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        for key, computed in (("precision", precision), ("recall", recall), ("f1", f1)):
            _close(_probability(attack[key], f"{label} {key}"), computed, f"{label} {key}")
        _close(_probability(section["accuracy"], f"{label} accuracy"), (tn + tp) / n, f"{label} accuracy")
        fpr = fp / (fp + tn) if fp + tn else None
        fnr = fn / (fn + tp) if fn + tp else None
        _close(_probability(section["false_positive_rate"], f"{label} FPR", nullable=True), fpr, f"{label} FPR")
        _close(_probability(section["false_negative_rate"], f"{label} FNR", nullable=True), fnr, f"{label} FNR")
        auc = _probability(section.get("roc_auc"), f"{label} ROC-AUC", nullable=True)
        if auc is not None and (tn + fp == 0 or tp + fn == 0):
            raise InvalidEvaluation(f"{label}: ROC-AUC is undefined for a single-class sample")
        return {
            "n": n, "tn": tn, "fp": fp, "fn": fn, "tp": tp,
            "precision": precision, "recall": recall, "f1": f1,
            "accuracy": (tn + tp) / n, "fpr": fpr, "fnr": fnr, "auc": auc,
        }
    except (KeyError, TypeError, IndexError, AttributeError) as exc:
        raise InvalidEvaluation(f"{label}: missing or malformed metric fields: {exc}") from exc


def validate_report(report: object) -> dict[str, object]:
    """Check evaluation status, selection protocol and metric arithmetic."""
    if not isinstance(report, dict) or report.get("status") != "evaluation_completed":
        raise InvalidEvaluation("Expected an evaluation_completed aggregate report")
    validation = report.get("validation")
    if not isinstance(validation, dict) or set(validation) != {"logistic_regression", "random_forest"}:
        raise InvalidEvaluation("Validation must contain both documented baseline models")
    metrics = {name: _metric_section(entry, f"validation {name}") for name, entry in validation.items()}
    winner = max(("logistic_regression", "random_forest"), key=lambda name: metrics[name]["f1"])
    selected = report.get("selected_model")
    if selected != winner:
        raise InvalidEvaluation("Selected model conflicts with validation attack-F1 rule")
    selection = report.get("selection_protocol")
    if not isinstance(selection, dict) or selection.get("test_models_evaluated") != [selected]:
        raise InvalidEvaluation("Held-out test must evaluate only the selected model")
    test = _metric_section(report.get("official_test_selected_model"), "held-out test")
    if test["n"] == 0:
        raise InvalidEvaluation("Held-out test cannot be empty")
    hashes = report.get("source_files_sha256")
    if not isinstance(hashes, dict) or not all(
        isinstance(hashes.get(name), str)
        and len(hashes[name]) == 64
        and all(c in "0123456789abcdef" for c in hashes[name].lower())
        for name in ("UNSW_NB15_training-set.csv", "UNSW_NB15_testing-set.csv")
    ):
        raise InvalidEvaluation("Missing SHA-256 source-file digests; use nids evaluate on local CSVs")
    return {"validation": metrics, "selected": selected, "test": test, "hashes": hashes}


def _fmt(value: object) -> str:
    if value is None:
        return "Undefined (no positive/negative denominator or single-class split)"
    return f"{float(value):.4f}"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render only aggregate metrics already present in a consistent local report."""
    checked = validate_report(report)
    validation = checked["validation"]
    selected = checked["selected"]
    heldout = checked["test"]
    hashes = checked["hashes"]
    assert isinstance(validation, dict) and isinstance(heldout, dict) and isinstance(hashes, dict)
    lines = [
        "# Locally Measured Network Intrusion Detection Baseline Results",
        "",
        "> **Provenance warning:** These numbers were imported from a local JSON file. ",
        "> This generator checks arithmetic and selection rules, **not** whether ",
        "> the CSVs originated from UNSW or whether the experiment was independently replicated.",
        "> Verify the original source and file contents before reporting these as official UNSW-NB15 findings.",
        "",
        "## Method and model selection",
        "",
        "Validation attack F1 determines the selected baseline. The provider-designated test split is used only for the selected model.",
        "",
        "| Validation metric | Logistic Regression | Random Forest |",
        "| --- | ---: | ---: |",
    ]
    a = validation["logistic_regression"]
    b = validation["random_forest"]
    for key, title in [("n", "Validation observations"), ("precision", "Attack precision"),
                       ("recall", "Attack recall"), ("f1", "Attack F1"),
                       ("auc", "ROC-AUC"), ("fpr", "False-positive rate")]:
        lines.append(f"| {title} | {a[key] if key == 'n' else _fmt(a[key])} | {b[key] if key == 'n' else _fmt(b[key])} |")
    lines.extend([
        "", f"**Validation-selected model:** `{selected}`", "",
        "## Held-out test — selected model only", "",
        "| Metric | Observed |", "| --- | ---: |",
    ])
    for key, title in [("n", "Test observations"), ("tn", "True negatives"),
                       ("fp", "False positives"), ("fn", "False negatives"),
                       ("tp", "True positives"), ("accuracy", "Accuracy"),
                       ("precision", "Attack precision"), ("recall", "Attack recall"),
                       ("f1", "Attack F1"), ("fpr", "False-positive rate"),
                       ("fnr", "False-negative rate"), ("auc", "ROC-AUC")]:
        value = heldout[key]
        lines.append(f"| {title} | {value if key in {'n', 'tn', 'fp', 'fn', 'tp'} else _fmt(value)} |")
    lines.extend([
        "", "## Input-file provenance evidence", "",
        "The following SHA-256 values identify the **local bytes** and do not independently authenticate their source:", "",
    ])
    for name, digest in hashes.items():
        lines.append(f"- `{name}`: `{digest}`")
    lines.extend([
        "", "## Scientific limitations", "",
        "- Positive class: `label=1` (attack); negative class: `label=0` (normal).",
        "- Dataset authenticity and permitted use must be confirmed against the UNSW official page.",
        "- Results from a static research benchmark do not establish real-world deployment performance.",
        "- This report is a generated summary, **not** a peer-reviewed publication or independent replication.",
        "- Do not change model parameters after seeing these held-out results and present the same test split as unbiased.",
        "",
    ])
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a verified-arithmetic academic summary from local NIDS evaluation.json")
    parser.add_argument("--input", type=Path, default=Path("artifacts/reports/evaluation.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/reports/benchmark_summary.md"))
    args = parser.parse_args(argv)
    try:
        with args.input.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        rendered = render_markdown(payload)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".tmp", dir=args.output.parent, delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(rendered)
            os.replace(temporary, args.output)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        print(f"Local report created: {args.output}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Cannot generate summary: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
