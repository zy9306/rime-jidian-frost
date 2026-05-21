#!/usr/bin/env python3
"""Generate a Wubi86 dictionary from the enabled Rime Frost dictionaries."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


DICT_SEPARATOR = "\n...\n"
JIDIAN_DICT = Path("jidian_dicts/wubi86_jidian.dict.yaml")
FROST_DICT = Path("rime_frost.dict.yaml")
OUTPUT_DICT = Path("rime_wubi86_frost.dict.yaml")
MISSING_LOG = Path("rime_wubi86_frost.missing.tsv")


@dataclass(frozen=True)
class SingleCode:
    text: str
    code: str
    weight: int
    order: int


@dataclass(frozen=True)
class Stats:
    frost_rows: int
    encoded_rows: int
    skipped_rows: int
    output_rows: int
    missing_chars: Counter[str]


@dataclass(frozen=True)
class MissingEntry:
    source: Path
    text: str
    source_code: str
    weight: int
    missing_chars: tuple[str, ...]


def split_rime_dict(content: str) -> tuple[str, str]:
    if DICT_SEPARATOR not in content:
        raise ValueError("Rime dictionary is missing a standalone '...' separator")

    return content.split(DICT_SEPARATOR, 1)


def iter_dict_rows(path: Path) -> list[list[str]]:
    _, body = split_rime_dict(path.read_text(encoding="utf-8"))
    rows: list[list[str]] = []

    for line in body.splitlines():
        if not line or line.startswith("#"):
            continue

        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append(parts)

    return rows


def parse_weight(parts: list[str], default: int = 0) -> int:
    if len(parts) < 3:
        return default

    try:
        return int(parts[2])
    except ValueError:
        return default


def parse_frost_imports(root: Path) -> list[Path]:
    header, _ = split_rime_dict((root / FROST_DICT).read_text(encoding="utf-8"))
    imports: list[Path] = []

    for line in header.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue

        table = stripped[2:].split("#", 1)[0].strip()
        if table:
            imports.append(root / f"{table}.dict.yaml")

    return imports


def load_single_codes(root: Path) -> tuple[dict[str, list[SingleCode]], dict[str, str]]:
    by_char: dict[str, list[SingleCode]] = {}

    for order, parts in enumerate(iter_dict_rows(root / JIDIAN_DICT)):
        text, code = parts[0], parts[1]
        if len(text) != 1 or not code.isalpha() or not code.islower():
            continue

        by_char.setdefault(text, []).append(
            SingleCode(text=text, code=code, weight=parse_weight(parts), order=order)
        )

    canonical = {
        text: sorted(codes, key=lambda item: (-len(item.code), -item.weight, item.order))[0].code
        for text, codes in by_char.items()
    }
    return by_char, canonical


def encode_word(text: str, canonical_codes: dict[str, str]) -> str:
    codes = [canonical_codes[char] for char in text]

    if len(text) == 1:
        return codes[0]
    if len(text) == 2:
        return codes[0][:2] + codes[1][:2]
    if len(text) == 3:
        return codes[0][:1] + codes[1][:1] + codes[2][:2]
    return codes[0][:1] + codes[1][:1] + codes[2][:1] + codes[-1][:1]


def collect_frost_entries(
    root: Path,
    canonical_codes: dict[str, str],
) -> tuple[dict[str, int], list[MissingEntry], Counter[str], int, int]:
    frost_weights: dict[str, int] = {}
    missing_entries: list[MissingEntry] = []
    missing_chars: Counter[str] = Counter()
    frost_rows = 0
    skipped_rows = 0

    for path in parse_frost_imports(root):
        for parts in iter_dict_rows(path):
            text = parts[0]
            if any(ord(char) < 128 for char in text):
                continue

            frost_rows += 1
            missing = [char for char in text if char not in canonical_codes]
            if missing:
                skipped_rows += 1
                missing_chars.update(missing)
                missing_entries.append(
                    MissingEntry(
                        source=path.relative_to(root),
                        text=text,
                        source_code=parts[1],
                        weight=parse_weight(parts),
                        missing_chars=tuple(dict.fromkeys(missing)),
                    )
                )
                continue

            frost_weights[text] = max(frost_weights.get(text, 0), parse_weight(parts))

    return frost_weights, missing_entries, missing_chars, frost_rows, skipped_rows


def build_rows(root: Path) -> tuple[list[tuple[str, str, int]], list[MissingEntry], Stats]:
    single_codes, canonical_codes = load_single_codes(root)
    frost_weights, missing_entries, missing_chars, frost_rows, skipped_rows = collect_frost_entries(
        root,
        canonical_codes,
    )

    rows: dict[tuple[str, str], int] = {}
    for text, weight in frost_weights.items():
        rows[(text, encode_word(text, canonical_codes))] = weight

    for text, codes in single_codes.items():
        fallback_weight = max(code.weight for code in codes)
        weight = frost_weights.get(text, fallback_weight)
        for single_code in codes:
            rows[(text, single_code.code)] = max(rows.get((text, single_code.code), 0), weight)

    sorted_rows = sorted(
        ((text, code, weight) for (text, code), weight in rows.items()),
        key=lambda row: (row[1], -row[2], row[0]),
    )
    stats = Stats(
        frost_rows=frost_rows,
        encoded_rows=len(frost_weights),
        skipped_rows=skipped_rows,
        output_rows=len(sorted_rows),
        missing_chars=missing_chars,
    )
    return sorted_rows, missing_entries, stats


def render_dict(rows: list[tuple[str, str, int]]) -> str:
    header = """# Rime dictionary
# encoding: utf-8
#
# Generated by scripts/generate_wubi86_frost_dict.py.
# Source words: rime_frost.dict.yaml import_tables.
# Source single-character codes: jidian_dicts/wubi86_jidian.dict.yaml.

---
name: rime_wubi86_frost
version: "2026-05-21"
sort: by_weight
columns:
  - text
  - code
  - weight
...
"""
    body = "".join(f"{text}\t{code}\t{weight}\n" for text, code, weight in rows)
    return header + body


def render_missing_log(entries: list[MissingEntry]) -> str:
    header = "source\ttext\tsource_code\tweight\tmissing_chars\n"
    body = "".join(
        f"{entry.source}\t{entry.text}\t{entry.source_code}\t{entry.weight}\t{''.join(entry.missing_chars)}\n"
        for entry in entries
    )
    return header + body


def write_if_changed(path: Path, content: str, dry_run: bool) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == content:
        return False

    if not dry_run:
        path.write_text(content, encoding="utf-8")
    return True


def print_stats(stats: Stats, changed: bool, dry_run: bool, output_path: Path) -> None:
    if changed:
        status = "Would update" if dry_run else "Updated"
    else:
        status = "No changes for"
    print(f"{status}: {output_path}")
    print(f"Frost rows considered: {stats.frost_rows}")
    print(f"Encoded unique words: {stats.encoded_rows}")
    print(f"Skipped rows: {stats.skipped_rows}")
    print(f"Output rows: {stats.output_rows}")

    if stats.missing_chars:
        print("Top missing chars:")
        for char, count in stats.missing_chars.most_common(20):
            print(f"  {char}\t{count}")


def print_log_status(changed: bool, dry_run: bool, log_path: Path) -> None:
    if changed:
        status = "Would update" if dry_run else "Updated"
    else:
        status = "No changes for"
    print(f"{status}: {log_path}")


def display_path(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help="Rime config directory; defaults to repository root")
    parser.add_argument("--output", default=None, help=f"Output dictionary path; defaults to {OUTPUT_DICT}")
    parser.add_argument("--missing-log", default=None, help=f"Missing-entry TSV path; defaults to {MISSING_LOG}")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing the dictionary")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    output_path = Path(args.output) if args.output else root / OUTPUT_DICT
    if not output_path.is_absolute():
        output_path = root / output_path
    missing_log_path = Path(args.missing_log) if args.missing_log else root / MISSING_LOG
    if not missing_log_path.is_absolute():
        missing_log_path = root / missing_log_path

    rows, missing_entries, stats = build_rows(root)
    content = render_dict(rows)
    changed = write_if_changed(output_path, content, args.dry_run)
    missing_log_changed = write_if_changed(missing_log_path, render_missing_log(missing_entries), args.dry_run)
    print_stats(stats, changed, args.dry_run, display_path(output_path, root))
    print_log_status(missing_log_changed, args.dry_run, display_path(missing_log_path, root))


if __name__ == "__main__":
    main()
