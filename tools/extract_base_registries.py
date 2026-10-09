#!/usr/bin/env python3
"""Extract registry identifiers from the compiled 1.21.1 Duneons mod.

The original project was supplied as a binary JAR.  Its generated registry
classes keep every identifier as a CONSTANT_String, which lets us recover the
registry manifests without depending on a decompiler.
"""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path


ID = re.compile(r"[a-z0-9_]+")


def class_strings(path: Path) -> set[str]:
    data = memoryview(path.read_bytes())
    position = 8
    pool_size = struct.unpack_from(">H", data, position)[0]
    position += 2
    pool: list[object | None] = [None] * pool_size
    tags = [0] * pool_size
    index = 1

    while index < pool_size:
        tag = data[position]
        tags[index] = tag
        position += 1
        if tag == 1:  # Utf8
            length = struct.unpack_from(">H", data, position)[0]
            position += 2
            pool[index] = bytes(data[position : position + length]).decode(
                "utf-8", "replace"
            )
            position += length
        elif tag in (3, 4):
            position += 4
        elif tag in (5, 6):
            position += 8
            index += 1
        elif tag in (7, 8, 16, 19, 20):
            pool[index] = struct.unpack_from(">H", data, position)[0]
            position += 2
        elif tag in (9, 10, 11, 12, 17, 18):
            position += 4
        elif tag == 15:
            position += 3
        else:
            raise ValueError(f"Unsupported constant-pool tag {tag} in {path}")
        index += 1

    values: set[str] = set()
    for index in range(1, pool_size):
        if tags[index] != 8 or not isinstance(pool[index], int):
            continue
        value = pool[pool[index]]
        if isinstance(value, str) and ID.fullmatch(value):
            values.add(value)
    values.discard("duneons")
    return values


def write_manifest(path: Path, values: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{value}\n" for value in sorted(values)), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path, help="Directory containing net/mde/duneons")
    parser.add_argument("output", type=Path, help="Registry manifest output directory")
    args = parser.parse_args()

    init = args.base / "net/mde/duneons/init"
    registries = {
        "base-blocks.txt": class_strings(init / "DuneonsModBlocks.class"),
        "base-items.txt": class_strings(init / "DuneonsModItems.class"),
        "entities.txt": class_strings(init / "DuneonsModEntities.class"),
    }
    for name, values in registries.items():
        write_manifest(args.output / name, values)
        print(f"{name}: {len(values)} identifiers")


if __name__ == "__main__":
    main()
