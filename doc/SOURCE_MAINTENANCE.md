# DevilTouch source maintenance

## Scope and plan

Preserve the existing repository, product and DevilutionX 1.5.5. First capture
and restore the complete checkout, then compare the six-patch prepared engine,
commit that exact source to an upstream-connected fork, switch both Apple build
paths to its immutable pin, and validate builds and source archive restoration.
Qualify a new free AltStore Classic IPA only after the release rights gates pass.
No engine upgrade, gameplay feature, device installation or upstream outreach is
part of this maintenance change.

## Source graph

The original app baseline is `7f609ed22afc75fdfe4ff05f27e486e9bd14a253`.
Its official engine submodule base is
`7223eeac9e8274fbf665b4de86fda26d3b22c52f` (1.5.5).
The preserved local engine had 26 changed files, all exactly reproduced by the
six checked-in iOS patches: no additional private engine changes were selected.
All 1,100 original tracked files matched in bytes and modes.

The selected [maintained fork](https://github.com/chrissotraidis/DevilutionX/tree/deviltouch/ios-1.5.5)
is a GitHub-connected fork of `diasurgical/DevilutionX` (verified via the GitHub
API). Commit `05d557e057cb7bda3825514e1c292daff56b7569` contains the existing
integration; `ecff940dd0fc0f9debc877578b194eedd0faeef5` adds its branch and
modification notice. The gitlink and `sources.lock.json` select that exact commit.
The engine remains under its Sustainable Use License; no license is replaced.

Both `configure-ios-device.sh` and `configure-ios-simulator.sh` consume this same
engine, `platform/ios/game_data_import.m` and its header, and the existing icon
catalog. Device is ARM64/iOS; Simulator selects ARM64 or x86_64 for the host.
iPad is the product's tested focus. No macOS, Android or tvOS release is claimed
merely because the upstream engine supports those platforms.

All six `patches/ios/*.patch` files map to engine commit `05d557e057cb7bda3825514e1c292daff56b7569`.
They are historical evidence, never replayed by normal builds. The existing
`apply-patches.sh` name is retained only as a read-only verification entry point.
There is no generated proprietary game source in this integration.

## Bounded package exceptions

The fmt 10.0.0 and libpng `0a158f3506502dfa23edfc42790dfaed82efba17` patches
remain package compatibility exceptions, owned by DevilTouch maintainers.
They change three fmt formatting calls and one libpng Apple header condition;
they are not the source of touch, importer, renderer or gameplay behavior.
`sources.lock.json` records upstreams, exact input/output SHA-256 and purpose.
The preparer rejects unexpected source, verifies its output and is idempotent.
These exceptions should be removed only in a separate dependency upgrade that
proves the compiler issue is fixed upstream. No upgrade occurred here.

Other dependencies remain pinned in the engine's `3rdParty/*/CMakeLists.txt`.
Apple builds select SDL2, SDL_image, SDL_audiolib, libfmt, libpng, libmpq,
libsmackerdec, libsodium (including its nested source), asio and simpleini.
Apple SDK zlib/bzip2 and system frameworks are toolchain inputs, not privately
vendored libraries. Keep every component's own license and notices.

## Building and updating

```sh
git clone --recurse-submodules https://github.com/chrissotraidis/deviltouch.git
cd deviltouch
python3 scripts/verify-sources.py
./scripts/build-ios-device.sh
./scripts/build-ios-simulator.sh
```

The engine verifier fails on a wrong commit or dirty/untracked engine files.
Do not reset dirty sources to make it pass. Preserve work on a branch first.
Source releases use clean app commits and include nested dependency source.

New engine fixes belong in ordinary commits on `deviltouch/ios-1.5.5`.
Compare against the recorded base with `git diff BASE..HEAD`; review and test
before advancing the app gitlink and lock together. Do not change a shared
fork's default branch or silently upgrade another app. Upstream contributions
must be independently scoped, and require explicit authorization to submit.
Reports start with DevilTouch until evidence identifies an upstream issue.

## Source archive and rollback

After configuring/building and committing intended app changes:

```sh
python3 scripts/source-archive.py build/ios-device /absolute/output/deviltouch-source.tar.gz
mkdir /absolute/new/restore
tar -xzf /absolute/output/deviltouch-source.tar.gz -C /absolute/new/restore
cd /absolute/new/restore/deviltouch-source
python3 scripts/verify-sources.py
./scripts/build-ios-device.sh
```

The archive contains the exact committed app and engine, all configured nested
dependency sources, individual license files, SHA-256/mode manifest and a CMake
initial cache selecting the included sources with FetchContent disconnected.
Xcode, its SDK, CMake and gettext remain required host tools. No Git repository,
private checkout, game data or downloaded release package is required to restore
these software sources. This is source completeness evidence, not clearance to
distribute the combined binary; see [release rights](RELEASE_RIGHTS.md).

Rollback is demonstrated in a separate restored baseline checkout: its original
Git history, dirty prepared engine, scripts and build outputs are retained.
For source-only comparison, check out app baseline `7f609ed22afc75fdfe4ff05f27e486e9bd14a253`
in a disposable directory, initialize its original submodule, and run the old
`./scripts/apply-patches.sh`. Never run a reset on the working product or remove
an installed app. Private backup paths and signing evidence stay in the local
handoff, outside public source. In-place device recovery requires the same bundle
and signing identity and a separately backed-up complete app container; no device
was used or modified for this task.
