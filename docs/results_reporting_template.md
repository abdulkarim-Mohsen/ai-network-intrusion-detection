# Empirical Results Record — Completed Local Benchmark

> **Provenance:** Measured on user-provided CSVs with UNSW-NB15 official-split filenames and matching record counts; independent provider-file authentication not established. Results from one local experiment; do not interpret as external deployment validation.

| Field | Recorded observation |
| --- | --- |
| Execution timestamp (UTC) | 2026-11-18T22:12:10.975945+00:00 |
| Experiment source | User-uploaded OneDrive ZIP; separate provider-byte verification pending |
| Base source commit | `5bfa8f46a6caf8f0410312b7c20015b35ee01cb0` |
| Python | 3.13.5 |
| scikit-learn | 1.8.0 |
| Training CSV SHA-256 | `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` |
| Test CSV SHA-256 | `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` |
| Fit / validation / held-out rows | 140,272 / 35,069 / 82,332 |
| Seed / validation fraction / forest trees | 42 / 0.2 / 100 |

## Validation model comparison

| Metric (validation only) | Logistic Regression | Random Forest |
| --- | ---: | ---: |
| Accuracy | 93.24% | 94.92% |
| ROC-AUC | 98.44% | 99.28% |
| False-positive rate | 10.65% | 4.98% |
| Attack precision | 95.01% | 97.60% |
| Attack recall | 95.06% | 94.88% |
| Attack F1 | 95.03% | 96.22% |

**Validation-selected baseline:** Random Forest (`random_forest`), using attack F1 only.

## Final held-out test for selected Random Forest only

| Metric | Observed |
| --- | ---: |
| TN / FP / FN / TP | 30,581 / 6,419 / 1,328 / 44,004 |
| Attack precision | 87.27% |
| Attack recall | 97.07% |
| Attack F1 | 91.91% |
| FPR | 17.35% |
| FNR | 2.93% |
| ROC-AUC | 98.46% |

Post-hoc audit: 8,054 of 82,332 test rows matched a fitted-row predictor fingerprint, suggesting possible optimistic bias. Full reproducibility metadata and all computed values are available in [aggregate evaluation JSON](results/evaluation.json) and the [research report](research_report.md).
