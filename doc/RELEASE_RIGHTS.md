# Release qualification

The original GPL libmpq/Sustainable Use License combination was not suitable
for this release. With explicit authorization on 2026-09-17, DevilTouch replaced
only the archive reader with MIT mpqfs, the backend adopted by upstream
[DevilutionX PR #8482](https://github.com/diasurgical/DevilutionX/pull/8482).
The engine remains based on 1.5.5; the save writer and touch controls are unchanged.
The historical libmpq build recipe is unused. The release graph contains mpqfs,
not libmpq. No third-party license was changed.

## Terms and delivery

| Component | Pin and terms | Delivery |
|---|---|---|
| DevilutionX and DevilTouch | Base `7223eeac9e8274fbf665b4de86fda26d3b22c52f`; maintained pin in `sources.lock.json`; Sustainable Use License 1.0 | Free, non-commercial release, modification notice, full source and terms. |
| mpqfs | `9423bd48d04c8a0c51d3df6ce328e66785e3b441`; MIT | Exact source and copyright/license notice. |
| SDL_audiolib | `cc1bb6af8d4cf5e200259072bde1edd1c8c5137e`; LGPL-3.0-or-later | Library source, GNU GPL/LGPL copies, application source, in-app credit and [rebuild/relink instructions](REBUILDING.md). |
| libsmackerdec | `91e732bb6953489077430572f43fc802bf2c75b2`; LGPL-2.1-or-later | Source including FFmpeg attribution, LGPL copy, application source and rebuild/relink instructions. |
| SDL2, SDL_image, fmt, libpng, libsodium, asio, SimpleIni | Exact declarations in engine `3rdParty/`, complete selected sources in release archive | Component license/copyright files collected in the IPA's `Notices` directory. |
| Embedded helpers and supplemental resources | PKWare/StormLib, PicoSHA2, hoehrmann UTF-8, tl, upstream font/resource terms | Original embedded notices, StormLib MIT notice, upstream OFL/CC-BY/zlib texts and source retained. Apple system zlib/bzip2 remain system libraries. |

The combined application permits personal modification and reverse engineering
for debugging modifications to its LGPL libraries. Those libraries retain their
own LGPL rights; the application's non-commercial terms do not replace them.
Full corresponding library source and application source support the static
relink route described by LGPL 2.1 section 6(a) and LGPL 3 section 4(d)(0).
Recipients sign their own build for AltStore Classic; no maintainer signing key
is required. See [REBUILDING.md](REBUILDING.md).

No retail Diablo/Hellfire MPQs, user saves, private game extraction, provisioning
profiles or signing keys are included. The app does contain upstream supplemental
UI, font and gameplay-support resources. This is not a claim that every resource
is original to DevilTouch, nor a grant of Blizzard game-data or trademark rights.
Users supply legally obtained game data. Distribution must remain free and
non-commercial. There is no endorsement by Blizzard or GOG.

## Evidence and boundaries

The reader comparison covers 1,106 files in five locally owned game archives:
whole reads, stream reads, independent clones and seeking match the old reader.
The mpqfs suite reports 46/46 tests passing (its optional external-save fixture
was absent). This is archive compatibility evidence, not full gameplay acceptance.
The original writer is retained byte-for-byte. Version 1.5.5 build 2 is an iPad
preview; a new physical AltStore installation is not claimed by this qualification.
The dated release validation record distinguishes baseline hardware evidence
from new build, Simulator and source-restoration checks.

## Historical investigation

The old pin `diasurgical/libmpq@b78d66c6fee6a501cc9b95d8556a129c68841b05`
was GPL-2.0-or-later and actually linked. Upstream libmpq's later
[LGPL relicensing](https://github.com/mbroemme/libmpq/blob/f5745cbf55ecf6878b7fc903e39d25723ec6048c/RELICENSING.md)
did not retroactively establish permission for that fork's additional changes.
The selected MIT replacement avoids relying on that unresolved combination.
Source modernization alone did not resolve it; the authorized replacement did.
