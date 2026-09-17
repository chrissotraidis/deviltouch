# Rebuild and replace LGPL libraries

The release's `deviltouch-source.tar.gz` contains the exact application, engine,
all ten nested dependency source trees, their licenses and local CMake inputs.
The automatic GitHub source zip does not contain these nested sources.

On an Apple Silicon Mac with Xcode 26.6 (iOS SDK 26.5), CMake 4.4.2 and Python 3:

```sh
tar -xzf deviltouch-source.tar.gz
cd deviltouch-source
python3 scripts/verify-sources.py
BUILD_DIR="$PWD/build/device" scripts/build-ios-device.sh
```

Source retrieval is disconnected: `dependencies.cmake` points to the included
sources and disables FetchContent downloads. Xcode and the Apple SDK are system
build tools obtained separately from Apple; signing may require network access.

To replace either LGPL library, first verify the archive, then edit
`dependencies/sdl_audiolib` and/or `dependencies/libsmackerdec`. Keep their
public interfaces compatible. Rebuild and relink the application:

```sh
DEVILTOUCH_REBUILD_LGPL=1 BUILD_DIR="$PWD/build/personal" scripts/build-ios-device.sh
mkdir -p build/personal-ipa/Payload
cp -R build/personal/Release-iphoneos/devilutionx.app build/personal-ipa/Payload/
cd build/personal-ipa
zip -qr ../DevilTouch-personal.ipa Payload
```

This explicit mode permits edits to those two library trees while checking the
remaining source manifest. It does not label the result an audited release.
The complete application source is supplied so you can also make changes needed
to relink it. Ordinary source/archive verification intentionally detects edits;
it is not an access control or a restriction on permitted modification.

For personal builds, retain the release IPA's `Notices` directory and
`BUILD_PROVENANCE.json` in your rebuilt app, marking provenance as modified
before signing. The official packaging command rejects personal rebuild mode.

Install AltStore Classic using its official AltServer instructions. In My Apps,
use + to select the IPA; AltStore signs it with your own Apple account. No
maintainer signing key is needed. For an existing installation, preserve its
bundle identifier and signing team, back up the entire app data container and
update in place. If the signer or app identity differs, stop: do not uninstall
to work around it. Retain your known-good IPA and complete data backup for rollback.

The combined work permits modification for your own use and reverse engineering
for debugging modifications to the LGPL libraries. The libraries retain their
LGPL rights; the root Sustainable Use License does not replace their licenses.
Rebuilding does not grant rights to distribute retail game data or trademarks.
