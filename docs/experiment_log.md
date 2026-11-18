# Research Protocol and Experiment Log

**Phase 3 (2026-11-18):** Dataset loading, leakage-aware preprocessing, and reproducible Logistic Regression / Random Forest training are implemented. Training was executed **only against synthetic test fixtures**, not the official UNSW records. No official dataset download, real-world benchmark, or measured detection performance has been performed.

## Protocol

1. Obtain the *official* train/test CSVs from UNSW and comply with required academic citations (see `docs/dataset.md`).
2. Validate headers, binary target encoding, schema agreement, and aggregate class distributions before experiments.
3. Preserve official test records as a holdout; split only the official training rows into train and validation partitions with seed `42` and stratification.
4. Exclude label, attack category and identifiers. Do not infer feature transformations from validation or test.
5. Fit scikit-learn preprocessing **inside each model's training pipeline**, never before the data split. Both baseline models will share the same partition protocol.
6. Phase 3 (implemented): fit two baseline pipelines strictly on training rows and save local model artifacts plus reproducibility metadata, including original CSV SHA-256 hashes when the real data become available.
7. Phase 4: evaluate once on official test records after model selection. Report per-class precision, recall, F1, confusion matrix, ROC-AUC when suitable, and false-positive rate with declared positive label.
8. Discuss class imbalance, possible duplicate/related flows, domain shift, and false alarms.

| Phase | Execution | Status |
| --- | --- | --- |
| 1 | Package structure, CLI and test scaffolding | Implemented |
| 2 | Local CSV loader, validation, stratified partitions, unfitted preprocessing | Implemented; synthetic test cases only |
| 2 | Official UNSW-NB15 file download / full-data inspection | **Not performed** |
| 3 | Training implementation and synthetic fixture runs | **Implemented and locally tested**; official UNSW training not performed |
| 4 | Held-out evaluation | **Not performed** |

**Important distinction:** Passing test cases on fictional rows demonstrates that the software executes; it does **not** validate the classifier on real intrusions. See `docs/training.md`.
