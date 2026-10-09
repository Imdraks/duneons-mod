#!/usr/bin/env python3
"""Register legacy block/entity IDs still referenced by structure templates."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbtlib


def read_manifest(path: Path) -> set[str]:
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def write_manifest(path: Path, values: set[str]) -> None:
    path.write_text("".join(f"{value}\n" for value in sorted(values)), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    args = parser.parse_args()

    registry = args.resources / "duneons/registry"
    blocks = read_manifest(registry / "blocks.txt")
    items = read_manifest(registry / "items.txt")
    entities = read_manifest(registry / "entities.txt")
    referenced_blocks: set[str] = set()
    referenced_entities: set[str] = set()

    for path in (args.resources / "data/duneons/structure").rglob("*.nbt"):
        structure = nbtlib.load(path)
        for entry in structure.get("palette", []):
            block_id = str(entry.get("Name", ""))
            if block_id.startswith("duneons:"):
                referenced_blocks.add(block_id.removeprefix("duneons:"))
        for entry in structure.get("entities", []):
            entity_id = str(entry.get("nbt", {}).get("id", ""))
            if entity_id.startswith("duneons:"):
                referenced_entities.add(entity_id.removeprefix("duneons:"))

    added_blocks = referenced_blocks - blocks
    added_entities = referenced_entities - entities
    blocks.update(added_blocks)
    entities.update(added_entities)
    # Every registered block receives a block item, so a same-named standalone
    # item would be an illegal duplicate in the item registry.
    items.difference_update(blocks)

    write_manifest(registry / "blocks.txt", blocks)
    write_manifest(registry / "items.txt", items)
    write_manifest(registry / "entities.txt", entities)
    print(f"Added {len(added_blocks)} structure-only blocks")
    print(f"Added {len(added_entities)} structure-only entities")


if __name__ == "__main__":
    main()
