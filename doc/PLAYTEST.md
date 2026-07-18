# iPadOS Simulator playtest record

Date: 2026-07-19

This record describes the current developer checkpoint. It includes Simulator coverage and physical-device build/signing evidence, but is not a claim of public-distribution readiness.

## Environment

- Mac architecture: ARM64
- Xcode: 26.6 (17F113)
- iOS Simulator runtime: 26.5 (23F77)
- Device: iPad Pro 13-inch (M5) Simulator
- Upstream: DevilutionX 1.5.5, commit `7223eeac9e8274fbf665b4de86fda26d3b22c52f`
- Game data: user-owned Diablo and Hellfire MPQs imported from ignored local storage

Physical-device build target:

- Device: iPad Pro 12.9-inch (6th generation), ARM64, iPadOS 26.5.2 (23F84)
- Connection: paired, Developer Mode enabled, available through CoreDevice
- Signing: Xcode-managed Apple Development profile for `com.chrissotraidis.deviltouch`

## Verified

- The checked-in configure and build scripts produce a Mach-O ARM64 Simulator app.
- The physical-device toolchain produces a thin Mach-O ARM64 iPhoneOS app with a minimum deployment target of iOS 13.0.
- Xcode automatic provisioning created a valid development signature and embedded profile for `com.chrissotraidis.deviltouch`; `codesign` verification passed and the signed bundle contains no proprietary game data.
- A cold launch with no root MPQs automatically presents the native iPad Files picker instead of dead-ending at the missing-data dialog.
- The picker supports selecting the five owned Diablo/Hellfire archives together, validates recognized filenames and MPQ headers, copies them into the Files-visible Documents directory, leaves no partial `.importing` file, and reaches the Blizzard splash through the engine's existing title-asset probe.
- Importing the recognized MPQs reaches the Hellfire/Diablo selector and both data sets are detected.
- Hellfire single-player hero selection, naming, difficulty selection, and game creation work.
- A new character loads into Tristram and remains stable during movement.
- Direct tap is the default iPad input path; the virtual overlay is off by default and the original HUD remains unobstructed.
- A touch refreshes the world target before issuing Diablo's native left click, avoiding stale cursor tiles during walk, item, NPC, object, and monster interactions.
- Ground-item targeting clears any prior-frame item-label lock before resolving the current touch, so a previously highlighted label cannot steal the next pickup or movement command.
- Visible ground items use their rendered sprite bounds for pointer hover and a minimum 44-point touch target. In a controlled test, a potion left several tiles from the hero highlighted under the pointer, then one tap produced the complete walk-and-pickup action and restored the belt count without a second tap.
- Front-end lists and the in-game pause/options menu follow the same two-step touch and pointer contract: the first tap or click moves the red selector without leaving the screen, and a second confirms the selected row.
- The front-end contract was also exercised with genuine Simulator finger events by installing a diagnostic copy without indirect-pointer opt-in. One physical touch produced SDL's synthetic touch-mouse pair plus the real finger pair; the shared UI event normalizer discarded the duplicate and translated the finger once. A first touch on `Settings` moved the red selector to that row, and a second opened it.
- The same normalized finger path now covers the regular front-end loop plus the title, dialog, progress, and credits event loops rather than fixing one menu screen at a time.
- In that native-finger build, Credits selected on the first touch, opened on the second, and closed on a touch within the credits screen. The multiplayer provider and hero-class lists also followed the two-step rule; choosing Rogue reached the name field, raised the native keyboard, allowed it to be dismissed with the iPad keyboard control, and returned through the touchable Cancel buttons.
- The Settings scrollbar down arrow advanced focus through the complete category list, scrolled `Previous Menu` into view, and a touch on the selected row returned to the main menu. No hardware Escape key is required to leave Settings.
- Store lists use that same select-then-confirm state rule; tapping a different shop row no longer activates the previously selected entry.
- The two-step rule was exercised through the main menu, Settings, the in-game pause/options menu, Cain's town-elder menu, Griswold's main shop, individual store-item rows, Back, Sell Items, Leave the Shop, and the death-menu Load Game action. Native-finger store testing also covered the insufficient-gold feedback row and the empty-sell view without changing the save's inventory or gold.
- SDL's synthetic mouse duplicate is discarded while DevilTouch's explicitly translated finger click is retained, preventing a second coordinate-space click from replacing the intended walk or interaction destination.
- A distant world click produced sustained pathing with the camera following the character rather than a single-tile nudge.
- One tap on Farnham and one tap on Griswold each produced the full path-to-NPC interaction and opened the intended conversation or shop.
- `Settings → Controller → Touch Controls` is present, defaults to `Off`, and toggles to `On` in the running Simulator build.
- When enabled, the optional D-pad/action overlay remains visible even after a direct world tap switches the engine to pointer mode, is positioned above the 128-pixel original HUD, responds to a D-pad drag, and hides while a left or right native panel is open.
- Duplicate virtual potion shortcuts and the redundant touch menu strip are removed on iPad. Potions remain on the original directly touchable belt/inventory UI.
- Tapping the original `INV` button opens the inventory and leaves the full grid unobstructed.
- The original `CHAR`, `QUESTS`, `MAP`, `INV`, and `SPELLS` controls all opened or toggled their native panels without overlay obstruction. The speedbook also opened and selected Trap Disarm through direct touch.
- Tapping a healing potion on the original belt consumes it directly; no virtual potion shortcut is required.
- Touch-only play entered the Cathedral, targeted a skeleton, sustained movement into combat, reached the death menu, and loaded the save again through the two-step selector.
- With Simulator hardware-keyboard emulation disconnected, the hero-name field automatically raises the native iPad software keyboard and remains visible above it. The same SDL text-input path is used by multiplayer address/password, chat, gold split, and stash withdrawal fields.

## Compatibility fixes exercised

- libpng no longer selects the obsolete macOS `<fp.h>` path when compiling for iOS with Xcode 26.
- fmt 10 internal bigint formatting compiles under the Xcode 26 consteval parser.
- ZeroTier is disabled for this single-player milestone because its iOS static archive is not produced by the upstream Xcode generator.

## Remaining acceptance gates

- Install is currently blocked by the test iPad's free-team limit of three active development apps. The device reported OpenRCT2Touch, PeonPad, and Daggerpad as the three occupied slots; one must be removed by its owner before DevilTouch can be installed and the physical matrix can continue.
- Repeat the full matrix on a physical iPad, including multi-touch, long sessions, suspend/resume, audio, thermal behavior, and 120 Hz devices.
- Re-run direct tap-to-destination, one-tap pickup, NPC/object interaction, and monster targeting on physical hardware and across town/dungeon pathing edge cases.
- Physically exercise the two-step selector in every store subtype and confirmation dialog; the shared handlers are fixed and Simulator front-end/pause-menu behavior is verified, but the full store matrix is not yet complete.
- Exercise every optional-overlay action in town and dungeon combat, including sustained physical holds and simultaneous D-pad/action-button touches. The original HUD panels and speedbook have passed the Simulator touch sweep.
- Repeat the native document-picker flow on physical iPad hardware, including invalid files, cancellation, replacement, low-storage failure, and backgrounding during the 517 MB base-archive copy.
- Modernize the UIKit scene lifecycle and orientation path flagged by iOS 26 runtime warnings.
- Produce and validate a distribution archive when a public signing/distribution path is selected; the current verified signature is development-only.
