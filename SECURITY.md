# Security Policy

## Scope and intended use

This academic prototype processes **local, authorized** tabular datasets. It has no scanning or packet-capture functions and is not approved as a production security monitoring system. Keep Streamlit on localhost for research unless a separate security/privacy review is completed.

## Reporting a vulnerability

Use the GitHub repository's private vulnerability-reporting feature **if enabled**, or contact the repository owner through an appropriate private channel. Do not post credentials, sensitive traffic, exploit details, or personal information in public issues. No monitored response-time guarantee is offered by this student research project.

## Handling model and data artifacts

- Never load a joblib/pickle artifact from an untrusted source. Python deserialization can execute code.
- Obtain datasets from the provider under its stated terms and verify their provenance independently; recognized filenames or SHA-256 hashes alone do not prove authenticity.
- Keep `data/raw/`, `data/processed/`, `artifacts/models/`, and `artifacts/reports/` out of Git.
- Use a dedicated virtual environment; review dependency updates and GitHub Actions results.
- The filename-based hygiene check is preventive but cannot detect all secrets or malicious contents.
