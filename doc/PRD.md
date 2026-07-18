# DevilTouch — Product Requirements Document

**Version:** 1.0 (2026-07-17)
**Status:** Draft
**Predecessor document:** [FEASIBILITY.md](../FEASIBILITY.md) — all product decisions here derive from that study's verified findings.

---

## 1. Product summary

**DevilTouch** is a free, non-commercial, iPadOS-first distribution of the classic action-RPG engine [DevilutionX](https://github.com/diasurgical/devilutionX). It is an **iPad experience layer over upstream, not a re-port**: DevilutionX already builds and runs on iOS with a virtual gamepad. DevilTouch exists to close the specific, evidence-backed gaps that make the current iPad experience rough — asset importing, touch-first controls, trackpad/keyboard polish, a real Xcode workflow, and one-tap sideloading.

DevilTouch requires the user to supply their own legally owned game data (`DIABDAT.MPQ` from the GOG or original release of Diablo®). It ships no copyrighted game assets, ever.

> Diablo® is a registered trademark of Blizzard Entertainment, Inc. DevilTouch and its maintainers are not affiliated with or endorsed by Blizzard Entertainment. The name "DevilTouch" deliberately avoids the DIABLO mark, following the naming convention of the Devilution/DevilutionX ecosystem.

## 2. Problem statement

DevilutionX officially supports iOS/iPadOS, but the iPad experience today is (per the feasibility study, verified against upstream master and the issue tracker):

1. **Getting game data onto the device requires a computer.** There is no in-app import on iOS (Android has one); the documented flow is Finder/iTunes file sharing, and upstream's own docs strike out the Files-app method as possibly broken (upstream PR #5801, issue #5796).
2. **Touch play is gamepad emulation, not touch-native.** No tap-to-move, no touch cursor — targeted spells are effectively unusable (#3359) — and the on-screen controls can't be moved, resized, or faded; upstream closed those requests as `not_planned` (#7023, #7336).
3. **Trackpad and hardware keyboard support is plumbed but unowned.** SDL delivers the events and the Info.plist opts in, but no one has QA'd or polished the pointer experience; the upstream tracker has zero trackpad-related issues or PRs.
4. **There is no simple build or install path.** No clone-and-run Xcode workflow exists (device builds are CMake→unsigned-ipa only), and installation is bare-ipa sideloading with recurring signing friction (#6183, #4622) and no AltStore source for one-tap install.

These gaps are real, unserved (no iPad-focused fork exists), and — critically for a separate repo's right to exist — partially **declined** by upstream.

## 3. Goals

Each goal is stated as a measurable outcome. Priorities: **P0** = required for v1.0, **P1** = required for v1.x, **P2** = exploratory.

### G1 (P0) — A user with an iPad and a GOG copy of the game can be playing in under 5 minutes, with no computer involved.
- First-run experience detects missing game data and walks the user through it: what `DIABDAT.MPQ` is, where to legally get it (GOG), and how to import it.
- In-app import via the native document picker (`UIDocumentPickerViewController`), with a registered imported UTType for `.mpq`, copy-with-progress UI (the file is ~517 MB), and MPQ validation (magic bytes + known-file probe) with actionable error messages.
- The shareware path is one tap: the app links to the diasurgical-hosted `spawn.mpq` (it does **not** rehost or auto-bundle it — see C2/C3) so a user without game data can try the shareware portion.
- The app's Documents folder remains visible in the Files app (`UIFileSharingEnabled` + `LSSupportsOpeningDocumentsInPlace`) as the power-user path; Files-app import is verified working on current iPadOS or the in-app picker fully covers it.
- **Measure:** a first-time user on a clean iPad, ipa already installed, reaches the in-game town in ≤5 minutes without touching a computer; zero "Data File Error" dead-ends reachable by following the UI.

### G2 (P0) — Touch is a first-class way to play, not an emulated gamepad.
- Tap-to-move / tap-to-interact as the default control scheme on touch, with the upstream virtual gamepad preserved as a selectable alternative.
- A touch targeting mechanism makes every targeted spell (telekinesis, runes, town portal placement) fully usable by touch.
- Double-tap (or equivalent single-gesture) item pickup.
- On-screen controls are user-editable: position, size, and opacity, with a reset-to-default.
- No on-screen control may permanently obscure an in-game panel button (the state upstream closed as `not_planned` in #7336).
- **Measure:** a full shareware playthrough (town → Cathedral levels) is completable using touch only, including at least one targeted-spell use, with no input task requiring the virtual gamepad.

### G3 (P0) — Magic Keyboard, trackpad, and mouse work the way a desktop player expects.
- Verified QA matrix on physical hardware: trackpad tap/click = left click, secondary click = right click (spell cast), scroll, hover, and pointer visibility; Smart Keyboard Folio and Magic Keyboard tested explicitly (this hardware class has documented SDL-stack regressions elsewhere).
- All stock keyboard shortcuts of DevilutionX function on a hardware keyboard; a shortcut reference is available in-app.
- The on-screen keyboard appears automatically for text fields (hero name, multiplayer password) and never covers the field being edited (`SDL_SetTextInputRect` keyboard avoidance); this also resolves the touch-only text-entry gap (upstream #2249) for DevilTouch users.
- **Measure:** the QA matrix passes on at least two physical iPad + keyboard/trackpad combinations; results published in the repo.

### G4 (P0) — `git clone` → open in Xcode → Run deploys to a personal iPad.
- A checked-in, documented Xcode path (CMake Xcode generator or thin Xcode project) with automatic signing that works on a **free** personal team.
- Documented one-time setup ≤ 3 steps beyond cloning; no manual ipa zipping, no toolchain archaeology.
- CI builds every push: unsigned release ipa + simulator build; CI recipe kept resilient to GitHub macOS runner retirements (the upstream failure mode in #7584/#8338).
- **Measure:** a developer with Xcode and a free Apple ID goes from clone to the app running on their own iPad in ≤15 minutes following README instructions alone.

### G5 (P0) — Installation is one tap, and stays installed with zero maintenance for AltStore users.
- Every release publishes: the unsigned ipa (GitHub Releases) **and** an AltStore/SideStore source JSON, so users add the source once and get one-tap install plus automatic 7-day re-signing.
- Install documentation honestly states Apple's constraints (free-account 3-app limit and 7-day certificates) and the SideStore on-device refresh option.
- **P1 extension:** evaluate and, if viable at zero cost, ship on AltStore PAL (EU, notarized) — the study found open-source hosting there is free via Epic's MegaGrant arrangement.
- **Measure:** a user with AltStore installed goes from "found the project" to launching the app in ≤3 minutes; the source JSON is validated in CI on every release.

### G6 (P0) — The app configures itself correctly for the iPad it's on.
- On first launch, render scale and UI sizing are auto-selected per device class (screen size, DPI, ProMotion); no settings visit required for a good default.
- ProMotion/120 Hz verified active on supporting iPads (upstream's SDL 2.32.8 pin contains the support; DevilTouch verifies it end-to-end).
- Home-indicator gesture deferral enabled during gameplay; device haptics are not attempted on iPads (no Taptic Engine) while controller rumble continues to work.
- Saves and `diablo.ini` remain in the sandbox Documents folder — visible in Files, included in device backups; save integrity is regression-tested across app relaunch and reinstall (data survives via Files export/import).
- **Measure:** fresh install on a base iPad and an M-series iPad Pro both render crisply at correct scale with no settings changes; 120 Hz confirmed via instrument capture on ProMotion hardware.

### G7 (P1) — DevilTouch stays thin and current against upstream.
- Upstream DevilutionX is pinned as a **submodule at a release tag** (starting at 1.5.5); DevilTouch's engine changes live in a small, documented patch series; native import/shell code lives outside the engine tree entirely.
- Every patch is classified `upstream-candidate` or `declined-by-upstream` (with the issue link); upstream-candidates are submitted upstream first (pointer fixes, keyboard avoidance, doc corrections), and dropped from the series when merged.
- A new upstream release is integrated within 30 days, or a tracking issue explains why not.
- **Measure:** patch series ≤ ~15 patches at any time; each carries its classification; upstream bump latency tracked in the repo.

### G8 (P2) — Ready for where iPadOS is going.
- Investigate iPadOS 26 windowing: migrate off the deprecated `UIRequiresFullScreen` (Apple TN3192), test SDL's fullscreen assumption under free-form resizing, and file/carry SDL patches as needed.
- Investigate App Store viability as an experiment only (post-2024 Guideline 4.7 precedent: Delta, iDOS 3, UTM SE), gated on the licensing audit in C5 and never as a v1 dependency.

## 4. Non-goals

- **No re-port, no engine work.** Renderer, game logic, balance, SDL3 migration, and cross-platform features follow upstream. DevilTouch does not compete with DevilutionX; it layers on it.
- **No non-Apple platforms.** Android, desktop, and console are upstream's domain.
- **No Hellfire-specific features** beyond what upstream provides (Hellfire data works if the user imports it, same as upstream).
- **No multiplayer work** in v1 beyond not breaking upstream's ZeroTier support (shipped upstream Oct 2025); its real-world iOS quality is unverified and out of scope to fix.
- **No asset downloading of any copyrighted content, no asset conversion tools** that would embed Blizzard data in the repo or releases.
- **No monetization of any kind** — not a non-goal but a prohibition; see C1.

## 5. Constraints (non-negotiable)

These derive directly from the feasibility study's legal findings and bind every release, contribution, and communication of the project.

- **C1 — Sustainable Use License compliance.** DevilutionX ≥1.5.0 is licensed under the Sustainable Use License v1.0 (non-commercial). DevilTouch is therefore distributed **free of charge, for non-commercial purposes, forever**: no paid app, no in-app purchases, no ads, no paywalled builds, no donation-gated features. The repo and every distributed build ship the SUL text, retain all upstream copyright/license notices, and carry a **prominent notice that the software is modified** from DevilutionX. DevilTouch's own additions are released under the same terms (the SUL is non-sublicensable; no relicensing).
- **C2 — No bundled copyrighted game assets, ever.** `DIABDAT.MPQ` (and Hellfire data) never appear in the repo, releases, CI artifacts, screenshots' metadata, or test fixtures. CI includes a guard that fails any build containing an MPQ other than upstream's own `devilutionx.mpq`.
- **C3 — Shareware data is linked, not rehosted.** The app and docs link to the diasurgical-hosted `spawn.mpq` and Blizzard's own shareware installer; DevilTouch does not redistribute the file itself (redistribution of the extracted file is tolerated practice, not documented permission).
- **C4 — Trademark hygiene.** The product, repo, bundle ID, and app icon contain no Blizzard marks or artwork. "Diablo®" appears only in descriptive body text ("for use with game data from Diablo®, which you must own") always accompanied by the trademark attribution and non-affiliation disclaimer. Screenshots used in marketing/README avoid implying official status. *(Note: this repository's current slug predates the rename decision; the public project name is DevilTouch, and the repo should be renamed before the first release.)*
- **C5 — Distribution-channel gate.** Any channel involving Apple review (TestFlight, App Store, notarized marketplaces beyond baseline) requires, first: a completed license audit of upstream's ~27 vendored third-party components, and a re-check of SUL-vs-channel-terms compatibility. Sideloading channels (G5) have no such gate.
- **C6 — Upstream-first ethic.** Anything upstream would plausibly accept is offered upstream before or alongside shipping in DevilTouch (G7). The patch series exists for work upstream has declined or that is out of upstream's scope — not as a divergence engine.

## 6. Target users

1. **The iPad-first player** — owns Diablo on GOG, has a modern iPad (possibly with Magic Keyboard), wants to play on the couch without a PC in the loop. Primary persona; G1/G2/G3/G6 serve them.
2. **The sideloading enthusiast** — already runs AltStore/SideStore, installs retro ports routinely, judges projects by install friction and update cadence. G5 serves them.
3. **The tinkerer/contributor** — wants to build from source on their own device, tweak controls, and contribute patches. G4/G7 serve them.

## 7. Success metrics (v1.0, 90 days post-release)

| Metric | Target | Source |
|---|---|---|
| Time-to-town, clean iPad, no computer (G1) | ≤ 5 min, verified each release | Release QA checklist |
| Touch-only shareware playthrough (G2) | Pass, verified each release | Release QA checklist |
| Pointer/keyboard QA matrix (G3) | 100% pass on ≥2 hardware combos | Published QA matrix |
| Clone-to-device time for new dev (G4) | ≤ 15 min | Timed doc walkthrough |
| AltStore source functional (G5) | Validated in CI every release | CI |
| Import-flow failure issues filed | 0 open > 14 days | Issue tracker |
| Upstream release integration lag (G7) | ≤ 30 days | Repo tracking |
| License/asset constraint violations (C1–C4) | 0, ever | CI guard + review |

No install-count or engagement targets: the project is non-commercial by license and collects **no analytics or telemetry**.

## 8. Milestones

- **M0 — Ground truth (1–2 weeks).** On-device QA of upstream 1.5.5 on modern iPads: Files-app import status, trackpad behavior, virtual-gamepad ergonomics. Converts the study's flagged unknowns into facts; may re-scope G1/G3 details. Repo renamed per C4.
- **M1 — Developer foundation (G4, G7).** Overlay repo structure: upstream submodule @1.5.5, SUL + notices + modification notice, Xcode personal-team path, CI with ipa artifact and C2 asset guard.
- **M2 — First user release (G1, G5, G6).** Import flow, first-run experience, auto-configuration, AltStore source JSON. This is v0.9 — the "5 minutes, no computer" release.
- **M3 — Touch-first (G2).** Tap-to-move behind a setting → default; touch targeting; editable overlay. Ships as v1.0 with G3 QA matrix complete.
- **M4 — Sustain (G7, G8).** Upstream 1.6.x integration, iPadOS 26 windowing investigation, AltStore PAL evaluation.

## 9. Goal-based acceptance loop

Until G2 and G3 pass, each development checkpoint repeats this loop:

1. Pick the next unverified touch-only flow: front-end lists, hero naming, town movement/NPCs/stores, HUD/inventory/belt/spellbook, ground items, dungeon movement/combat/objects, targeted spells, pause/options, death, save/load, and every confirmation dialog.
2. Exercise it with direct touch and indirect pointer input. Any list must move its visible selector on the first tap or click and confirm only when the selected row is pressed again; world targets remain single-action.
3. If text is required, verify the native iPad software keyboard appears automatically, keeps the field visible, and allows completion without a hardware keyboard.
4. Fix the narrowest shared input handler, rebuild the ARM64 app, re-run the affected flow plus previously verified menu, movement, item, and panel regressions, and record evidence in `doc/PLAYTEST.md`.
5. Do not declare touch acceptance complete until the full matrix works without a keyboard or mandatory virtual gamepad, first in Simulator and then on physical iPad hardware.

Macros are added only if this matrix identifies a normal gameplay action that cannot be reached cleanly through the original HUD or direct touch; convenience alone is not sufficient.

## 10. Open questions (tracked from the feasibility study)

1. Does Files-app copy-in work on current iPadOS builds? (M0 answers; shapes how much G1 leans on the picker vs. Files.)
2. What is the shipped ipa's true minimum iOS version (upstream sets 9.0 vs. toolchain default 13.0)? DevilTouch will likely raise it — to what floor?
3. How well does upstream's iOS ZeroTier multiplayer actually work? (Out of scope to fix; affects whether docs mention it.)
4. Tap-to-move implementation depth: can it live mostly in the touch event layer, or does it need pathing hooks inside game code? (M3 risk; prototype early.)
5. SDL behavior under iPadOS 26 free-form window resizing (G8).

## 11. Risks

Inherited from the feasibility study §8; the PRD-level top three:

1. **G2 is the schedule risk.** Touch-first controls touch game input logic, not just UI. Mitigation: prototype in M3's first week, keep the upstream gamepad as the always-available fallback, and be willing to ship v1.0 with tap-to-move as opt-in default rather than perfect.
2. **Upstream divergence cost.** Active SDL3 migration upstream could churn the patch series. Mitigation: G7's tag-pinning and patch budget; C6's upstream-first ethic keeps the series small.
3. **Platform-policy shifts** (sideloading rules, iPadOS windowing). Mitigation: multiple channels (G5), G8 investigation, and the fact that G4's build-it-yourself path can never be revoked.
