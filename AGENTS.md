# Agent instructions

## Releases

DevilTouch runs an open engine and ships no game data, so releases publish the full app (the owner's release formula, 29 Sep 2026: https://github.com/chrissotraidis/padforge/blob/main/docs/DECISIONS.md, D5). Never publish game data, saves or signing material.

Before any public release, every artifact must pass PadForge's content check (`python3 -m padforge audit <artifact>`; archives other than ZIP must be checked as ZIP). A failure is a stop, not a note.
