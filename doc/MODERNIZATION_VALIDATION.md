# Source-maintenance validation — 17 September 2026

Source migration is implemented in [PR #1](https://github.com/chrissotraidis/deviltouch/pull/1),
not merged. IPA publication remains blocked by [component-specific rights and
relink gates](RELEASE_RIGHTS.md). No public release, new hardware installation or
new gameplay acceptance is claimed.

## Evidence

- Original app: `7f609ed22afc75fdfe4ff05f27e486e9bd14a253`.
- Engine base: `7223eeac9e8274fbf665b4de86fda26d3b22c52f`; maintained pin:
  `ecff940dd0fc0f9debc877578b194eedd0faeef5`.
- Engine source: all 1,100 baseline files match before the one added branch
  notice; all six historical patches map to `05d557e057cb7bda3825514e1c292daff56b7569`.
- Dependencies: all 7,105 files across the ten selected package source trees
  match the preserved device baseline, including nested libsodium.
- Backup: full private checkout independently restored; 33,747 entries verified
  with SHA-256, modes and symlinks. Backup is on the same physical disk.
- Rollback: in a disposable source copy, reverse the six patches to the exact
  upstream Git blobs (including symlinks), then reapply to the exact prepared tree.
- Builds: ARM64 device and ARM64 Simulator both pass with Xcode 26.6 (17F113),
  iOS SDK 26.5 and CMake 4.4.2. Existing upstream warnings remain.
- Source delivery: local source archive restored without Git, 8,254 manifest
  entries verified, then a complete ARM64 device rebuild passed using included
  dependencies and `FETCHCONTENT_FULLY_DISCONNECTED=ON`. The CMake cache contains
  no original checkout or task-worktree paths. Manifest still verifies afterward.
- Guards: mismatch between lock and gitlink rejected; dirty/untracked engine
  rejected without deleting it; package patch idempotence and unexpected-input
  rejection pass; archive content/mode tampering rejected. Hosted source CI passes.
- Runtime: fresh iPad Simulator on iOS 26.5 installed/launched successfully and
  showed the first-run native Files picker. No game data was imported. Temporary
  Simulator was shut down and removed; physical hardware remained untouched.

## Local artifact identities

These are local qualification artifacts, not published releases or signed IPAs.

| Artifact | SHA-256 |
|---|---|
| Device executable | `b20a2e4e8f27b996e7b081777c74ac9f17b2394b8f258b4a3c782de6b6a0fb8d` |
| Simulator executable | `6200ca4dcf13f0d6ab6d615a191cab61f638b6aee715a7c42261d8fc0577303c` |
| Restored source archive | `75344dbf708bb9d1e6904bbf8a02458171ccb2eb1d4658f46998b258a9e74efc` |

The source archive's exact app commit is recorded in its `SOURCE_PROVENANCE.json`;
it includes the source-export implementation before this evidence-only document.
The device app remains unsigned and has no embedded provisioning profile.
Bundle ID stays `com.chrissotraidis.deviltouch`, version/build `1.5.5`, minimum
OS `13.0`, device families `[1, 2]`. No version increment is presented as a release.
No retail MPQs, saves or provisioning profiles were found in these app bundles.
The existing upstream supplemental resources, including `.dun` maps, remain;
their presence is not a claim that all game-derived material is cleared.
All 138 checked device resource files match the preserved package. Simulator
resources match except two generated app-icon PNGs; the tracked icon source is
unchanged. This is not a claim of bit-identical whole-app output across builds.

The complete private recovery handoff includes original package/signing
identities and the full checkout. It is deliberately excluded from public source.
Use [source maintenance](SOURCE_MAINTENANCE.md) for portable restoration and rollback
commands; do not overwrite the original dirty checkout or reset device data.
