# Read-Only Research Dashboard — Phase 5

## Purpose and status

The Streamlit application displays **only aggregated metrics from a local evaluation report**. It is not a real-time IDS, does not probe or capture network traffic, does not load serialized model objects, and does not upload or show raw flow records.

A real-data benchmark has now been run using the designated UNSW-NB15 train/test CSVs downloaded via the university-hosted SharePoint/OneDrive link on the [official UNSW Research page](https://research.unsw.edu.au/projects/unsw-nb15-dataset). The dashboard also has separate synthetic software tests. Previously recorded aggregate results are published under [docs/results/](results/README.md); this UI does not collect live network traffic.

## Installation and start

```bash
python -m venv .venv
# Activate the virtual environment. Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
streamlit run app/streamlit_app.py
```

By default, it reads `artifacts/reports/evaluation.json` from the repository root. When that file is missing, the dashboard **shows setup instructions rather than fabricated example scores**. The screenshot-ready view appears only after a local `nids evaluate` run creates the report.

### Running an authorized experiment before viewing it

1. Obtain the two designated CSV files directly from the [official UNSW-NB15 dataset page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) under its published research terms; do not redistribute the files in the repository.
2. Follow the official webpage's link to the university-hosted SharePoint/OneDrive repository. The loader checks CSV structure but does not perform a reference-checksum comparison.
3. Put the files in `data/raw/` (ignored by Git), and use the CLI:

```bash
nids inspect-data --data-dir data/raw
nids evaluate --data-dir data/raw --output-dir artifacts/reports --seed 42 --trees 100
streamlit run app/streamlit_app.py
```

To display reports in another local folder, set the environment variable before launching Streamlit:

```bash
# Windows PowerShell
$env:NIDS_REPORT_DIR="C:\path\to\local\aggregate-reports"
streamlit run app/streamlit_app.py
```

## What the interface displays

| Tab | Research outputs | Scope |
| --- | --- | --- |
| Overview | Selected classifier and attack-class precision/recall/F1 | Selected model's held-out test scores |
| Validation comparison | Both baseline classifiers' precision/recall/F1 and ROC-AUC | **Validation split only**; model selection uses validation attack F1 |
| Held-out test | FPR, FNR, ROC-AUC, class balance and confusion matrix | **Selected model only**; positive class is attack (`1`) |
| Protocol & limitations | Selection and provenance caveats | Methodological, not deployment claims |

Metrics and the confusion matrix come from the JSON report. The optional ROC plot is displayed only when its timestamp is at least as recent as the JSON report and AUC is defined; when not available, the interface shows the numerical metric without inventing a curve. Undefined values appear as **N/A**, never `0%`.

## Security and integrity decisions

- Only one fixed filename, `evaluation.json`, is parsed; the report size is limited to 2 MiB. JSON is **not** executable code.
- The schema and internal counts are checked before displaying results: both validation models must be present, selection must match the validation attack F1, and confusion counts, class supports, sample counts and defined rates must agree.
- No pickle or joblib files are loaded. No upload widgets, sockets, packet sniffing, shell commands, or live scanners are present.
- Raw samples, credentials and private network details must never be submitted to a publicly accessible Streamlit deployment. **Keep the dashboard local** unless a separate privacy and deployment review is completed.
- A blue informational notice documents the official UNSW Research webpage and its institutional SharePoint/OneDrive download path. SHA-256 hashes identify the *local copies* used, but the dashboard cannot compare them with a publisher-issued reference checksum unless one is supplied. The note is not an error or a claim of third-party origin.
- The test output is for **one selected model**, not a final test-set competition between models. Reusing the test to choose new hyperparameters compromises the research protocol.

## Validation and testing

The dashboard's pure-Python loader is covered by synthetic tests checking valid reports, missing/corrupt/oversized JSON, inconsistent metrics, mismatched model-selection metadata and unavailable ROC-AUC. Separate test doubles exercise the Streamlit **empty-state** and **results-rendering** code paths without requiring a server. Actual browser UI verification depends on installing Streamlit in a local environment; a fake framework alone cannot establish browser rendering or compatibility.

## References

- [Streamlit documentation](https://docs.streamlit.io/)
- [scikit-learn: model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [UNSW-NB15 official research dataset](https://research.unsw.edu.au/projects/unsw-nb15-dataset)
