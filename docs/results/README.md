# Reproducible Aggregate Results — User-Supplied UNSW-NB15 Layout

**Researcher:** Abdulkarim Mohsen Hussein Alhuos (Cybersecurity and Networks, College of Engineering and Information Technology, Amran University).

This directory contains **aggregate results only**, without original CSVs, network records, identifiers, or model binaries. These are results of a *single local experiment* conducted on the two CSV files submitted by the user, with names and record counts matching the UNSW-NB15 designated train/test partitions. **Their source authenticity was not cryptographically or independently verified**; a matching SHA-256 documents byte identity for reproducibility, not provenance.

- [evaluation.json](evaluation.json) — actual validation scores for both models, held-out scores for only the selected model, class counts, parameters, software versions and input SHA-256 digests.
- [benchmark_summary.md](benchmark_summary.md) — arithmetic-checked human-readable metrics.
- [dataset_overlap_audit.json](dataset_overlap_audit.json) — post-hoc duplicate-predictor fingerprints; potential optimism in validation and testing is a key limitation.
- [Research report](../research_report.md) — full methodology and discussion.

**Observed held-out test summary:** Random Forest chosen by validation attack F1; N=82,332, attack F1=91.91%, accuracy=90.59%, false-positive rate=17.35%. False positives=6,419 out of 37,000 normal test records. This must not be misrepresented as operational real-world detection performance.

The original dataset must still be obtained/verified directly from UNSW for an independently authenticated research replication. Do not tune on the published held-out test results and then present that same test evaluation as unbiased.
