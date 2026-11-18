# Model Card — Offline Binary Network-Flow Baselines

**Status:** A single real-data **local experiment** was conducted on user-provided UNSW-NB15-layout CSVs; the source bytes were not independently authenticated. The designated train/test layout matches the published dataset sizes, but exact predictor overlap across splits limits interpretation. This is a non-deployable research prototype; no model binary is distributed here.

## Intended use

Educational, offline binary classification of authorized research network-flow tables, `label=0` for normal and `label=1` for attack. The model predicts labels, not verified security incidents.

## Out-of-scope use

Production blocking, real-time traffic inspection, surveillance, attribution, zero-day protection, law-enforcement decisions, or any assertion of operational accuracy.

## Algorithms and training inputs

Logistic Regression and Random Forest, each with its own training-only scikit-learn preprocessing pipeline. Excluded `id`, `attack_cat`, `label`; retained 42 predictors; 140,272 fit records and 35,069 validation records from the training file; Random Forest selected by validation attack F1. Fixed seed 42; 100 forest trees with max depth 18 and minimum leaf size 2. Code and parameters: [research report](research_report.md).

## Observed performance

**Validation-only F1 (attack class):** Logistic Regression 95.03%; Random Forest 96.22%.

**Held-out selected Random Forest (82,332 rows):** attack precision 87.27%; recall 97.07%; F1 91.91%; accuracy 90.59%; ROC-AUC 98.46%; FPR 17.35%; FNR 2.93%. Confusion matrix `[[30581, 6419], [1328, 44004]]` (true rows, predicted columns; order normal, attack).

These are measured on user-supplied benchmark files, **not independent official-byte verification or field validation**. No held-out test comparison for Logistic Regression was conducted, by design.

## Primary risks and limitations

- **False alarms:** 6,419 of 37,000 normal held-out records were classified as attacks.
- **Predictor duplicates:** 8,054 test rows share a selected-feature hash with fitted rows. A further 16,342 validation rows share predictor hashes with fitted rows, potentially inflating selection scores.
- **Dataset representativeness:** a historical synthetic testbed split is not a modern network deployment; thresholds are uncalibrated.
- **Fairness and external generalization:** no real operator study, cross-domain robustness, attack-family fairness, subgroup tests, or independent confidence intervals.
- **Reproducibility:** record dataset SHA-256 digests and library versions. Hashes cannot prove provenance.

## Security and accountability

Do not load unknown serialized model binaries. Original records and models are excluded from the public repository; aggregate metrics only are published. See [documented results](results/README.md), [references](references.md), and [research report](research_report.md).
