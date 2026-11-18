# Research Protocol and Experiment Log

**Phase 7 (2026-11-18):** Reproducible training, validation-based model selection, selected-model held-out evaluation and aggregate plotting, a read-only Streamlit reporting interface, and software quality checks are implemented. All evaluation runs used **synthetic software-test fixtures**, not official UNSW records. No official download or real-dataset performance benchmark has been performed.

## Protocol

1. Obtain the *official* train/test CSVs from UNSW and comply with required academic citations (see `docs/dataset.md`).
2. Validate headers, binary target encoding, schema agreement, and aggregate class distributions before experiments.
3. Preserve official test records as a holdout; split only the official training rows into train and validation partitions with seed `42` and stratification.
4. Exclude label, attack category and identifiers. Do not infer feature transformations from validation or test.
5. Fit scikit-learn preprocessing **inside each model's training pipeline**, never before the data split. Both baseline models will share the same partition protocol.
6. Phase 3 (implemented): fit two baseline pipelines strictly on training rows and save local model artifacts plus reproducibility metadata, including original CSV SHA-256 hashes when the real data become available.
7. Phase 4 (implemented): compute class-wise validation metrics for both models; select using the attack-class F1 on **validation only** (Logistic Regression wins an exact tie); evaluate only the selected model on the final held-out test split. Report class support, precision, recall, F1, confusion matrix, ROC-AUC when possible, FPR=FP/(FP+TN), and FNR=FN/(TP+FN).
8. Phase 5 (implemented): render and validate local aggregate report metrics without loading models, raw records, or interacting with networks; show no scores when results are missing. The dashboard does not authenticate dataset provenance.
9. Phase 6 (implemented): run synthetic test fixtures, enforce statement coverage, check the Git index for restricted artifacts, and validate dependency consistency in CI. These checks do not establish IDS effectiveness.
10. Discuss class imbalance, possible duplicate/related flows, domain shift, and false alarms.
11. Phase 7: publish an auditable manuscript, source bibliography, model card, unfilled results template, and reproducibility checklist. **Do not report synthetic fixture scores as UNSW results.**

| Phase | Execution | Status |
| --- | --- | --- |
| 1 | Package structure, CLI and test scaffolding | Implemented |
| 2 | Local CSV loader, validation, stratified partitions, unfitted preprocessing | Implemented; synthetic test cases only |
| 2 | Official UNSW-NB15 file download / full-data inspection | **Not performed** |
| 3 | Training implementation and synthetic fixture runs | **Implemented and locally tested**; official UNSW training not performed |
| 4 | Evaluation code and aggregate graphics, synthetic test execution | **Implemented and locally tested; official UNSW evaluation not performed** |
| 5 | Aggregate read-only Streamlit view, strict report validation, synthetic UI-mock smoke tests | **Implemented and locally tested; real browser and official UNSW runs pending** |
| 6 | GitHub Actions quality gates, tracked-artifact hygiene and synthetic regression tests | **Implemented; CI result must be verified separately after each push** |
| 7 | Academic report, required dataset citations, reproducibility guide, model card and portfolio summary | **Documentation implemented; no official-data results** |

**Important distinction:** Passing test cases on fictional rows demonstrates that the software executes; it does **not** validate the classifier on real intrusions. See `docs/training.md`.

**Data provenance limitation:** The loader validates schema and expected filenames, not the authenticity or rights attached to each CSV. Only results from independently verified official files may be cited in academic claims. The official test is opened during input validation, but its labels are never used to fit, tune, or select a model.


## Phase 7 documentation verification (2026-11-18)

- **Source:** all six academic-documentation tests passed alongside the existing synthetic test suite: **103/103 locally**.
- **Measured local statement coverage:** **94.72%**, using `python -m pytest -q --cov=nids --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=90`.
- **Python syntax compilation:** passed for application, source, tests and scripts.
- **Local smoke test:** `PYTHONPATH=src python -m nids.cli status` reported no dataset, model or evaluation files.
- **Local Git index hygiene check:** passed on the existing local working-tree index; repository-wide CI must be rechecked after the Phase 7 push.
- **Local `pip check`:** failed on a dependency conflict between unrelated installed `moviepy` and `pillow` packages in the shared runner environment. This is **not evidence of a project dependency failure**. The project CI uses a fresh Python environment and should be checked after the push.
- **Last verified Phase 6 GitHub Actions:** [successful workflow run](https://github.com/abdulkarim-Mohsen/ai-network-intrusion-detection/actions/runs/44338575947). The Phase 7 run needs separate verification.
- **Research benchmark:** not performed, with official CSV files absent. No model performance metrics exist.

## 2026-11-19 — Empirical access and report-export work

- Reconfirmed UNSW's public academic-use and five-reference requirements; the original file-download link redirects to Microsoft sign-in in the available browser environment.
- The provider's dataset CSVs could not be downloaded, and no UNSW-NB15 benchmark run took place.
- Added an aggregate-only report generator with arithmetic consistency tests. Its tests use **synthetic fixtures** and cannot establish actual prediction quality.
- Next action: acquire the provider's pre-split CSVs with the user, verify origin and observed row counts, run `nids evaluate`, then review the output and update the research manuscript.


## 2026-11-18 22:12:10 UTC — First measured experiment on user-supplied files

- Received `OneDrive_3_19-11-2026.zip` from the user containing two correctly named CSVs; ZIP CRC check passed, row counts 175,341 training and 82,332 test, 45 columns, no pandas-recognized missing cells. Screenshot shows original access to a shared OneDrive folder. Independent provider-byte authentication was **not** performed.
- Input SHA-256: training `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`, testing `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`.
- Predeclared protocol: fit/validation split 140,272/35,069 using seed 42; logistic regression (max_iter 1000) vs Random Forest (100 trees) chosen by validation attack F1. Both preprocessors fitted only on fit data. Test scored once for selected Random Forest.
- Validation attack F1: Logistic Regression 95.03%, Random Forest 96.22%; selected Random Forest.
- **Measured held-out test:** 90.59% accuracy, 91.91% attack F1, 17.35% FPR. Matrix `[[30581,6419],[1328,44004]]`; AUC 98.46%. Genuine results, not synthetic-fixture metrics.
- Post-evaluation duplicate audit: 8,054 held-out test rows matched selected predictor-vector hashes present in fit rows; 16,342 validation rows also matched fit rows. This **post-hoc observation did not drive tuning or model selection** and limits independence/generalization claims.
- Evaluation environment: Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, joblib 1.5.3.
- Complete file: [measured aggregate JSON](results/evaluation.json); numerical summary: [benchmark_summary.md](results/benchmark_summary.md); full scientific discussion: [research_report.md](research_report.md).
- Raw datasets remained under git-ignored `data/raw/`. Neither CSV rows nor serialized models are published. Confirmation of GitHub CI on the final commit must be checked separately.
