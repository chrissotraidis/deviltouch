# DevilTouch

DevilTouch is an iPadOS-first, touch-focused distribution workflow for [DevilutionX](https://github.com/diasurgical/DevilutionX). It is a thin integration layer, not a new Diablo engine: this repository pins a known upstream release, carries a small reviewable patch series, and provides reproducible ARM64 Simulator and physical-iPad builds with user-owned game data.

The current developer prototype pins DevilutionX `1.5.5` at commit `7223eeac9e8274fbf665b4de86fda26d3b22c52f`. It has been compiled as a native ARM64 iPad Simulator app with Xcode 26.6, launched on iOS 26.5, and playtested into Tristram with Diablo and Hellfire data. Direct tap is the iPad default: a touch updates the target immediately, then uses Diablo's original left-click path for walking, attacking, talking, operating objects, and using panel items.

The virtual movement/action overlay is optional and defaults off. It can be enabled under **Settings → Controller → Touch Controls**. Its duplicate potion shortcuts and menu strip are removed on iPad; potions remain on Diablo's original belt and inventory. One finger keeps the original left-click grab/place behavior, while a two-finger tap uses the potion or other usable item.

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

For a real mouse or trackpad test in Simulator, enable **I/O → Input → Send Pointer to Device**. Enable **I/O → Keyboard → Connect Hardware Keyboard** for keyboard testing. Without pointer forwarding, Simulator intentionally turns every host click—including a host right-click—into a one-finger screen tap, so the app receives no secondary-button information. On a forwarded or physical iPad pointer, left-click retains Diablo's original action and right-click uses the item or casts the selected spell.

To build, sign, install, and launch on a paired iPad, use the 10-character team identifier from your Apple Development certificate:

```sh
DEVELOPMENT_TEAM=YOURTEAMID ./scripts/run-ios-device.sh
```

The iPad must be unlocked, paired with the Mac, and have Developer Mode enabled. `DEVICE_ID` can be set to a CoreDevice identifier when more than one available iPad is paired. A free Apple team permits only three active development apps per device; if that limit is reached, iPadOS requires removing one of those apps before DevilTouch can be installed.

On an iPad, launch DevilTouch with no game data installed and the native Files picker opens automatically. Select `DIABDAT.MPQ` (or `spawn.mpq`) and, optionally, `hellfire.mpq`, `hfmonk.mpq`, `hfmusic.mpq`, and `hfvoice.mpq`; multiple files can be selected at once. DevilTouch validates recognized filenames and MPQ headers, shows native copy progress, stores canonical lowercase copies in its Files-visible Documents folder, and then lets the engine verify the expected game content before continuing. The app never downloads or bundles game data.

In play, tap a destination, visible item, NPC, monster, object, or original HUD control directly. A single ground-item tap highlights it, walks the character to it, and picks it up; dragging updates the in-game cursor target. On the belt or inventory, one finger grabs or places an item and a two-finger tap uses it. List menus use a consistent two-step contract for both touch and pointer input: the first tap or click moves the red selector, and a second on the selected row confirms it. Stock DevilutionX keyboard shortcuts and mouse buttons remain available when hardware is connected.

## Developer commands

```sh
./scripts/configure-ios-simulator.sh
./scripts/build-ios-simulator.sh
./scripts/configure-ios-device.sh
./scripts/build-ios-device.sh
./scripts/import-game-data.sh /path/to/your/Diablo
./scripts/check-no-proprietary-assets.sh
```

The generated apps are written to:

```text
build/ios-simulator/Release-iphonesimulator/devilutionx.app
build/ios-device/Release-iphoneos/devilutionx.app
```

The device build is unsigned when `DEVELOPMENT_TEAM` is omitted, which is useful for compile verification. Supplying a team ID enables Xcode-managed development signing and produces an installable app.

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

This is a source-only developer preview, not a signed public release. A native ARM64 physical-device build and Xcode-managed development signature are verified, but installation and physical touch acceptance remain gated by an available development-app slot on the test iPad. iPadOS scene-lifecycle modernization and complete touch acceptance across every menu and dungeon remain active work. The native document picker and iPad software keyboard have been exercised in Simulator, but still require physical-device acceptance; multiplayer is disabled in the iPad build while the single-player touch experience is stabilized.

DevilTouch and DevilutionX do not ship Diablo or Hellfire data. Users must supply files from a legally obtained copy. The code and patches are governed by the [Sustainable Use License](LICENSE.md), including its non-commercial and free-of-charge distribution limits. See [NOTICE.md](NOTICE.md) for the prominent modification and affiliation notice.

Diablo and Hellfire are trademarks of Blizzard Entertainment. This unofficial project is not affiliated with or endorsed by Blizzard Entertainment, GOG.com, Valve, or the DevilutionX maintainers.
