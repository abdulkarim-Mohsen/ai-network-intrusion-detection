"""Write a Markdown summary from an existing offline NIDS evaluation report.

Usage:
    python -m scripts.render_evaluation_summary \
        --input artifacts/reports/evaluation.json \
        --output artifacts/reports/benchmark_summary.md

Only the saved aggregate report is read; no model is trained or loaded.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nids.dashboard import DashboardReportError, build_dashboard_snapshot

MODEL_LABELS = {
    "logistic_regression": "Logistic Regression",
    "random_forest": "Random Forest",
}


def percent(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.2f}%"


def render_summary(report: dict) -> str:
    """Validate all reported metrics before formatting a summary."""
    snapshot = build_dashboard_snapshot(report)
    config = report.get("training_run", {}).get("training_config", {})
    run = report.get("training_run", {})
    selected = MODEL_LABELS[snapshot.selected_model]
    test = snapshot.selected_test
    matrix = snapshot.confusion_matrix
    (tn, fp), (fn, tp) = matrix

    rows = [
        "# Local Network Intrusion Detection — Evaluation Summary",
        "",
        f"**Evaluation time (UTC):** {snapshot.generated_at}",
        f"**Dataset description:** {report.get('dataset', 'Not recorded')}",
        f"**Selected model:** {selected}",
        f"**Train / validation / held-out test samples:** "
        f"{run.get('training_rows', 'N/A')} / {run.get('validation_rows', 'N/A')} / "
        f"{snapshot.test_count:,}",
        f"**Experiment settings:** seed={config.get('seed', 'N/A')}; "
        f"Random Forest trees={config.get('forest_trees', 'N/A')}; "
        f"Logistic Regression max_iter={config.get('logistic_max_iter', 'N/A')}",
        "",
        "## Validation comparison (selection by attack-class F1)",
        "",
        "| Metric | Logistic Regression | Random Forest |",
        "| --- | ---: | ---: |",
    ]
    keys = [
        ("Accuracy", "accuracy"),
        ("Attack precision", "precision_attack"),
        ("Attack recall", "recall_attack"),
        ("Attack F1", "f1_attack"),
        ("ROC-AUC", "roc_auc"),
        ("False positive rate", "false_positive_rate"),
    ]
    by_name = {row["model"]: row for row in snapshot.validation_rows}
    for label, field in keys:
        lr = percent(by_name["logistic_regression"][field])
        rf = percent(by_name["random_forest"][field])
        rows.append(f"| {label} | {lr} | {rf} |")

    rows.extend([
        "",
        f"**Validation winner:** {selected}",
        "",
        "## Held-out test (selected model only)",
        "",
        f"- **Test samples:** {snapshot.test_count:,}",
        f"- **Accuracy:** {percent(test['accuracy'])}",
        f"- **Attack precision:** {percent(test['precision_attack'])}",
        f"- **Attack recall:** {percent(test['recall_attack'])}",
        f"- **Attack F1:** {percent(test['f1_attack'])}",
        f"- **ROC-AUC:** {percent(test['roc_auc'])}",
        f"- **False positive rate:** {percent(test['false_positive_rate'])}",
        f"- **False negative rate:** {percent(test['false_negative_rate'])}",
        "",
        "### Confusion matrix (rows = actual, columns = predicted)",
        "",
        "| Actual | Predicted normal (0) | Predicted attack (1) |",
        "| --- | ---: | ---: |",
        f"| Normal (0) | {tn:,} (TN) | {fp:,} (FP) |",
        f"| Attack (1) | {fn:,} (FN) | {tp:,} (TP) |",
        "",
        "## Research limitations",
        "",
        "- The dashboard and this summary represent an offline academic evaluation, not live intrusion monitoring.",
        "- Local file names and SHA-256 fingerprints do not independently authenticate a dataset provider.",
        "- Potential repeated or correlated feature vectors across splits may affect generalization estimates.",
        "- Do not use held-out test results for further model selection without a new untouched test set.",
        "- Data use and provenance must be confirmed from the original provider.",
        "",
    ])
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a checked local NIDS evaluation JSON to Markdown"
    )
    parser.add_argument("--input", type=Path, required=True, help="Input evaluation.json")
    parser.add_argument("--output", type=Path, required=True, help="Output Markdown path")
    args = parser.parse_args(argv)
    source = args.input.expanduser().resolve()
    target = args.output.expanduser().resolve()
    if source == target:
        parser.error("Input and output must not be the same file")
    if target.suffix.lower() != ".md":
        parser.error("Output must have a .md extension")
    try:
        if source.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Report exceeds the dashboard's 2 MiB size limit")
        report = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError("Report must be a JSON object")
        markdown = render_summary(report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown, encoding="utf-8")
    except (OSError, UnicodeError, ValueError, TypeError, DashboardReportError) as exc:
        print(f"Cannot create summary: {exc}", file=sys.stderr)
        return 1
    print(f"Summary saved: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
