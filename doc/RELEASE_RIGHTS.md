# Release qualification: not cleared for publication

The requested new AltStore Classic IPA has **not been published**. No public
GitHub release existed when checked on 2026-09-17. Source maintenance can proceed,
but the current combined binary has a specific unresolved licensing conflict.
This document records evidence and required decisions, not legal clearance.

## Exact components

| Component | Selected source and terms | Release gate |
|---|---|---|
| DevilutionX 1.5.5 and DevilTouch integration | Base `7223eeac9e8274fbf665b4de86fda26d3b22c52f`; Sustainable Use License 1.0 | Free, non-commercial distribution; retain terms and prominent modification notice. No grant is invented for third-party game material or trademarks. |
| libmpq | `diasurgical/libmpq` `b78d66c6fee6a501cc9b95d8556a129c68841b05`; `COPYING` GPL v2 and `libmpq/mpq.c` GPL-2.0-or-later notice | Selected by `3rdParty/libmpq/CMakeLists.txt` as a static library. Reconcile GPL combined-work requirements with engine non-commercial restrictions before binary publication. No applicable exception or alternate permission has been established. A source bundle alone does not resolve this conflict. |
| SDL_audiolib | `realnc/SDL_audiolib` `cc1bb6af8d4cf5e200259072bde1edd1c8c5137e`; LGPL v3 family, `COPYING` and `COPYING.LESSER` | Preserve notices/source and establish the combined-work terms and a tested replacement/relink route for the selected static iOS build. |
| libsmackerdec | `diasurgical/libsmackerdec` `91e732bb6953489077430572f43fc802bf2c75b2`; LGPL-2.1-or-later notices in headers and `COPYING` | Include its source/notices and validate applicable replacement/relink requirements for the static build. |
| Other dependencies | Exact declarations under engine `3rdParty/`; component terms retained in the restored source archive | Verify notices for the exact binary. Do not apply the root SUL to these components. |

The engine's iOS toolchain selects static dependencies; the existing generated
Xcode project contains both libmpq and SDL_audiolib targets. This is an actual
build path, not a concern inferred from unused files elsewhere in upstream.
The engine's inherited `MACOSX_BUNDLE_COPYRIGHT Unlicense` value also requires
correction before publication; it is not evidence that the selected engine is
unlicensed or permissively licensed.

## Recheck: the current pin is blocked, not every future IPA

On 2026-09-17, a second upstream check found two developments that the initial
review missed:

- libmpq was relicensed to LGPL-2.1-or-later beginning with commit
  `f5745cbf55ecf6878b7fc903e39d25723ec6048c`, and that change is included in
  [v0.5.0](https://github.com/mbroemme/libmpq/releases/tag/v0.5.0). The
  [relicensing record](https://github.com/mbroemme/libmpq/blob/f5745cbf55ecf6878b7fc903e39d25723ec6048c/RELICENSING.md)
  documents contributor approvals. This does not establish LGPL coverage of our
  older diasurgical fork commit or its additional changes, and does not change
  the license notices in our selected source.
- Upstream DevilutionX merged [PR #8482](https://github.com/diasurgical/DevilutionX/pull/8482),
  replacing libmpq with MIT-licensed mpqfs. The maintainers describe this in
  [discussion #7556](https://github.com/diasurgical/DevilutionX/discussions/7556).
  Our fixed 1.5.5 base does not contain that replacement.

The current app explicitly calls libmpq from `Source/mpq/mpq_reader.cpp`, and
its generated device link flags include `liblibmpq.a`. Thus the old dependency
is active, not an unused source-tree artifact. No applicable linking exception
was found in the selected package's license and accompanying notices.

An IPA is technically buildable; the blocker concerns distributing this exact
license combination, not the IPA format or all uses of libmpq. A separately
scoped update to the LGPL release (with downstream-delta review and LGPL
replacement/relink delivery), or a validated mpqfs backport, provides a concrete
potential path forward. Neither is silently included in this behavior-preserving
migration, and neither is automatic clearance for the rest of the package.

## Remaining action

Establish a documented compatible permission basis for the exact libmpq/engine
combination, or separately authorize and validate a compatible replacement.
Do not silently replace MPQ handling, remove game functionality, relicense
third-party work, or contact upstream authors as part of this migration.
Then finish LGPL replacement/relink delivery, packaged notices and provenance,
versioned IPA packaging, and AltStore Classic installation acceptance.

A future release should provide the exact source archive, component notices,
provenance and checksums alongside the IPA. Audit bundle version, deployment
minimum, entitlements, game-data absence and actual included resources. AltStore
Classic re-signs for the recipient: it does not resolve these source licenses.
When publishing, download every public asset anonymously and compare hashes.
No new device signing, installation or gameplay acceptance is claimed here.

## References

- [Pinned engine license](https://github.com/diasurgical/DevilutionX/blob/7223eeac9e8274fbf665b4de86fda26d3b22c52f/LICENSE.md)
- [libmpq source notice](https://github.com/diasurgical/libmpq/blob/b78d66c6fee6a501cc9b95d8556a129c68841b05/libmpq/mpq.c)
- [SDL_audiolib license](https://github.com/realnc/SDL_audiolib/blob/cc1bb6af8d4cf5e200259072bde1edd1c8c5137e/COPYING.LESSER)
- [GNU GPL compatibility guidance](https://www.gnu.org/licenses/gpl-faq.html#GPLIncompatibleLibs)
- [AltStore source format](https://faq.altstore.io/developers/make-a-source)
