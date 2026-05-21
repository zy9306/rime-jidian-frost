#!/usr/bin/env python3
"""Fetch upstream dictionaries and merge them into this Rime config."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


JIDIAN_REPO = "https://github.com/KyleBing/rime-wubi86-jidian.git"
FROST_REPO = "https://github.com/gaboolic/rime-frost.git"

JIDIAN_DICTS = {
    "wubi86_jidian.dict.yaml": "jidian_dicts/wubi86_jidian.dict.yaml",
}

FROST_DIRS = {
    "cn_dicts": "frost_dicts/cn_dicts",
    "cn_dicts_cell": "frost_dicts/cn_dicts_cell",
}


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def clone_repo(url: str, destination: Path) -> None:
    run(["git", "clone", "--depth", "1", url, str(destination)])


def split_rime_dict(text: str) -> tuple[str, str]:
    separator = "\n...\n"
    if separator not in text:
        raise ValueError("Rime dictionary is missing a standalone '...' separator")

    header, body = text.split(separator, 1)
    return header + "\n", body


def remove_import_tables(header: str) -> str:
    lines = header.splitlines()
    result: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith("import_tables:"):
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if next_line.startswith((" ", "\t")) or not next_line.strip() or next_line.lstrip().startswith("#"):
                    index += 1
                    continue
                break
            continue

        result.append(line)
        index += 1

    return "\n".join(result).rstrip() + "\n"


def write_if_changed(path: Path, content: str, dry_run: bool) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == content:
        return False

    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return True


def merge_jidian_dicts(root: Path, upstream_root: Path, dry_run: bool) -> list[Path]:
    changed: list[Path] = []

    for source, target in JIDIAN_DICTS.items():
        source_path = upstream_root / source
        target_path = root / target
        content = source_path.read_text(encoding="utf-8")

        if source == "wubi86_jidian.dict.yaml":
            header, body = split_rime_dict(content)
            content = remove_import_tables(header) + "...\n" + body.rstrip() + "\n"

        if write_if_changed(target_path, content, dry_run):
            changed.append(target_path)

    return changed


def merge_frost_dict(root: Path, upstream_root: Path, dry_run: bool) -> bool:
    source_path = upstream_root / "rime_frost.dict.yaml"
    header, _ = split_rime_dict(source_path.read_text(encoding="utf-8"))

    lines = []
    for line in header.splitlines():
        if line.lstrip().startswith("# - cn_dicts/tencent"):
            indent = line[: len(line) - len(line.lstrip())]
            lines.append(indent + line.lstrip()[2:].replace("cn_dicts/", "frost_dicts/cn_dicts/"))
        else:
            lines.append(
                line.replace("cn_dicts_cell/", "frost_dicts/cn_dicts_cell/").replace(
                    "cn_dicts/",
                    "frost_dicts/cn_dicts/",
                )
            )

    content = "\n".join(lines).rstrip() + "\n...\n\n"
    return write_if_changed(root / "rime_frost.dict.yaml", content, dry_run)


def copy_frost_directories(root: Path, upstream_root: Path, dry_run: bool) -> list[Path]:
    changed: list[Path] = []

    for source_directory, target_directory in FROST_DIRS.items():
        source_dir = upstream_root / source_directory
        target_dir = root / target_directory
        source_files = sorted(source_dir.glob("*.dict.yaml"))

        for source_path in source_files:
            target_path = target_dir / source_path.name
            content = source_path.read_text(encoding="utf-8")
            if write_if_changed(target_path, content, dry_run):
                changed.append(target_path)

    if merge_frost_dict(root, upstream_root, dry_run):
        changed.append(root / "rime_frost.dict.yaml")

    return changed


def update_dictionaries(root: Path, dry_run: bool) -> list[Path]:
    with tempfile.TemporaryDirectory(prefix="rime-upstream-") as temp_dir:
        temp_root = Path(temp_dir)
        jidian_root = temp_root / "rime-wubi86-jidian"
        frost_root = temp_root / "rime-frost"

        clone_repo(JIDIAN_REPO, jidian_root)
        clone_repo(FROST_REPO, frost_root)

        changed = merge_jidian_dicts(root, jidian_root, dry_run)
        changed.extend(copy_frost_directories(root, frost_root, dry_run))

    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help="Rime config directory; defaults to repository root")
    parser.add_argument("--dry-run", action="store_true", help="Report files that would change without writing them")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]

    changed = update_dictionaries(root, args.dry_run)
    if not changed:
        print("No dictionary changes.")
        return

    prefix = "Would update" if args.dry_run else "Updated"
    for path in changed:
        print(f"{prefix}: {path.relative_to(root)}")


if __name__ == "__main__":
    main()
