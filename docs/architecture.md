# Software Architecture (Phase 1)

## Design principles

- **Defensive / offline:** no socket scanning, packet capture, exploitation, or active traffic.
- **Separation of concerns:** file ingestion, feature transformations, model training, evaluation, plots, and dashboard live in distinct modules.
- **Reproducibility:** later phases will use a fixed seed, explicit training/validation/test partitions, recorded Python/package versions, and deterministic evaluation inputs wherever practical.
- **Leakage controls:** transformations fit only on training data; a final test set remains untouched until final evaluation; target and label-derived columns are excluded from predictors.
- **Data hygiene:** raw CSVs, processed records, trained models, and generated results stay out of version control by default.

## Directory map

```text
ai-network-intrusion-detection/
├── .github/workflows/ci.yml         # automated scaffold checks
├── app/streamlit_app.py              # Phase 5 offline UI placeholder
├── artifacts/
│   ├── models/                       # local model artifacts (ignored)
│   └── reports/                      # local experiment outputs (ignored)
├── data/
│   ├── raw/                          # official, locally downloaded files
│   └── processed/                    # local transformed files
├── docs/
│   ├── architecture.md
│   ├── experiment_log.md
│   └── research_report.md
├── src/nids/
│   ├── cli.py                         # working status command
│   ├── config.py                      # working path management
│   ├── data/load.py                   # Phase 2
│   ├── features/preprocess.py         # Phase 2
│   ├── models/train.py                # Phase 3
│   ├── models/evaluate.py             # Phase 4
│   └── visualization/plots.py         # Phase 4
├── tests/                             # scaffold unit tests
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Planned module contracts

| Module | Input | Output |
| --- | --- | --- |
| `data/load.py` | Official academic CSV paths | Validated DataFrame and schema report |
| `features/preprocess.py` | Training DataFrame, target definition | Fitted training-only transformer |
| `models/train.py` | Training/validation partitions, model config | Model bundle and reproducibility metadata |
| `models/evaluate.py` | Unseen test DataFrame, model bundle | Quantitative metrics and class-level error analysis |
| `visualization/plots.py` | Verified evaluation results | Saved figures |
| `app/streamlit_app.py` | Local, non-sensitive results | Read-only model comparison view |

**Status:** Dataset loading, partitioning and unfitted feature transformations in Phase 2 are implemented and tested with synthetic fixtures. No real data has been inspected or models trained. Components marked Phases 3–5 still contain placeholders.

## Local directory convention

`NIDS_PROJECT_ROOT` may override the project root for tests or alternative working directories. If unset, the root is resolved relative to the installed `nids` source files. Files should not be downloaded automatically by importing modules.
