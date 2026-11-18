"""Smoke tests for the offline Markdown reporting command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.render_evaluation_summary import main, render_summary


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "results" / "evaluation.json"


def test_summary_matches_published_aggregate_benchmark():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    markdown = render_summary(report)
    assert "**Selected model:** Random Forest" in markdown
    assert "Random Forest trees=100" in markdown
    assert "82,332" in markdown
    assert "17.35%" in markdown
    assert "91.91%" in markdown
    assert "not live intrusion monitoring" in markdown
    assert "publisher" in markdown


def test_cli_generates_markdown(tmp_path):
    destination = tmp_path / "benchmark_summary.md"
    assert main(["--input", str(REPORT), "--output", str(destination)]) == 0
    content = destination.read_text(encoding="utf-8")
    assert "## Held-out test" in content
    assert "| Normal (0) |" in content


def test_incomplete_report_cannot_be_summarized():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["status"] = "trained_no_evaluation"
    with pytest.raises(ValueError, match="completed"):
        render_summary(report)
