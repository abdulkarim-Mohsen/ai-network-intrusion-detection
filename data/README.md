# Local datasets only

Obtain `UNSW_NB15_training-set.csv` and `UNSW_NB15_testing-set.csv` from the UNSW research project linked in [docs/dataset.md](../docs/dataset.md), subject to its academic-use and attribution conditions. Place those files in `data/raw/` locally. Do not commit or redistribute them through this project.

Run `nids inspect-data --data-dir data/raw` to confirm their schema and report aggregate counts. `data/processed/` is reserved for future local outputs and is ignored by Git.
