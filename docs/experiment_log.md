# Research Protocol and Experiment Log

**Phase 2 (2026-11-18):** Dataset loader, leakage-aware partitioning and an unfitted preprocessor were implemented. **No official UNSW dataset was downloaded or examined. No model was trained.** Tests use only small, synthetic fixtures.

## Protocol

1. Obtain the *official* train/test CSVs from UNSW and comply with required academic citations (see `docs/dataset.md`).
2. Validate headers, binary target encoding, schema agreement, and aggregate class distributions before experiments.
3. Preserve official test records as a holdout; split only the official training rows into train and validation partitions with seed `42` and stratification.
4. Exclude label, attack category and identifiers. Do not infer feature transformations from validation or test.
5. Fit scikit-learn preprocessing **inside each model's training pipeline**, never before the data split. Both baseline models will share the same partition protocol.
6. Phase 3: train Logistic Regression and Random Forest baselines; record random states, versions, hyperparameters and artifacts.
7. Phase 4: evaluate once on official test records after model selection. Report per-class precision, recall, F1, confusion matrix, ROC-AUC when suitable, and false-positive rate with declared positive label.
8. Discuss class imbalance, possible duplicate/related flows, domain shift, and false alarms.

| Phase | Execution | Status |
| --- | --- | --- |
| 1 | Package structure, CLI and test scaffolding | Implemented |
| 2 | Local CSV loader, validation, stratified partitions, unfitted preprocessing | Implemented; synthetic test cases only |
| 2 | Official UNSW-NB15 file download / full-data inspection | **Not performed** |
| 3 | Model training | **Not performed** |
| 4 | Held-out evaluation | **Not performed** |
