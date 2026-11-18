"""Reject tracked files that should not be published in this research repository.

Only examines *tracked path names* and never opens data, secrets or artifacts.
This is a focused release-policy check, not a general secret or malware scanner.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable

# Any data/outputs must remain local. Keep only placeholders in these folders.
PRIVATE_DIRS = (
    ("data", "raw"),
    ("data", "processed"),
    ("artifacts", "models"),
    ("artifacts", "reports"),
)
FORBIDDEN_DIRECTORIES = frozenset({".venv", "venv", "__pycache__", ".pytest_cache", ".git"})
FORBIDDEN_SUFFIXES = (
    ".csv", ".parquet", ".feather", ".joblib", ".pkl", ".pem", ".key", ".p12", ".pfx"
)
FORBIDDEN_BASENAMES = frozenset({"id_rsa", "id_ed25519", "secrets.toml", ".env"})


def check_tracked_paths(paths: Iterable[str]) -> list[str]:
    """Return paths violating the repository's *tracked filename* policy.

    This does not detect secrets stored inside otherwise ordinary text files.
    """
    violations: list[str] = []
    for item in paths:
        parts = PurePosixPath(item).parts
        if not parts or item.startswith("/") or ".." in parts:
            violations.append(item)
            continue
        if any(segment in FORBIDDEN_DIRECTORIES for segment in parts[:-1]):
            violations.append(item)
            continue
        if any(parts[:2] == prefix for prefix in PRIVATE_DIRS):
            if len(parts) != 3 or parts[-1] != ".gitkeep":
                violations.append(item)
            continue
        filename = parts[-1]
        lower = filename.lower()
        if lower in FORBIDDEN_BASENAMES or lower.startswith(".env.") and lower != ".env.example":
            violations.append(item)
            continue
        if lower.endswith(FORBIDDEN_SUFFIXES):
            violations.append(item)
            continue
        if lower.startswith("phase") and lower.endswith("_git_payload.json"):
            violations.append(item)
            continue
        if parts[:2] == (".streamlit", "secrets.toml"):
            violations.append(item)
    return violations


def list_tracked_files(root: Path) -> list[str]:
    """Ask git for the actual index, so ignored but accidentally staged files count."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [p.decode("utf-8", errors="surrogateescape") for p in result.stdout.split(b"\0") if p]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check tracked paths for forbidden data and secrets")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        files = list_tracked_files(args.root.expanduser().resolve())
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Could not list git-tracked files: {exc}", file=sys.stderr)
        return 2
    bad = check_tracked_paths(files)
    if bad:
        print("Forbidden tracked files (remove them from the Git index):", file=sys.stderr)
        for item in bad:
            print(f"  {item}", file=sys.stderr)
        return 1
    print(f"Repository hygiene check passed ({len(files)} tracked paths).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
