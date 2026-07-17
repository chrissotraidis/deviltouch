# DiabloTouch — Technical & Product Feasibility Study

**Date:** 2026-07-17
**Question under study:** Does a meaningful iPadOS-first Diablo I project exist on top of DevilutionX, or would it merely duplicate and rebrand DevilutionX's existing iOS support?

**Verdict (short):** Yes — a meaningful project exists, but only if it is scoped as an **iPad experience layer** (import UX, touch-first controls, pointer/keyboard polish, Xcode workflow, one-tap distribution), not as a re-port. Roughly half of the originally proposed feature list already exists upstream and must not be duplicated. Two constraints are non-negotiable: the project **cannot be commercial** (DevilutionX is under the Sustainable Use License since v1.5.0), and it **should not be named "DiabloTouch"** (live Blizzard trademark, with direct enforcement precedent against fan-project names).

All claims below were verified against the DevilutionX master branch (commit `159b023a4cbc`, 2026-07-16), release 1.5.5 (2025-10-30), the upstream issue tracker, and primary sources (SDL source history, Apple developer documentation, USPTO records). Unverifiable items are flagged in §9.

---

## 1. What DevilutionX already provides on iOS/iPadOS (do not duplicate)

DevilutionX's iOS support is real, official, and maintained:

- **Official iOS builds.** `.github/workflows/iOS.yml` builds on every push and attaches an unsigned `devilutionx-iOS.ipa` (~8 MB) to every GitHub release, including 1.5.5. There is no TestFlight and no App Store presence; the documented install path (`docs/installing.md`) is sideloading via AltStore or Sideloadly.
- **iPad is a first-class target.** `Packaging/apple/Info.plist` declares `UIDeviceFamily` [1, 2], iPad-specific landscape-only orientations, `UIRequiresFullScreen=true`, and — importantly — `UIApplicationSupportsIndirectInputEvents=true` (opting into iPadOS 13.4+ pointer events) plus `UIFileSharingEnabled=true` and `LSSupportsOpeningDocumentsInPlace=true` (exposing the app's Documents folder in the Files app and Finder/iTunes file sharing).
- **Touch controls exist.** `Source/controls/touch/` (~1,830 lines) implements a virtual d-pad with draggable knob, primary/secondary/spell/cancel buttons, potion quick-slots, and a menu panel (character/quests/inventory/map). It is DPI-aware, activates automatically on finger input, and auto-hides when a mouse/keyboard/controller is used. Touch also drives panels (inventory, spellbook, stores) directly.
- **Sensible iOS defaults.** Saves and `diablo.ini` resolve to the sandbox Documents directory (`Source/platform/ios/ios_paths.m`, `Source/utils/paths.cpp`); MPQs are searched for there; "Fit to Screen" defaults on (handles iPad aspect ratios); fullscreen is forced; hardware cursor is correctly disabled on iOS.
- **Modern niceties already landed.** ProMotion/high refresh rate (issue #7721, fixed Feb 2025; pinned SDL 2.32.8 contains the `CADisplayLink.preferredFrameRateRange` support), and ZeroTier multiplayer on iOS (issue #8174, shipped in 1.5.5).
- **Input plumbing is in place.** SDL 2.32.8 (statically linked via FetchContent) maps iPad trackpad/mouse to real SDL mouse events (SDL has done this since 2.0.14, with relative mode since 2.0.16), delivers hardware keyboard events, and supports MFi/Xbox/PS controllers via GCController.

**Conclusion of §1:** "Port Diablo to iPad" is already done. A project whose pitch is "DevilutionX, but on iPad" duplicates upstream and has no reason to exist.

## 2. What is genuinely missing or rough (the actual gap)

The gap analysis is where the project earns — or fails to earn — its existence. Every item below is evidence-backed from the upstream tracker, docs, or code.

### 2.1 Asset import is the single worst part of the experience

- There is **no in-app import UI on iOS**. Android got an in-app file browser and import/validation UI (1.5.x release notes); iOS got nothing equivalent.
- The official docs tell users to launch the app once (to force creation of the Documents folder — a real footgun, issue #5796), then copy `DIABDAT.MPQ` in via **Finder or iTunes file sharing from a computer**. The Files-app copy method is literally struck out in `docs/installing.md` as "may no longer work" (PR #5801), even though the entitlements now support it.
- There is no `CFBundleDocumentTypes` / `UTImportedTypeDeclarations` for `.mpq`: no "Open in…" share-sheet flow, no document picker, no validation, no progress UI for a ~517 MB copy.
- SDL provides no help here: SDL2 has no file-dialog API at all, and SDL3's `SDL_ShowOpenFileDialog` has **no iOS/UIKit backend**. A proper import flow requires native Swift/Obj-C code (`UIDocumentPickerViewController`), which is exactly what comparable apps (Provenance, Delta, iDOS 3) ship.

### 2.2 Touch controls are gamepad emulation, not touch-first — and upstream has declined to change that

- The virtual gamepad is a joystick-plus-buttons overlay. There is no touch-to-move / tap-to-walk (issue #6264, open), no double-tap to pick up items (#7501, open), no touch cursor for aiming targeted spells (#7603, open) — telekinesis and runes are effectively unusable on touch (#3359, open).
- There is **zero customization**: no moving, resizing, or opacity control for the virtual controls (#6992 open since 2023, #3346 open since 2021, #7023 **closed as not_planned**). Controls overlap in-game panel buttons and that report was **closed as not_planned** (#7336).
- The mouse-centric UI has been acknowledged as a poor fit for non-desktop input since 2019 (#493, open, 60 comments) with no overhaul landed.

The two `not_planned` closures matter strategically: parts of a touch-first agenda **cannot simply be upstreamed**, which is the strongest single argument that a separate iPad-focused effort has room to exist.

### 2.3 Pointer/keyboard support is plumbed but unowned

- The upstream tracker contains **zero** issues or PRs mentioning "trackpad" or iPad pointer support. The Info.plist key is set and SDL delivers the events, but nobody has QA'd right-click spell casting, hover, scroll, cursor capture, or Smart/Magic Keyboard combos (a class of hardware with documented SDL-stack regressions elsewhere, e.g. osu! #23290).
- There is no touch/controller-friendly virtual keyboard for hero names and multiplayer passwords (#2249, open), and no keyboard-avoidance work around SDL text input.

### 2.4 No "clone → open in Xcode → run on device" path

- The device build is CMake + the vendored leetal/ios-cmake toolchain producing an **unsigned** ipa zipped by hand; the Xcode generator is only documented for the simulator. CI has no signing step. A personal-team, automatic-signing, run-on-your-own-iPad workflow does not exist and is a real contribution.
- Minor upstream wobbles: docs reference `CMake/Platforms/ios.toolchain.cmake` but the path is lowercase `platforms`; `CMAKE_OSX_DEPLOYMENT_TARGET` is set to 9.0 while the toolchain defaults to 13.0.

### 2.5 Distribution is raw

- Sideloading friction is the top recurring iOS complaint in the tracker (#6183 "integrity could not be verified", 20 comments; #4622). Upstream ships a bare ipa; there is no AltStore/SideStore **source JSON** for one-tap install-and-auto-refresh, and no EU AltStore PAL presence.
- iOS CI breaks whenever GitHub retires a macOS runner (#7584, #8338) — platform upkeep is reactive.

### 2.6 Looming platform risk upstream isn't tracking

- `UIRequiresFullScreen` is formally deprecated (Apple TN3192) and iPadOS 26's windowing system will eventually ignore it. SDL's iOS backend assumes a fullscreen window; behavior under free-form window resizing is untested territory with no upstream issue tracking it.

## 3. Verdict on the central question

A rebrand of upstream's ipa would be pointless — §1 is already done and shipped. But §2 is a coherent, real, evidence-backed body of work that upstream has partially **declined** to do (touch customization, touch-first controls), partially **not noticed** (pointer QA, iPadOS 26 windowing), and partially **left to sideloaders** (import UX, signing workflow, one-tap distribution). That is enough to justify a separate iPad-focused repository — with the scope, structure, and constraints below.

## 4. Recommended project shape: overlay, not hard fork

Three options were considered:

| Option | Assessment |
|---|---|
| Contribute everything upstream | Best for the ecosystem, but blocked for the core touch-UX agenda (#7023/#7336 closed not_planned) and would leave no room for the Xcode/distribution deliverables, which don't belong upstream. |
| Hard fork | Maximum freedom, but inherits a large, actively developed C++ codebase (SDL3 migration in progress upstream) and a permanent rebase burden. Historically how forks die. |
| **Overlay repo (recommended)** | Pin upstream as a submodule at a release tag; keep all iPad work as (a) a native Swift shell + import UI, (b) a small, well-isolated patch series against upstream, (c) an Xcode project + CI + AltStore source. Upstream-eligible pieces (pointer fixes, doc fixes, virtual-keyboard work) get submitted upstream first; only the declined/out-of-scope pieces live in the patch series. |

The overlay model keeps the project honest: its value is measured by the iPad experience delta, not by forked code volume, and it tracks upstream releases (which still fix cross-platform bugs, e.g. the 1.5.5 stash-corruption fixes) instead of diverging from them.

## 5. Scope: what the project would actually build

Ordered by user impact; effort assumes one experienced developer.

1. **First-run import flow** (highest value). Native `UIDocumentPickerViewController` screen with a `UTImportedTypeDeclarations` entry for `.mpq`, `asCopy` import with progress UI (DIABDAT.MPQ is ~517 MB), MPQ validation (magic bytes + known-file probe), shareware `spawn.mpq` guidance, and a clear "what you need and where to get it (GOG)" screen. Keep `UIFileSharingEnabled`/`LSSupportsOpeningDocumentsInPlace` as the power-user path and fix/verify the Files-app flow upstream doc-wise. *~1–2 weeks.*
2. **Touch-first control layer.** Tap-to-move/tap-to-target as the default scheme (with the upstream virtual gamepad as a selectable alternative), touch cursor for targeted spells, double-tap pickup, and move/resize/opacity editing for on-screen controls. This is the largest and riskiest chunk — it touches game input logic, not just UI. *~4–8 weeks to good quality.*
3. **Pointer & keyboard polish.** Systematic QA of trackpad right-click (spells), scroll, hover, cursor behavior, Magic Keyboard/Smart Keyboard matrix; keyboard shortcuts audit; `SDL_SetTextInputRect` keyboard avoidance; on-screen keyboard invocation for text fields. Mostly QA plus small patches, largely upstreamable. *~1–2 weeks.*
4. **Xcode-native build.** A checked-in, documented path from `git clone` to running on a personal device with automatic signing (CMake `-G Xcode -DPLATFORM=OS64` + `DEVELOPMENT_TEAM` wiring, or a thin Xcode project over a CMake-built static lib), plus CI producing both the unsigned ipa and a simulator build. *~1–2 weeks, plus ongoing runner churn.*
5. **One-tap distribution.** Publish an AltStore/SideStore source JSON so installs and 7-day refreshes are automatic; evaluate AltStore PAL (EU) — free for open-source via Epic's MegaGrant arrangement — as a zero-cost notarized channel. *~days, plus release process.*
6. **iPad-specific configuration defaults.** Auto-select sensible render scale/UI size per device class, ProMotion verification, home-indicator deferral (`SDL_HINT_IOS_HIDE_HOME_INDICATOR`), skip haptics (iPads have no Taptic Engine; controller rumble still works). *~days.*
7. **iPadOS 26 windowing readiness** (forward-looking). Test under the new windowing system, migrate off `UIRequiresFullScreen` per TN3192, and file/carry SDL patches for live bounds changes. *Unknown; research task.*

Explicitly **out of scope**: engine work, renderer changes, game balance, SDL3 migration (follow upstream), and anything shipping on non-Apple platforms.

## 6. Legal and licensing constraints (hard requirements)

1. **License: Sustainable Use License v1.0, not open source in the OSI sense.** DevilutionX relicensed from The Unlicense (≤1.4.1) to the SUL (≥1.5.0, i.e. since June 2023). The SUL permits copying, modification, and derivative works **only** distributed "free of charge for non-commercial purposes." Consequences for this project:
   - No paid app, no in-app purchases, no ad-supported build; even donation framing needs care. Distribution must be free.
   - The fork cannot be relicensed (SUL is non-sublicensable); the repo must ship the SUL text, retain upstream notices, and carry a **prominent modification notice**.
   - Basing on pre-SUL (Unlicense) code to escape these terms would mean forking a 2022 codebase and abandoning three years of fixes — not worth it. Accept the SUL.
2. **No bundled Diablo assets — ever.** `DIABDAT.MPQ` is Blizzard's copyrighted content; users must supply it (GOG sells Diablo since 2019). The shareware `spawn.mpq` is rehosted by the diasurgical project itself and Blizzard still serves the original shareware installer, but redistribution of the extracted file is tolerated practice, not documented permission — the safest posture is to **link** to diasurgical's copy rather than rehost it.
3. **Blizzard's enforcement pattern.** No DMCA has ever been filed against Devilution/DevilutionX in ~8 years; Blizzard's GitHub takedowns (D2R 2021, WoW assets 2022) targeted redistributed clients/assets, not reverse-engineered engine code. Tacit tolerance, not permission — keeping the no-assets line bright is what preserves it.
4. **The name "DiabloTouch" should be dropped.** DIABLO is a live, renewed USPTO registration (Reg. 3633218) in exactly this goods/services class, and Blizzard has enforced trademarks against a free fan engine's *name* before (FreeCraft C&D → project reborn as Stratagus, 2003). Every long-lived project in this ecosystem avoids the mark in its brand (Devilution, DevilutionX, Freeablo). Using the mark as the dominant element of a consumer-facing app name is the single most legally provocative choice available to this project, and also a near-automatic App Store Guideline 5.2.1 problem if that route is ever attempted. **Recommendation:** pick an original name (Stratagus model) — e.g. "TouchDelve", "Tristram Touch"-style names still flirt with lore; something fully original is safest — and keep "for use with Diablo® game data, which you must own" as descriptive body text only, with the standard non-affiliation disclaimer.
5. **App Store is not the plan, but not impossible.** Apple's post-2024 Guideline 4.7 era (Delta, iDOS 3, UTM SE) shows "bring your own copyrighted game files" apps are now acceptable in principle; a native engine port isn't literally an emulator, and SUL-vs-App-Store is untested but lacks the GPL's specific conflicts. Trademark exposure in name/screenshots would be the bigger review risk. Treat App Store as a possible later experiment, not a dependency.

## 7. Distribution strategy

- **Primary:** GitHub releases (unsigned ipa) + a published **AltStore/SideStore source JSON** → one-tap install and automatic 7-day re-signing for free-Apple-ID users (3-app limit still applies; $99/yr accounts get 1-year certs).
- **EU:** AltStore PAL (notarized, no content review beyond Apple's baseline; free hosting for open-source apps). Japan's MSCA marketplaces (live since Dec 2025) are a follow-on.
- **Secondary:** the Xcode personal-team path (deliverable #4) *is* a distribution channel for tinkerers and needs no Apple review at all.
- **TestFlight:** optional beta channel if a paid account is accepted; 90-day build expiry and beta review make it a treadmill, and review exposure of Blizzard IP is untested.

## 8. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Trademark complaint over name | High if named "DiabloTouch" | Rename before first release (§6.4) |
| Touch-first control layer is harder than estimated (input logic is deep in game code) | High | Prototype tap-to-move first, behind a setting; keep upstream gamepad overlay as fallback |
| Upstream divergence (active SDL3 migration) makes the patch series expensive | Medium | Pin release tags, not master; keep patches small; upstream everything acceptable |
| Blizzard tolerance shifts | Low-medium | No assets ever, no monetization (also SUL-required), non-affiliation disclaimers |
| iPadOS 26 windowing breaks the SDL fullscreen assumption | Medium, growing | Deliverable #7; track TN3192 |
| macOS CI runner churn | Low | Same fix as upstream applies (#8338); automate runner-version bumps |
| Sideloading policy changes | Low | Multiple channels (§7); US legislation (H.R.3209) unpassed as of this study |

## 9. What this study could not verify

- Whether the Files-app copy method currently works on device (upstream's own docs say "may no longer work" while the entitlements say it should) — needs on-device testing, and it directly shapes deliverable #1.
- Real-world quality of iOS ZeroTier multiplayer (shipped only in Oct 2025).
- The effective minimum iOS version of the shipped ipa (9.0 vs 13.0 toolchain conflict).
- Contributor-consent mechanics of the Unlicense→SUL relicense; per-component audit of the ~27 vendored third-party libraries (needed before any App Store attempt).
- Shareware EULA text authorizing redistribution of the extracted `spawn.mpq`.
- SDL behavior under iPadOS 26 free-form window resizing.
- Community sentiment on Hacker News/Reddit (proxy-blocked or unindexed); the near-absence of iPad-specific community threads suggests a small iOS user base — which cuts both ways: modest audience, but also an unserved one.

## 10. Recommended next steps

1. **Rename** the project and repo before any public artifact exists (§6.4).
2. Buy-or-locate Diablo game data, sideload upstream 1.5.5 on a modern iPad, and spend a day on structured on-device QA: Files-app import, trackpad right-click, Magic Keyboard, virtual gamepad ergonomics. This converts §9's biggest unknowns into facts and validates the gap analysis first-hand.
3. Stand up the overlay repo: upstream as submodule at 1.5.5, SUL + notices, `clone → open in Xcode → run` on a personal team (deliverable #4) as the first milestone — it's the enabler for everything else.
4. Ship deliverable #1 (import flow) as the first user-visible release, with an AltStore source (deliverable #5).
5. Prototype tap-to-move (deliverable #2) behind a setting; decide fork-vs-upstream per piece based on upstream's response.

---

### Appendix: key sources

- DevilutionX repo, master `159b023a4cbc`: `docs/building.md`, `docs/installing.md`, `Packaging/apple/Info.plist`, `Source/controls/touch/`, `Source/platform/ios/ios_paths.m`, `Source/options.cpp`, `CMake/platforms/ios.cmake`, `.github/workflows/iOS.yml`, `LICENSE.md` (Sustainable Use License v1.0) — https://github.com/diasurgical/devilutionX
- Release 1.5.5 assets (incl. `devilutionx-iOS.ipa`) — https://github.com/diasurgical/devilutionX/releases
- Upstream issues cited: #493, #2249, #2959, #3346, #3359, #4622, #5430, #5723, #5796, #5804, #5919, #6183, #6264, #6992, #7023, #7336, #7501, #7603, #7721, #8174; PRs #3612, #5056, #5801, #5817, #8178, #8338
- SDL iOS docs & history — https://github.com/libsdl-org/SDL/blob/SDL2/docs/README-ios.md ; pointer-support commits in `src/video/uikit/SDL_uikitview.m`; SDL3 dialog gap https://github.com/libsdl-org/SDL/issues/14121
- Apple: TN3192 (`UIRequiresFullScreen` deprecation) — https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key ; App Review Guidelines 4.7 / 2.5.2 / 5.2.1 — https://developer.apple.com/app-store/review/guidelines/ ; alternative distribution — https://developer.apple.com/support/alternative-app-marketplace-in-the-eu/
- USPTO DIABLO registration — https://trademarks.justia.com/787/70/diablo-78770575.html ; FreeCraft→Stratagus precedent — https://en.wikipedia.org/wiki/Stratagus
- Blizzard GitHub DMCA notices (D2R 2021, WoW 2022) — https://github.com/github/dmca
- Comparable import flows: Provenance (`PVUI/.../DocumentPicker.swift`), Delta FAQ — https://faq.deltaemulator.com/getting-started/importing-games , iDOS/dospad — https://github.com/litchie/dospad
- AltStore PAL — https://rileytestut.com/blog/2024/04/17/introducing-altstore-pal/
