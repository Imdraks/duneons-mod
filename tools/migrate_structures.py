#!/usr/bin/env python3
"""Apply the safe 1.21.1 -> 26.2 migrations to Duneons structure NBT.

This intentionally preserves Duneons blocks, block-entity payloads, item
stacks and entities.  Registry coverage is handled by the Java port instead
of deleting content from the structures.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import nbtlib
from nbtlib.tag import Compound, Int, List, String


REPLACEMENTS = {
    "forge:entity_gravity": "minecraft:gravity",
    "forge:step_height_addition": "minecraft:step_height",
    "forge:swim_speed": "minecraft:water_movement_efficiency",
    "forge.swimSpeed": "minecraft:water_movement_efficiency",
    "minecraft:generic.armor": "minecraft:armor",
    "minecraft:generic.armor_toughness": "minecraft:armor_toughness",
    "minecraft:generic.attack_damage": "minecraft:attack_damage",
    "minecraft:generic.attack_knockback": "minecraft:attack_knockback",
    "minecraft:generic.follow_range": "minecraft:follow_range",
    "minecraft:generic.knockback_resistance": "minecraft:knockback_resistance",
    "minecraft:generic.max_health": "minecraft:max_health",
    "minecraft:generic.movement_speed": "minecraft:movement_speed",
    "minecraft:generic.oxygen_bonus": "minecraft:oxygen_bonus",
    "minecraft:horse.jump_strength": "minecraft:jump_strength",
    "minecraft:zombie.spawn_reinforcements": "minecraft:spawn_reinforcements",
    "test:chests/library_room": "minecraft:chests/stronghold_library",
}


def migrate_ids(value: object) -> int:
    changed = 0
    if isinstance(value, Compound):
        for key, child in list(value.items()):
            if isinstance(child, String) and str(child) in REPLACEMENTS:
                value[key] = String(REPLACEMENTS[str(child)])
                changed += 1
            else:
                changed += migrate_ids(child)
    elif isinstance(value, List):
        for index, child in enumerate(value):
            if isinstance(child, String) and str(child) in REPLACEMENTS:
                value[index] = String(REPLACEMENTS[str(child)])
                changed += 1
            else:
                changed += migrate_ids(child)
    return changed


def migrate_pools(structure: Compound, pool_root: Path) -> int:
    changed = 0
    for block in structure.get("blocks", []):
        block_nbt = block.get("nbt")
        if block_nbt is None or "pool" not in block_nbt:
            continue
        old_pool = str(block_nbt["pool"])
        new_pool: str | None = None
        if old_pool in ("", "minecraft:", "duneons:"):
            new_pool = "minecraft:empty"
        elif old_pool.startswith("test:"):
            new_pool = "duneons:" + old_pool.removeprefix("test:")
        elif old_pool.startswith("duneons:"):
            pool_path = pool_root / (old_pool.removeprefix("duneons:") + ".json")
            if not pool_path.is_file():
                new_pool = "minecraft:empty"
        if new_pool is not None and new_pool != old_pool:
            block_nbt["pool"] = String(new_pool)
            changed += 1
    return changed


def migrate_spawners(value: object) -> int:
    changed = 0
    if isinstance(value, Compound):
        spawn_data = value.get("SpawnData")
        if isinstance(spawn_data, Compound) and "id" in spawn_data and "entity" not in spawn_data:
            value["SpawnData"] = Compound({"entity": spawn_data})
            changed += 1

        potentials = value.get("SpawnPotentials")
        if isinstance(potentials, List):
            migrated = []
            for entry in potentials:
                if isinstance(entry, Compound) and "Entity" in entry:
                    migrated.append(
                        Compound(
                            {
                                "weight": entry.get("Weight", Int(1)),
                                "data": Compound({"entity": entry["Entity"]}),
                            }
                        )
                    )
                    changed += 1
                else:
                    migrated.append(entry)
            if changed:
                value["SpawnPotentials"] = List[Compound](migrated)

        for child in list(value.values()):
            changed += migrate_spawners(child)
    elif isinstance(value, List):
        for child in value:
            changed += migrate_spawners(child)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("resources", type=Path, help="src/main/resources directory")
    args = parser.parse_args()

    structures = args.resources / "data/duneons/structure"
    pools = args.resources / "data/duneons/worldgen/template_pool"
    changed_files = 0
    changed_values = 0
    for path in structures.rglob("*.nbt"):
        structure = nbtlib.load(path)
        changed = migrate_ids(structure) + migrate_pools(structure, pools) + migrate_spawners(structure)
        if changed:
            structure.save()
            changed_files += 1
            changed_values += changed
    print(f"Migrated {changed_values} values in {changed_files} structures")


if __name__ == "__main__":
    main()
