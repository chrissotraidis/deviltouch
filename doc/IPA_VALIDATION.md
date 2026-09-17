# IPA candidate validation — 17 September 2026

Version 1.5.5 build 2 retains the existing iPad product, touch controls, importer
and save writer. Source modernization was merged in PR #1. The authorized
release follow-up replaces GPL libmpq with MIT mpqfs, without an engine upgrade.
Exact commits are recorded by `sources.lock.json` and packaged provenance.

## Archive compatibility

- mpqfs `9423bd48d04c8a0c51d3df6ce328e66785e3b441`: 46/46 upstream tests pass;
  optional external save fixture absent.
- Differential adapter test: 1,106 matching file reads across Diablo, Hellfire,
  music, voice and monk archives. Compared complete bytes, 997-byte stream
  chunks, clone-owned streams, object counts, mid-file seeks and end-of-file.
- 1,128 literal asset path candidates were collected from the unchanged engine;
  canonical MPQ backslashes were used for comparison. mpqfs additionally accepts
  forward slashes, unlike old libmpq.
- Retail archive contents and comparison outputs remain private. No game data
  or personal save was committed. `mpq_writer.cpp` is unchanged from the baseline.

## Build and delivery checks

The release requires device and Simulator builds, an audited unsigned package,
a complete nested source restore and a modified-library rebuild. Final package
identities are in the accompanying provenance and SHA256SUMS release assets.
New physical AltStore installation and exhaustive gameplay are not claimed.
The earlier physical-iPad playtest remains documented separately in PLAYTEST.md.

## Recovery

The original dirty checkout, full Git history, local game data and accepted apps
are preserved privately outside the checkout on the same physical disk. The
backup and independent restore matched 33,747 manifest entries. A reverse/reapply
rehearsal matched 1,100 original engine files. This is a same-disk recovery copy,
not protection against disk failure.

For source rollback, use a disposable checkout of app commit
`9ce31c245f0fc68a5696ae57e8cd70416fcebf95`, then initialize its submodule. This
restores the source-maintenance baseline including the old reader; its binary
must not be republished with the unresolved GPL combination. Do not reset the
original dirty working directory. For device rollback, retain the known-good
IPA and full container backup, keep the same signer/bundle ID and update in place.
