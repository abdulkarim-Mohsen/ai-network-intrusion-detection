"""Check the expected separation of project modules."""

from pathlib import Path


def test_required_module_boundaries_present():
    root = Path(__file__).resolve().parents[1]
    expected = [
        "src/nids/data/load.py",
        "src/nids/features/preprocess.py",
        "src/nids/models/train.py",
        "src/nids/models/evaluate.py",
        "src/nids/visualization/plots.py",
        "app/streamlit_app.py",
        "src/nids/dashboard.py",
        "docs/dashboard.md",
        "docs/quality_assurance.md",
        "scripts/check_repo_hygiene.py",
        "docs/research_report.md",
        "docs/references.md",
        "docs/reproducibility.md",
        "docs/results_reporting_template.md",
        "docs/model_card.md",
        "docs/academic_portfolio.md",
        "CITATION.cff",
        "requirements.txt",
        ".gitignore",
        ".github/workflows/ci.yml",
    ]
    assert all((root / filename).is_file() for filename in expected)
