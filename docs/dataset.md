# Dataset Provenance, Permission and Preprocessing Protocol

## 1. Authorized primary source

UNSW Sydney / UNSW Canberra, **UNSW-NB15 Dataset**:
https://research.unsw.edu.au/projects/unsw-nb15-dataset

The official webpage links to the provider's download location. Obtain these **specific pre-split CSVs**, not the four large raw CSVs used to construct the corpus:

- `UNSW_NB15_training-set.csv` — the official page describes **175,341** records.
- `UNSW_NB15_testing-set.csv` — the official page describes **82,332** records.

Those figures are **provider-reported metadata**, not measurements produced by this project. No data has been bundled with the repository. Keep both official files under `data/raw/`; they are excluded by `.gitignore`.

## 2. Terms of use and required attribution

On its official webpage, UNSW grants free use of UNSW-NB15 for **academic research** in perpetuity, says **commercial use must be agreed by the authors**, and retains copyright. The page requires dataset users to cite **five specified papers**. This is **not an assertion that the dataset is MIT-licensed or public domain**. The MIT license in this repository applies **only to the project's original code**. Review the current UNSW terms before using or distributing the underlying data, and do not rehost raw records.

Provider-requested publications (full titles and bibliography appear on the official dataset webpage):

1. Moustafa, N. and Slay, J. (2015). *UNSW-NB15: A comprehensive data set for network intrusion detection systems.* MilCIS. https://doi.org/10.1109/MilCIS.2015.7348942
2. Moustafa, N. and Slay, J. (2016). *The evaluation of Network Anomaly Detection Systems: Statistical analysis of the UNSW-NB15 dataset and the comparison with the KDD99 dataset.* *Information Security Journal: A Global Perspective*.
3. Moustafa, N., et al. (2017). *Novel geometric area analysis technique for anomaly detection using trapezoidal area estimation on large-scale networks.* *IEEE Transactions on Big Data*.
4. Moustafa, N., et al. (2017). *Big data analytics for intrusion detection system: statistical decision-making using finite dirichlet mixture models.* *Data Analytics and Decision Support for Cybersecurity*. Springer, pp. 127–156.
5. Sarhan, M., Layeghy, S., Moustafa, N. and Portmann, M. *NetFlow Datasets for Machine Learning-Based Network Intrusion Detection Systems.* BDTA/WiCON 2020 conference proceedings (published as conference-proceedings volume). See UNSW's official citation list.

## 3. Local setup / validation

From the project root:

```text
data/
└── raw/
    ├── UNSW_NB15_training-set.csv
    └── UNSW_NB15_testing-set.csv
```

```bash
python -m pip install -r requirements-dev.txt
nids status
nids inspect-data --data-dir data/raw
python -m pytest -q
```

The `inspect-data` command reads only the two local CSV files, checks required columns and 0/1 labels, ensures both schemas match, and prints **aggregate counts** of rows, target labels, and missing cells. It does **not** download anything, train a model, or print individual traffic records. Invalid or missing files raise errors and will not produce experimental claims.

## 4. Data leakage prevention

- Preserve the UNSW-provided test partition *as the final holdout*. Never merge its records into the training pool.
- Split **only** the official training rows into fit and validation subsets with stratification and a fixed seed (`42` by default).
- Exclude `id` (row identifier), `attack_cat` (ground-truth attack category), and `label` (classification target) from every predictor matrix.
- Treat `proto`, `service`, `state` as categoricals; remaining UNSW split features as numeric.
- Numeric parse errors and infinities become missing values. Blank categorical cells become missing; the meaningful placeholder `-` is retained as a category.
- Use an **unfitted** scikit-learn `ColumnTransformer`: median imputation + standard scaling for numerics, most-frequent imputation + one-hot encoding for categoricals.
- **Only fit** these transformers on `X_train` in a training pipeline. The test set must never be involved in fitting, scaling, encoding, choosing hyperparameters, or selecting features.
- Unseen categories in validation/test will be encoded with `handle_unknown='ignore'`.

`partition_data` produces raw feature/target partitions; `build_preprocessor` returns an *unfitted* transformer. No fitted models or accuracy values are produced during Phase 2.

## 5. Research limitations

This dataset is from a controlled simulation setting rather than live deployment. Its provided train/test partitions are not proof of time-based independence or absence of highly similar sessions. Class proportions can differ between train and test. Future evaluation must report the positive-class definition, class distributions, prevalence-sensitive metrics, and false-positive rate, and explicitly discuss any split limitations.

**Status on 2026-11-18:** Dataset download and actual-row inspection have not been performed. The loader and preprocessing logic have been tested on *synthetic fixtures only*.
