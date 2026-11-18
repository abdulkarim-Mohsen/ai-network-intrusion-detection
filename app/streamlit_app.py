"""Offline, read-only display of aggregate intrusion-detection evaluation.

This app does not train models, deserialize pickle/joblib, open sockets,
perform scanning or accept uploads of private flow data.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from nids.dashboard import DashboardReportError, load_dashboard_snapshot

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = Path(os.getenv("NIDS_REPORT_DIR", ROOT / "artifacts" / "reports")).expanduser().resolve()
MODEL_LABELS = {"logistic_regression": "Logistic Regression", "random_forest": "Random Forest"}


def percent(value: float | None) -> str:
    """Format absent/undefined metrics without implying a zero score."""
    return "N/A" if value is None else f"{value * 100:.2f}%"


def main() -> None:
    st.set_page_config(page_title="Network Intrusion Detection | Research", page_icon="🛡️", layout="wide")
    st.title("🛡️ Network Intrusion Detection — Research Dashboard")
    st.caption("Offline, read-only academic visualization · No live traffic monitoring or scanning")
    st.sidebar.header("Report source")
    st.sidebar.code(str(REPORT_DIR), language=None)
    st.sidebar.caption("To change this directory, set NIDS_REPORT_DIR before starting Streamlit.")

    try:
        snapshot = load_dashboard_snapshot(REPORT_DIR)
    except FileNotFoundError:
        st.info("No evaluation report found. No detection results are available to display.")
        st.markdown("**To generate an aggregate report from authorized, verified local research CSVs:**")
        st.code("nids inspect-data --data-dir data/raw\nnids evaluate --data-dir data/raw --output-dir artifacts/reports --seed 42 --trees 100", language="bash")
        st.warning("Never describe software-test results or unverified dataset files as UNSW-NB15 benchmarks.")
        return
    except DashboardReportError as exc:
        st.error(f"The local evaluation report is incomplete or invalid: {exc}")
        st.info("Re-run the offline evaluation into a clean reports folder; do not manually edit metric values.")
        return

    st.info(
        "**Dataset source:** UNSW-NB15 — University of New South Wales (UNSW). "
        "The research CSVs were obtained via the "
        "[official UNSW Research dataset page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) "
        "and its university-hosted SharePoint/OneDrive repository. "
        "The results displayed here are from the designated training and testing CSVs. "
        "File hashes identify the local copies; the dashboard does not perform an independent "
        "byte-for-byte comparison with a publisher-issued reference checksum."
    )
    st.caption(f"Evaluation file timestamp (UTC): {snapshot.generated_at}")
    st.caption("Input SHA-256 hashes recorded: " + ("yes (not proof of provenance)" if snapshot.hashes_recorded else "not available"))

    overview, comparison, held_out, protocol = st.tabs([
        "Overview", "Validation comparison", "Held-out test", "Protocol & limitations"
    ])

    with overview:
        st.subheader("Selected baseline and test summary")
        st.success(f"Selected on validation F1: {MODEL_LABELS[snapshot.selected_model]}")
        test = snapshot.selected_test
        a, b, c, d = st.columns(4)
        a.metric("Test samples", f"{snapshot.test_count:,}")
        b.metric("Attack recall", percent(test["recall_attack"]))
        c.metric("Attack precision", percent(test["precision_attack"]))
        d.metric("Attack F1", percent(test["f1_attack"]))
        st.caption("These are metrics from an existing local report, not live predictions. No data rows are displayed.")

    with comparison:
        st.subheader("Validation-only comparison of both models")
        frame = pd.DataFrame([
            {"Model": MODEL_LABELS[row["model"]], "Precision (attack)": row["precision_attack"],
             "Recall (attack)": row["recall_attack"], "F1 (attack)": row["f1_attack"],
             "ROC-AUC": row["roc_auc"], "Validation samples": row["sample_count"]}
            for row in snapshot.validation_rows
        ])
        st.dataframe(frame.round(3), use_container_width=True, hide_index=True)
        st.bar_chart(frame.set_index("Model")[["Precision (attack)", "Recall (attack)", "F1 (attack)"]])
        st.caption("Only validation data are used to choose the model. The other model is not evaluated on the held-out test split.")

    with held_out:
        st.subheader("Held-out test · selected model only")
        test = snapshot.selected_test
        a, b, c = st.columns(3)
        a.metric("False-positive rate", percent(test["false_positive_rate"]))
        b.metric("False-negative rate", percent(test["false_negative_rate"]))
        c.metric("ROC-AUC", percent(test["roc_auc"]))
        if test["roc_auc"] is None:
            st.info(snapshot.roc_auc_note or "ROC-AUC is not defined for this test split.")

        count1, count2 = st.columns(2)
        count1.metric("Normal flows", f"{snapshot.normal_count:,}")
        count2.metric("Attack flows", f"{snapshot.attack_count:,}")
        st.caption("Class balance matters: accuracy alone is insufficient for intrusion detection.")

        fig, ax = plt.subplots(figsize=(5.6, 4.2))
        matrix = snapshot.confusion_matrix
        im = ax.imshow(matrix, cmap="Blues")
        ax.set_xticks([0, 1], ["Normal", "Attack"])
        ax.set_yticks([0, 1], ["Normal", "Attack"])
        ax.set_xlabel("Predicted label")
        ax.set_ylabel("True label")
        ax.set_title("Confusion matrix · held-out test")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{matrix[i][j]:,}", ha="center", va="center",
                        color="white" if matrix[i][j] > max(max(row) for row in matrix) * 0.5 else "black")
        fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
        st.caption("Rows = true label, columns = predicted label. Positive class (attack) = 1.")

        roc_plot = REPORT_DIR / "roc_curve.png"
        report_json = REPORT_DIR / "evaluation.json"
        # Require a plot at least as recent as its JSON report to avoid showing
        # stale figures from an earlier run in a reused output directory.
        if test["roc_auc"] is not None and roc_plot.is_file() and 0 < roc_plot.stat().st_size < 10_000_000 and roc_plot.stat().st_mtime >= report_json.stat().st_mtime:
            st.image(str(roc_plot), caption="Local ROC figure from the current evaluation run")
        elif test["roc_auc"] is not None:
            st.caption("ROC-AUC is available numerically; no matching current-run ROC figure was found.")

    with protocol:
        st.subheader("Methods and research limitations")
        st.markdown(
            "- Preprocessing is fitted only on the designated training subset.\n"
            "- Both classifiers are compared using attack-class F1 on the validation subset.\n"
            "- Only the validation-selected classifier is evaluated on the official-designated test subset.\n"
            "- The data were downloaded via UNSW's official Research webpage and institutional SharePoint link. Local SHA-256 hashes identify copies, but are not publisher-reference checksums.\n"
            "- No model deserialization, packet capture, network probing or raw-row viewing occurs here.\n"
            "- Static academic samples do not demonstrate real-world detection reliability."
        )
        st.info("Use this dashboard for local aggregate research results. It is not a deployed IDS or an alarm console.")


if __name__ == "__main__":
    main()
