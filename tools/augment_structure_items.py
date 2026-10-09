#!/usr/bin/env python3
"""Add every Duneons item stack referenced by structures to the item manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbtlib
from nbtlib.tag import Compound, List


def collect_stacks(value: object, result: set[str]) -> None:
    if isinstance(value, Compound):
        item_id = str(value.get("id", ""))
        looks_like_stack = "Slot" in value or "count" in value or "Count" in value
        if looks_like_stack and item_id.startswith("duneons:"):
            result.add(item_id.removeprefix("duneons:"))
        for child in value.values():
            collect_stacks(child, result)
    elif isinstance(value, List):
        for child in value:
            collect_stacks(child, result)


def read_manifest(path: Path) -> set[str]:
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    args = parser.parse_args()

    registry = args.resources / "duneons/registry"
    blocks = read_manifest(registry / "blocks.txt")
    items = read_manifest(registry / "items.txt")
    referenced: set[str] = set()
    for path in (args.resources / "data/duneons/structure").rglob("*.nbt"):
        collect_stacks(nbtlib.load(path), referenced)

    additions = referenced - blocks - items
    items.update(additions)
    (registry / "items.txt").write_text(
        "".join(f"{item}\n" for item in sorted(items)), encoding="utf-8"
    )
    print(f"Added {len(additions)} structure-only item identifiers")
    for item in sorted(additions):
        print(item)


if __name__ == "__main__":
    main()
