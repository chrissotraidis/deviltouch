# iPadOS Simulator playtest record

Date: 2026-07-19

This record describes the current developer checkpoint. It is Simulator evidence, not a claim of physical-device or public-distribution readiness.

## Environment

- Mac architecture: ARM64
- Xcode: 26.6 (17F113)
- iOS Simulator runtime: 26.5 (23F77)
- Device: iPad Pro 13-inch (M5) Simulator
- Upstream: DevilutionX 1.5.5, commit `7223eeac9e8274fbf665b4de86fda26d3b22c52f`
- Game data: user-owned Diablo and Hellfire MPQs imported from ignored local storage

## Verified

- The checked-in configure and build scripts produce a Mach-O ARM64 Simulator app.
- Launching without game data reaches the expected missing-data error instead of crashing.
- Importing the recognized MPQs reaches the Hellfire/Diablo selector and both data sets are detected.
- Hellfire single-player hero selection, naming, difficulty selection, and game creation work.
- A new character loads into Tristram and remains stable during movement.
- Direct tap is the default iPad input path; the virtual overlay is off by default and the original HUD remains unobstructed.
- A touch refreshes the world target before issuing Diablo's native left click, avoiding stale cursor tiles during walk, item, NPC, object, and monster interactions.
- Ground-item targeting clears any prior-frame item-label lock before resolving the current touch, so a previously highlighted label cannot steal the next pickup or movement command.
- Touch-originated menu clicks select and activate the tapped row in one gesture instead of acting on the previous selection.
- `Settings → Controller → Touch Controls` is present, defaults to `Off`, and toggles to `On` in the running Simulator build.
- When enabled, the optional D-pad/action overlay is positioned above the 128-pixel original HUD and hides while a left or right native panel is open.
- Duplicate virtual potion shortcuts and the redundant touch menu strip are removed on iPad. Potions remain on the original directly touchable belt/inventory UI.
- Tapping the original `INV` button opens the inventory and leaves the full grid unobstructed.

## Compatibility fixes exercised

- libpng no longer selects the obsolete macOS `<fp.h>` path when compiling for iOS with Xcode 26.
- fmt 10 internal bigint formatting compiles under the Xcode 26 consteval parser.
- ZeroTier is disabled for this single-player milestone because its iOS static archive is not produced by the upstream Xcode generator.

## Remaining acceptance gates

- Repeat the full matrix on a physical iPad, including multi-touch, long sessions, suspend/resume, audio, thermal behavior, and 120 Hz devices.
- Re-run direct tap-to-destination, pickup, NPC/object interaction, and monster targeting on physical hardware and across town/dungeon pathing edge cases.
- Exercise every original HUD panel and optional-overlay action in town and dungeon combat.
- Add a native document-picker import experience so end users do not need Simulator tooling.
- Modernize the UIKit scene lifecycle and orientation path flagged by iOS 26 runtime warnings.
- Configure signing and verify a clean device archive without proprietary data.
