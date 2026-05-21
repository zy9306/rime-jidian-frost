#!/usr/bin/env python3
"""Package the Wubi86 + Rime Frost schemes."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PACKAGE_FILES = (
    "default.custom.yaml",
    "squirrel.custom.yaml",
    "weasel.custom.yaml",
    "rime_wubi86_frost.schema.yaml",
    "rime_wubi86_frost_mix.schema.yaml",
    "rime_wubi86_frost.dict.yaml",
    "rime_frost.schema.yaml",
    "rime_frost_static.schema.yaml",
    "rime_frost.dict.yaml",
    "lua/rime_datetime_translator.lua",
)

FROST_DICT_FILES = tuple(
    f"frost_dicts/cn_dicts/{name}.dict.yaml"
    for name in ("8105", "41448", "base", "ext", "tencent", "others", "corrections")
) + tuple(
    f"frost_dicts/cn_dicts_cell/{name}.dict.yaml"
    for name in (
        "medication",
        "industry_product",
        "exthot",
        "chess",
        "chess2",
        "animal",
        "game",
        "idiom",
        "sport",
        "media",
        "shulihua",
        "food",
        "inputmethod",
        "history",
        "place",
        "geography",
        "name2",
        "literature",
        "music",
        "computer",
        "composite",
        "luna",
        "name",
    )
)


def package_lua_full(root: Path | str | None = None, output: Path | str | None = None) -> Path:
    """Create a zip containing the Wubi86 and Rime Frost scheme files."""
    repo_root = Path(root) if root else Path(__file__).resolve().parents[1]
    repo_root = repo_root.resolve()
    zip_path = Path(output) if output else repo_root / "dist" / "rime-wubi86-frost.zip"
    if not zip_path.is_absolute():
        zip_path = repo_root / zip_path

    package_files = PACKAGE_FILES + FROST_DICT_FILES
    missing = [relative for relative in package_files if not (repo_root / relative).exists()]
    if missing:
        missing_list = "\n".join(f"- {item}" for item in missing)
        raise FileNotFoundError(f"Missing required Lua full package files:\n{missing_list}")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for relative in package_files:
            archive.write(repo_root / relative, arcname=relative)

    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None, help="Rime config directory; defaults to repository root")
    parser.add_argument("--output", default=None, help="Output zip path; defaults to dist/rime-wubi86-frost.zip")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(package_lua_full(args.root, args.output))


if __name__ == "__main__":
    main()
