#!/usr/bin/env python3
"""Format YAML files with Prettier, preserving Rime dictionary bodies."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


DEFAULT_EXCLUDES = {".git", "build", "dist", "__pycache__"}
DICT_SEPARATOR = "\n...\n"


def find_prettier() -> list[str]:
    configured = os.environ.get("PRETTIER")
    if configured:
        return configured.split()

    prettier = shutil.which("prettier")
    if prettier:
        return [prettier]

    npx = shutil.which("npx")
    if npx:
        return [npx, "--yes", "prettier"]

    raise RuntimeError("Prettier is not available. Install prettier or make npx available.")


def run_prettier(prettier: list[str], path: Path) -> str:
    result = subprocess.run(
        [*prettier, "--parser", "yaml", str(path)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout


def is_excluded(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    return any(part in DEFAULT_EXCLUDES for part in relative_parts)


def iter_yaml_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.yaml")
        if path.is_file() and not is_excluded(path, root)
    )


def split_dict_yaml(content: str) -> tuple[str, str]:
    if DICT_SEPARATOR not in content:
        raise ValueError("Rime dictionary is missing a standalone '...' separator")

    return content.split(DICT_SEPARATOR, 1)


def format_dict_yaml(prettier: list[str], path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    header, body = split_dict_yaml(content)

    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", encoding="utf-8", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(header.rstrip() + "\n")

    try:
        formatted_header = run_prettier(prettier, temp_path).rstrip()
    finally:
        temp_path.unlink(missing_ok=True)

    return formatted_header + DICT_SEPARATOR + body


def format_plain_yaml(prettier: list[str], path: Path) -> str:
    return run_prettier(prettier, path)


def format_file(prettier: list[str], path: Path, dry_run: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    if path.name.endswith(".dict.yaml"):
        formatted = format_dict_yaml(prettier, path)
    else:
        formatted = format_plain_yaml(prettier, path)

    if formatted == original:
        return False

    if not dry_run:
        path.write_text(formatted, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help="Rime config directory; defaults to repository root")
    parser.add_argument("--dry-run", action="store_true", help="Report files that would change without writing them")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    prettier = find_prettier()

    changed: list[Path] = []
    for path in iter_yaml_files(root):
        if format_file(prettier, path, args.dry_run):
            changed.append(path)

    if not changed:
        print("No YAML changes.")
        return

    prefix = "Would format" if args.dry_run else "Formatted"
    for path in changed:
        print(f"{prefix}: {path.relative_to(root)}")


if __name__ == "__main__":
    main()
