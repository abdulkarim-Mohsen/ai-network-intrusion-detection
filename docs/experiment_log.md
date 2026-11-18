# Research Protocol and Experiment Log

**Phase 6 (2026-11-18):** Reproducible training, validation-based model selection, selected-model held-out evaluation and aggregate plotting, a read-only Streamlit reporting interface, and software quality checks are implemented. All evaluation runs used **synthetic software-test fixtures**, not official UNSW records. No official download or real-dataset performance benchmark has been performed.

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

| Phase | Execution | Status |
| --- | --- | --- |
| 1 | Package structure, CLI and test scaffolding | Implemented |
| 2 | Local CSV loader, validation, stratified partitions, unfitted preprocessing | Implemented; synthetic test cases only |
| 2 | Official UNSW-NB15 file download / full-data inspection | **Not performed** |
| 3 | Training implementation and synthetic fixture runs | **Implemented and locally tested**; official UNSW training not performed |
| 4 | Evaluation code and aggregate graphics, synthetic test execution | **Implemented and locally tested; official UNSW evaluation not performed** |
| 5 | Aggregate read-only Streamlit view, strict report validation, synthetic UI-mock smoke tests | **Implemented and locally tested; real browser and official UNSW runs pending** |
| 6 | GitHub Actions quality gates, tracked-artifact hygiene and synthetic regression tests | **Implemented; CI result must be verified separately after each push** |

**Important distinction:** Passing test cases on fictional rows demonstrates that the software executes; it does **not** validate the classifier on real intrusions. See `docs/training.md`.

**Data provenance limitation:** The loader validates schema and expected filenames, not the authenticity or rights attached to each CSV. Only results from independently verified official files may be cited in academic claims. The official test is opened during input validation, but its labels are never used to fit, tune, or select a model.
