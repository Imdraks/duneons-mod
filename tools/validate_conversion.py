#!/usr/bin/env python3
"""Validate registry coverage and resource syntax for the preservation port."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import nbtlib
from nbtlib.tag import Compound, List


def manifest(path: Path) -> set[str]:
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def collect_item_stacks(value: object, result: set[str]) -> None:
    if isinstance(value, Compound):
        item_id = str(value.get("id", ""))
        if item_id.startswith("duneons:") and ("Slot" in value or "count" in value or "Count" in value):
            result.add(item_id.removeprefix("duneons:"))
        for child in value.values():
            collect_item_stacks(child, result)
    elif isinstance(value, List):
        for child in value:
            collect_item_stacks(child, result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    args = parser.parse_args()

    registry = args.resources / "duneons/registry"
    blocks = manifest(registry / "blocks.txt")
    items = manifest(registry / "items.txt")
    entities = manifest(registry / "entities.txt")

    invalid_json: list[str] = []
    for path in args.resources.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exception:
            invalid_json.append(f"{path}: {exception}")

    structure_files = 0
    block_count = 0
    entity_count = 0
    referenced_blocks: set[str] = set()
    referenced_entities: set[str] = set()
    referenced_items: set[str] = set()
    for path in (args.resources / "data/duneons/structure").rglob("*.nbt"):
        structure_files += 1
        structure = nbtlib.load(path)
        palette = structure.get("palette", [])
        structure_blocks = structure.get("blocks", [])
        structure_entities = structure.get("entities", [])
        block_count += len(structure_blocks)
        entity_count += len(structure_entities)
        for entry in palette:
            block_id = str(entry.get("Name", ""))
            if block_id.startswith("duneons:"):
                referenced_blocks.add(block_id.removeprefix("duneons:"))
        for entry in structure_entities:
            entity_id = str(entry.get("nbt", {}).get("id", ""))
            if entity_id.startswith("duneons:"):
                referenced_entities.add(entity_id.removeprefix("duneons:"))
        collect_item_stacks(structure, referenced_items)

    missing_blocks = referenced_blocks - blocks
    missing_entities = referenced_entities - entities
    missing_items = referenced_items - blocks - items

    print(f"JSON files: {len(list(args.resources.rglob('*.json')))}; invalid: {len(invalid_json)}")
    print(f"Structures: {structure_files}; blocks: {block_count}; embedded entities: {entity_count}")
    print(f"Registered blocks/items/entities: {len(blocks)}/{len(items)}/{len(entities)}")
    print(
        "Missing referenced blocks/items/entities: "
        f"{len(missing_blocks)}/{len(missing_items)}/{len(missing_entities)}"
    )

    failures = invalid_json + [
        f"Missing block: {value}" for value in sorted(missing_blocks)
    ] + [
        f"Missing item: {value}" for value in sorted(missing_items)
    ] + [
        f"Missing entity: {value}" for value in sorted(missing_entities)
    ]
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
