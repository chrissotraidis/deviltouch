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
- The development-signed app installed and launched on the paired physical iPad. A subsequent in-place update retained the same app-data-container identity, and `Documents/diablo.ini` was read back successfully after installation; owned MPQs and saves were not removed or recopied.
- A cold launch with no root MPQs automatically presents the native iPad Files picker instead of dead-ending at the missing-data dialog.
- The picker supports selecting the five owned Diablo/Hellfire archives together, validates recognized filenames and MPQ headers, copies them into the Files-visible Documents directory, leaves no partial `.importing` file, and reaches the Blizzard splash through the engine's existing title-asset probe.
- Importing the recognized MPQs reaches the Hellfire/Diablo selector and both data sets are detected.
- Hellfire single-player hero selection, naming, difficulty selection, and game creation work.
- A new character loads into Tristram and remains stable during movement.
- Direct tap is the default iPad input path; the virtual overlay is off by default and the original HUD remains unobstructed.
- A touch refreshes the world target before issuing Diablo's native left click, avoiding stale cursor tiles during walk, item, NPC, object, and monster interactions.
- Ground-item targeting clears any prior-frame item-label lock before resolving the current touch, so a previously highlighted label cannot steal the next pickup or movement command.
- Visible ground items use their rendered sprite bounds for pointer hover and a minimum 56-pixel logical touch target, selecting the nearest item when expanded targets overlap. In a controlled test, a potion left several tiles from the hero highlighted under the pointer, then one tap produced the complete walk-and-pickup action and restored the belt count without a second tap.
- Front-end lists and the in-game pause/options menu follow the same two-step touch and pointer contract: the first tap or click moves the red selector without leaving the screen, and a second confirms the selected row.
- The front-end contract was also exercised with genuine Simulator finger events by installing a diagnostic copy without indirect-pointer opt-in. One physical touch produced SDL's synthetic touch-mouse pair plus the real finger pair; the shared UI event normalizer discarded the duplicate and translated the finger once. A first touch on `Settings` moved the red selector to that row, and a second opened it.
- The same normalized finger path now covers the regular front-end loop plus the title, dialog, progress, and credits event loops rather than fixing one menu screen at a time.
- In that native-finger build, Credits selected on the first touch, opened on the second, and closed on a touch within the credits screen. The multiplayer provider and hero-class lists also followed the two-step rule; choosing Rogue reached the name field, raised the native keyboard, allowed it to be dismissed with the iPad keyboard control, and returned through the touchable Cancel buttons.
- The Settings scrollbar down arrow advanced focus through the complete category list, scrolled `Previous Menu` into view, and a touch on the selected row returned to the main menu. No hardware Escape key is required to leave Settings.
- Store lists use that same select-then-confirm state rule; tapping a different shop row no longer activates the previously selected entry.
- The two-step rule was exercised through the main menu, Settings, the in-game pause/options menu, Cain's town-elder menu, Griswold's main shop, individual store-item rows, Back, Sell Items, Leave the Shop, and the death-menu Load Game action. Native-finger store testing also covered the insufficient-gold feedback row and the empty-sell view without changing the save's inventory or gold.
- The merchant sweep now also covers Pepin's healer menu and buy list plus Adria's witch menu, non-empty sell list, and empty staff-recharge view. In each variant, the first tap moved the red selector, the second opened the selected view, item rows and Back used the same contract, and the test exited without accidentally selling an item.
- SDL's synthetic mouse duplicate is discarded while DevilTouch's explicitly translated finger click is retained, preventing a second coordinate-space click from replacing the intended walk or interaction destination.
- A distant world click produced sustained pathing with the camera following the character rather than a single-tile nudge.
- One tap on Farnham and one tap on Griswold each produced the full path-to-NPC interaction and opened the intended conversation or shop.
- `Settings → Controller → Touch Controls` is present, defaults to `Off`, and toggles to `On` in the running Simulator build.
- When enabled, the optional D-pad/action overlay remains visible even after a direct world tap switches the engine to pointer mode, is positioned above the 128-pixel original HUD, responds to a D-pad drag, and hides while a left or right native panel is open.
- Duplicate virtual potion shortcuts and the redundant touch menu strip are removed on iPad. Potions remain on the original directly touchable belt/inventory UI.
- Tapping the original `INV` button opens the inventory and leaves the full grid unobstructed.
- The original `CHAR`, `QUESTS`, `MAP`, `INV`, and `SPELLS` controls all opened or toggled their native panels without overlay obstruction. The speedbook also opened and selected Trap Disarm through direct touch.
- A one-finger belt tap was observed lifting a healing potion through Diablo's original left-click path, and the next tap placed it again. The paired two-finger gesture is isolated to belt/inventory items and routes the stored item directly through Diablo's original `UseInvItem` path without adding another overlay control.
- Touch-only play entered the Cathedral, targeted a skeleton, sustained movement into combat, reached the death menu, and loaded the save again through the two-step selector.
- With Simulator hardware-keyboard emulation disconnected, the hero-name field automatically raises the native iPad software keyboard and remains visible above it. The same SDL text-input path is used by multiplayer address/password, chat, gold split, and stash withdrawal fields.
- With Simulator hardware-keyboard forwarding enabled, `I` toggled the inventory, `Tab` toggled the automap, and Down/Return selected and loaded the saved game from the death menu.
- Input diagnostics proved that an ordinary Simulator host right-click, without native pointer forwarding, arrives only as a finger event plus SDL's synthetic left mouse event. This is not a valid external-mouse test; **I/O → Input → Send Pointer to Device** must be enabled so UIKit can deliver primary, secondary, and scroll events. The real pointer button-down path now refreshes the inventory target at the button coordinates before invoking Diablo's original mouse handler.

## Deployed for physical retest

- Direct screen touches and indirect trackpad contacts are now classified separately. SDL's optional companion finger stream for a trackpad is discarded before it can change direct-touch state; the native mouse path remains intact.
- Inventory gesture state resets when a contact ends outside the panel, a real pointer click takes over, iPadOS reuses a finger ID after omitting its prior finger-up, or either finger lifts after a completed two-finger action. This prevents both the stuck state that required an app relaunch and subsequent equip/place taps inheriting the prior action's consumed state.
- The two-finger gesture uses a timing window without an arbitrary finger-distance limit. It routes belt items through native item use and open-inventory items through the shared context action, including potion/scroll use and Gillian stash transfers.
- Merchant lists accept vertical swipe gestures in the main list area. Each 32-pixel logical step uses the store's existing next/previous behavior, while row activation is deferred until finger-up and suppressed after scrolling so a swipe cannot accidentally purchase or choose its starting row.
- Finger events consumed by inventory gestures no longer leak into generic control-mode detection or replace item-specific help text with the virtual-gamepad fallback.
- This input-coexistence build compiled, development-signed, installed in place, and launched on the physical iPad on 2026-07-19. Behavioral acceptance remains with the physical retest matrix below.

## Compatibility fixes exercised

- libpng no longer selects the obsolete macOS `<fp.h>` path when compiling for iOS with Xcode 26.
- fmt 10 internal bigint formatting compiles under the Xcode 26 consteval parser.
- ZeroTier is disabled for this single-player milestone because its iOS static archive is not produced by the upstream Xcode generator.

## Remaining acceptance gates

- Repeat the full matrix on a physical iPad, including multi-touch, long sessions, suspend/resume, audio, thermal behavior, and 120 Hz devices.
- With the Magic Keyboard/trackpad attached before launch, alternate direct screen taps and trackpad clicks repeatedly in menus, the world, inventory, and stash without relaunching.
- Physically verify one-finger lift/place and two-finger context action on belt, inventory, and stash items, including potions, scrolls, books, equipment, full/empty resource states, and widely separated fingers.
- Verify a paired Magic Mouse, trackpad, and Magic Keyboard on physical iPad hardware: primary click, secondary click on belt/inventory items, spell casting, hover, wheel scrolling, every stock keyboard shortcut, and modifier combinations.
- Re-run direct tap-to-destination, one-tap pickup, NPC/object interaction, and monster targeting on physical hardware and across town/dungeon pathing edge cases.
- Physically exercise the two-step selector in every store subtype and confirmation dialog; the shared handlers are fixed and Simulator front-end/pause-menu behavior is verified, but the full store matrix is not yet complete.
- Physically sweep vertical merchant-list scrolling in buy, sell, repair, recharge, and identify views, including short drags, long drags, list boundaries, and a tap immediately after a swipe.
- Verify press-and-hold continuously attacks the retained monster target and releases immediately when the finger lifts; no additional combat macro is currently planned.
- Exercise every optional-overlay action in town and dungeon combat, including sustained physical holds and simultaneous D-pad/action-button touches. The original HUD panels and speedbook have passed the Simulator touch sweep.
- Repeat the native document-picker flow on physical iPad hardware, including invalid files, cancellation, replacement, low-storage failure, and backgrounding during the 517 MB base-archive copy.
- Modernize the UIKit scene lifecycle and orientation path flagged by iOS 26 runtime warnings.
- Produce and validate a distribution archive when a public signing/distribution path is selected; the current verified signature is development-only.
