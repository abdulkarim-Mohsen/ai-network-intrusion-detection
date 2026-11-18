# Reproducibility Guide and Evidence Checklist

## Status and system boundary

An actual offline benchmark was conducted on 2026-11-18 (UTC) using UNSW-NB15 CSVs downloaded through the official UNSW dataset webpage's university-hosted SharePoint/OneDrive link. Raw CSVs are not in GitHub; aggregate outputs are in [results/](results/README.md). Software tests are distinct from independent scientific replication.

## 1. Prepare an isolated environment

Use **Python 3.11 or 3.12** (the versions exercised by CI); from the repository root:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
python -m pytest -q --cov=nids --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=90
python scripts/check_repo_hygiene.py --root .
```

This software uses **bounded dependency ranges, not an exact lockfile**. Record a snapshot of installed package versions when making research claims:

```bash
python --version
python -m pip freeze > environment-versions.txt
```

Do **not** commit `environment-versions.txt` if it contains sensitive local package source URLs or credentials. Inspect it first.

## 2. Source and verify the academic dataset

Open the [UNSW source](https://research.unsw.edu.au/projects/unsw-nb15-dataset); follow its official download location and current academic-use/attribution conditions. Obtain only these two pre-partitioned files, and place them **locally**:

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
```

Follow the [official UNSW-NB15 dataset page](https://research.unsw.edu.au/projects/unsw-nb15-dataset)'s university-hosted repository link, not an arbitrary mirror. Keep the source URL/date and local SHA-256 digests. A hash identifies the local copy, and a publisher-issued reference digest (if provided) enables an additional byte-for-byte comparison. Do not merge official partitions or commit the original CSVs.

## 3. Execute the *actual* offline experiment

```bash
nids status
nids inspect-data --data-dir data/raw
nids train --data-dir data/raw --output-dir artifacts/models --seed 42 --validation-fraction 0.2 --trees 100 --max-iter 1000
nids evaluate --data-dir data/raw --output-dir artifacts/reports --seed 42 --validation-fraction 0.2 --trees 100 --max-iter 1000
streamlit run app/streamlit_app.py
```

Commands use no live network detection or scanning. The evaluation command **refits** its own baselines; it does not read joblib models created by `train`. Do not interpret the resulting test score as independent evidence if parameters were modified after seeing test outcomes.

### Optional: create a consistency-checked academic summary

After the `nids evaluate` command has produced `evaluation.json` from official-link UNSW dataset copies, run:

```bash
python -m scripts.render_evaluation_summary --input artifacts/reports/evaluation.json --output artifacts/reports/benchmark_summary.md
```

This checks whether each confusion matrix and derived binary metrics agree before rendering *only those observed aggregate results*. The report documents the official-link provenance and the limits of local checksums. See [benchmark execution steps](benchmark_execution.md).

## 4. Keep local evidence, not GitHub datasets

| Local output | What it establishes | Limitation |
| --- | --- | --- |
| `artifacts/models/training_manifest.json` | Training settings, version metadata, class counts, SHA-256 input-file digests | Not predictive accuracy; hashes identify copies but are not publisher reference digests |
| `artifacts/models/*.joblib` | Trusted, locally trained serialized models | Never load untrusted models; not distributed |
| `artifacts/reports/evaluation.json` | Validation metrics for both candidates, winner and held-out metrics for chosen model | Depends on consistent local copies and documented official source |
| `artifacts/reports/confusion_matrix.png` | Aggregate held-out TP/FP/TN/FN chart | Does not demonstrate deployment effectiveness |
| `artifacts/reports/roc_curve.png` | ROC plot, only when both true classes are present | ROC-AUC can be undefined for a single-class partition |

All generated models and report files are deliberately Git-ignored. Do not publish source CSVs, row-level predictions, network addresses or credential material.

## 5. Complete the research manuscript **after** verification

The published local experiment has been completed once; for *independent verification* of this result:

1. Record the date, commit SHA, official source URL, access conditions, real row counts and class distributions.
2. Preserve the CLI command lines, package version snapshot and SHA-256 source digests.
3. Copy the actual aggregate metric values from `evaluation.json`; confirm the confusion matrix sums to the reported held-out sample count.
4. State which model won on **validation attack F1** and clearly distinguish validation comparisons from **the chosen model's single final test score**.
5. Explain false-positive and false-negative operational implications, class imbalance, label provenance, and realistic external-validity limitations.
6. Cross-check the already recorded metrics in [results_reporting_template.md](results_reporting_template.md) with the [measured evaluation JSON](results/evaluation.json) and [research report](research_report.md). Do not fabricate or extrapolate results.
7. Keep any citations required by UNSW; see [references.md](references.md).

## 6. Known reproducibility limitations

A seed improves repeatability but does not guarantee bit-for-bit equality across Python, operating systems or changing library versions. The project currently does not publish a fully locked environment, repeated randomized trials, calibrated thresholds, confidence intervals, or an external deployment benchmark. A result on one fixed provider split must be framed accordingly.
