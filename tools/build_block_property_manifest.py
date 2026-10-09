#!/usr/bin/env python3
"""Build dynamic block-state schemas from assets and structure palettes."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import nbtlib


PropertyMap = dict[str, dict[str, set[str]]]


def add_value(properties: PropertyMap, block: str, name: str, value: object) -> None:
    if not isinstance(value, str):
        return
    for part in value.split("|"):
        part = part.strip()
        if part:
            properties[block][name].add(part)


def collect_condition(properties: PropertyMap, block: str, condition: object) -> None:
    if isinstance(condition, list):
        for child in condition:
            collect_condition(properties, block, child)
    elif isinstance(condition, dict):
        for name, value in condition.items():
            if name.upper() in {"OR", "AND"}:
                collect_condition(properties, block, value)
            elif isinstance(value, str):
                add_value(properties, block, name, value)


def collect_blockstates(resources: Path, properties: PropertyMap) -> None:
    root = resources / "assets/duneons/blockstates"
    for path in root.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exception:
            raise RuntimeError(f"Cannot parse blockstate {path}") from exception
        block = path.stem
        for variant in data.get("variants", {}):
            for assignment in variant.split(","):
                if "=" in assignment:
                    name, value = assignment.split("=", 1)
                    add_value(properties, block, name, value)
        for part in data.get("multipart", []):
            collect_condition(properties, block, part.get("when", {}))


def collect_structures(resources: Path, properties: PropertyMap) -> None:
    root = resources / "data/duneons/structure"
    for path in root.rglob("*.nbt"):
        structure = nbtlib.load(path)
        for palette_entry in structure.get("palette", []):
            name = str(palette_entry.get("Name", ""))
            if not name.startswith("duneons:"):
                continue
            block = name.removeprefix("duneons:")
            for property_name, value in palette_entry.get("Properties", {}).items():
                add_value(properties, block, property_name, str(value))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    properties: PropertyMap = defaultdict(lambda: defaultdict(set))
    collect_blockstates(args.resources, properties)
    collect_structures(args.resources, properties)

    output: dict[str, dict[str, list[str]]] = {}
    for block, block_properties in sorted(properties.items()):
        normalized: dict[str, list[str]] = {}
        for name, values in sorted(block_properties.items()):
            if len(values) == 1:
                only = next(iter(values))
                if only in {"true", "false"}:
                    values.update({"true", "false"})
                else:
                    values.add("legacy_unused")
            normalized[name] = sorted(values)
        if normalized:
            output[block] = normalized

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Wrote {sum(len(value) for value in output.values())} properties "
        f"for {len(output)} blocks"
    )


if __name__ == "__main__":
    main()
