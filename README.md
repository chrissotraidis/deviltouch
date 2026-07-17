# diablotouch (working title — see naming note)

Feasibility study for a proposed iPadOS-first Diablo I experience built on top of
[DevilutionX](https://github.com/diasurgical/devilutionX).

Documents:

- **[FEASIBILITY.md](FEASIBILITY.md)** — deep technical, product, and legal feasibility
  study (2026-07-17) answering the central question: *does a meaningful project exist here,
  or would it merely duplicate DevilutionX's existing iOS support?*
- **[doc/PRD.md](doc/PRD.md)** — goal-based product requirements document for **DevilTouch**, the
  proposed project name (trademark-safe, following the Devilution naming convention).

Summary of the study's conclusions:

- **Feasible and worthwhile**, but only as an *iPad experience layer* over upstream — asset
  import UX, touch-first controls, pointer/keyboard polish, an Xcode-native build, and
  one-tap sideloading — not as a re-port. Upstream already ships official iOS builds with a
  virtual gamepad.
- **Recommended shape:** overlay repo pinning upstream as a submodule, with a small patch
  series; upstream-eligible work goes upstream first.
- **Hard constraints:** DevilutionX is under the Sustainable Use License (non-commercial,
  free-of-charge distribution only); no Diablo game assets may ever be bundled; and the
  project should be **renamed** before any public release — "Diablo" is a live Blizzard
  trademark with enforcement precedent against fan-project names.

This repository currently contains only the study. No code yet, and no copyrighted game
assets — ever. Diablo® is a trademark of Blizzard Entertainment, Inc.; this project is not
affiliated with or endorsed by Blizzard Entertainment.
