# Local Network Intrusion Detection — Evaluation Summary

**Evaluation time (UTC):** 2026-11-18T23:34:47.660032+00:00
**Dataset description:** Local CSVs using UNSW-NB15 official split filenames
**Selected model:** Random Forest
**Train / validation / held-out test samples:** 140272 / 35069 / 82,332
**Experiment settings:** seed=42; Random Forest trees=20; Logistic Regression max_iter=1000

## Validation comparison (selection by attack-class F1)

| Metric | Logistic Regression | Random Forest |
| --- | ---: | ---: |
| Accuracy | 93.26% | 94.87% |
| Attack precision | 95.00% | 97.61% |
| Attack recall | 95.10% | 94.78% |
| Attack F1 | 95.05% | 96.17% |
| ROC-AUC | 98.45% | 99.26% |
| False positive rate | 10.67% | 4.94% |

**Validation winner:** Random Forest

## Held-out test (selected model only)

- **Test samples:** 82,332
- **Accuracy:** 90.51%
- **Attack precision:** 87.14%
- **Attack recall:** 97.09%
- **Attack F1:** 91.85%
- **ROC-AUC:** 98.41%
- **False positive rate:** 17.55%
- **False negative rate:** 2.91%

### Confusion matrix (rows = actual, columns = predicted)

| Actual | Predicted normal (0) | Predicted attack (1) |
| --- | ---: | ---: |
| Normal (0) | 30,506 (TN) | 6,494 (FP) |
| Attack (1) | 1,321 (FN) | 44,011 (TP) |

## Research limitations

- The dashboard and this summary represent an offline academic evaluation, not live intrusion monitoring.
- Local file names and SHA-256 fingerprints do not independently authenticate a dataset provider.
- Potential repeated or correlated feature vectors across splits may affect generalization estimates.
- Do not use held-out test results for further model selection without a new untouched test set.
- Data use and provenance must be confirmed from the original provider.
