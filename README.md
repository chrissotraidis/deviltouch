# DevilTouch

DevilTouch is an iPadOS-first, touch-focused distribution workflow for [DevilutionX](https://github.com/diasurgical/DevilutionX). It is a thin integration layer, not a new Diablo engine: this repository pins a known upstream release, carries a small reviewable patch series, and provides one-command ARM64 Simulator bring-up with user-owned game data.

The current developer prototype pins DevilutionX `1.5.5` at commit `7223eeac9e8274fbf665b4de86fda26d3b22c52f`. It has been compiled as a native ARM64 iPad Simulator app with Xcode 26.6, launched on iOS 26.5, and playtested into Tristram with Diablo and Hellfire data. Direct tap is the iPad default: a touch updates the target immediately, then uses Diablo's original left-click path for walking, attacking, talking, operating objects, and using panel items.

The virtual movement/action overlay is optional and defaults off. It can be enabled under **Settings → Controller → Touch Controls**. Its duplicate potion shortcuts and menu strip are removed on iPad; potions remain directly usable from Diablo's original belt or inventory.

## Quick start

Requirements:

- An Apple silicon Mac with Xcode and an iOS Simulator runtime
- CMake 3.21 or newer
- Git and an internet connection for the first dependency fetch
- A legally obtained Diablo installation; Hellfire is optional

Clone with the pinned upstream and launch using local game data:

```sh
git clone --recurse-submodules https://github.com/chrissotraidis/deviltouch.git
cd deviltouch
./scripts/run-ios-simulator.sh /path/to/your/Diablo
```

For this checkout, the ignored Steam export can be used without copying anything into Git:

```sh
./scripts/run-ios-simulator.sh ref/Diablo
```

The script builds the app, boots or reuses an iPad Simulator, installs only the recognized MPQ data into the app's Documents container, and launches it. If the Simulator device is still portrait, rotate it once from the Simulator toolbar; gameplay is designed and tested in landscape.

In play, tap a destination, item, NPC, monster, object, or original HUD control directly. Dragging updates the in-game cursor target. Menu rows select and activate on the same touch rather than applying the action to the previously highlighted row.

## Developer commands

```sh
./scripts/configure-ios-simulator.sh
./scripts/build-ios-simulator.sh
./scripts/import-game-data.sh /path/to/your/Diablo
./scripts/check-no-proprietary-assets.sh
```

The generated app is written to:

```text
build/ios-simulator/Release-iphonesimulator/devilutionx.app
```

`ref/`, `build/`, and Xcode-derived output are ignored. The import script recognizes `diabdat.mpq` or `spawn.mpq` plus the optional Hellfire archives `hellfire.mpq`, `hfmonk.mpq`, `hfmusic.mpq`, and `hfvoice.mpq`. It never copies executables, movies, manuals, or other installation files.

## Repository layout

- `upstream/DevilutionX` — pinned official upstream submodule
- `patches/ios` — minimal iPad-specific behavior and layout changes
- `patches/dependencies` — compatibility fixes required by Xcode 26
- `scripts` — reproducible configure, build, import, launch, and asset-safety checks
- `FEASIBILITY.md` — technical, product, and legal feasibility study
- `doc/PRD.md` — goal-based product requirements
- `doc/PLAYTEST.md` — current Simulator evidence and remaining device gates

## Current limits

This is a source-only developer preview, not a signed public release. Physical-device signing, a native document-picker import flow, iPadOS scene-lifecycle modernization, and complete touch acceptance across every menu and dungeon remain active work. Multiplayer is disabled in the iPad build while the single-player touch experience is stabilized.

DevilTouch and DevilutionX do not ship Diablo or Hellfire data. Users must supply files from a legally obtained copy. The code and patches are governed by the [Sustainable Use License](LICENSE.md), including its non-commercial and free-of-charge distribution limits. See [NOTICE.md](NOTICE.md) for the prominent modification and affiliation notice.

Diablo and Hellfire are trademarks of Blizzard Entertainment. This unofficial project is not affiliated with or endorsed by Blizzard Entertainment, GOG.com, Valve, or the DevilutionX maintainers.
