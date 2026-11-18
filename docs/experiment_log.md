# Experiment Protocol and Run Log

**Phase 1 status:** No dataset downloaded. No model trained. No measured evaluation results.

## Experimental plan (to be implemented)

1. Verify UNSW-NB15's official download page, citation requirements and permitted use.
2. Inspect feature schema and target balance; remove target-derived and non-predictive identifier columns.
3. Keep the designated official test split untouched if suitable; otherwise create a documented, stratified holdout before feature fitting. Never fit preprocessing on that holdout.
4. Compare Logistic Regression and Random Forest using identical training/validation inputs, fixed random seeds, and appropriate preprocessing pipelines.
5. Report per-class precision, recall, F1-score, confusion matrix, ROC-AUC when appropriate, and false-positive rate calculated as `FP / (FP + TN)` for the stated positive class.
6. Record timestamps, Python/library versions, data source, feature exclusions, row counts, data partition strategy, hyperparameters, random state, and command lines. Include confidence/uncertainty where appropriate.
7. Run the held-out test evaluation once after model selection; clearly state any deviations and limitations.

## Execution log

| Date | Event | Status | Notes |
| --- | --- | --- | --- |
| 2026-11-18 | Repository architecture scaffold | Prepared locally | No dataset or trained models |
