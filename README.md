# Dungeons Content Vestiges — NeoForge 26.2

This repository is a source-based preservation port of the supplied Dungeons
Content 1.21.1 binary.  It targets Minecraft 26.2 and NeoForge 26.2.0.88.

The first milestone preserves registry identifiers, creative inventory access,
assets and structure/worldgen data.  Specialized block entities, mob AI,
animated renderers, GUIs and procedures are migrated incrementally instead of
being hidden behind generic binary patches.

## Current compatibility layer

- 2,562 block identifiers and block items are registered: all 2,418 original
  1.21.1 registrations plus resource and structure-only compatibility IDs.
- 761 standalone item identifiers are registered, including 76 identifiers
  found only in structure containers.
- 300 entity identifiers are summonable: all 250 registrations from the
  1.21.1 binary plus 50 legacy IDs still embedded in structures.
- The 57 historical spawn eggs are real spawn eggs again.
- All 1,098 original structure templates are included with their blocks,
  item stacks and embedded entities intact.
- State schemas recovered for 1,079 blocks preserve legacy structure palette
  values such as `facing`, `half`, `shape` and `waterlogged`.

Entity AI and rendering currently use a visible zombie compatibility entity.
Most blocks retain their visual assets and state data but use generic behavior.
Custom chest and spawner blocks are preserved in templates, but their original
block-entity logic, loot interaction and GUIs still need dedicated ports.

## Build

Windows:

```bat
gradlew.bat build
```

Linux/macOS:

```sh
./gradlew build
```

The built JAR is written to `build/libs/`.

Java 25 is required for both the build and Minecraft 26.2. On Windows, run the
commands from PowerShell or Command Prompt in the project directory; the
included Gradle wrapper downloads Gradle automatically.

## Provenance manifests

`src/main/resources/duneons/registry/` contains the recovered block, item and
entity identifiers.  `tools/extract_base_registries.py` documents how the
lists were recovered from the original Java 21 classes.

The scripts in `tools/` reproduce the registry extraction, safe NBT migrations,
block-state schema generation and conversion validation. Install their Python
dependency with `py -m pip install -r tools/requirements.txt` on Windows.
