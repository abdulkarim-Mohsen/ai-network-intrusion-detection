# Locally Measured Network Intrusion Detection Baseline Results

> **Provenance warning:** These numbers were imported from a local JSON file. 
> This generator checks arithmetic and selection rules, **not** whether 
> the CSVs originated from UNSW or whether the experiment was independently replicated.
> Verify the original source and file contents before reporting these as official UNSW-NB15 findings.

## Method and model selection

Validation attack F1 determines the selected baseline. The provider-designated test split is used only for the selected model.

| Validation metric | Logistic Regression | Random Forest |
| --- | ---: | ---: |
| Validation observations | 35069 | 35069 |
| Attack precision | 0.9501 | 0.9760 |
| Attack recall | 0.9506 | 0.9488 |
| Attack F1 | 0.9503 | 0.9622 |
| ROC-AUC | 0.9844 | 0.9928 |
| False-positive rate | 0.1065 | 0.0498 |

**Validation-selected model:** `random_forest`

## Held-out test — selected model only

| Metric | Observed |
| --- | ---: |
| Test observations | 82332 |
| True negatives | 30581 |
| False positives | 6419 |
| False negatives | 1328 |
| True positives | 44004 |
| Accuracy | 0.9059 |
| Attack precision | 0.8727 |
| Attack recall | 0.9707 |
| Attack F1 | 0.9191 |
| False-positive rate | 0.1735 |
| False-negative rate | 0.0293 |
| ROC-AUC | 0.9846 |

## Input-file provenance evidence

The following SHA-256 values identify the **local bytes** and do not independently authenticate their source:

- `UNSW_NB15_training-set.csv`: `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa`
- `UNSW_NB15_testing-set.csv`: `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559`

## Scientific limitations

- Positive class: `label=1` (attack); negative class: `label=0` (normal).
- Dataset authenticity and permitted use must be confirmed against the UNSW official page.
- Results from a static research benchmark do not establish real-world deployment performance.
- This report is a generated summary, **not** a peer-reviewed publication or independent replication.
- Do not change model parameters after seeing these held-out results and present the same test split as unbiased.
