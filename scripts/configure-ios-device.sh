#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UPSTREAM="$ROOT/upstream/DevilutionX"
BUILD_DIR=${BUILD_DIR:-"$ROOT/build/ios-device"}

command -v cmake >/dev/null 2>&1 || {
	echo "CMake is required." >&2
	exit 1
}

command -v xcodebuild >/dev/null 2>&1 || {
	echo "Xcode command-line tools are required." >&2
	exit 1
}

if [ ! -f "$UPSTREAM/CMakeLists.txt" ]; then
	git -C "$ROOT" submodule update --init upstream/DevilutionX
fi
"$ROOT/scripts/apply-patches.sh" "$BUILD_DIR"

cmake \
	-S "$UPSTREAM" \
	-B "$BUILD_DIR" \
	-G Xcode \
	-DCMAKE_TOOLCHAIN_FILE="$UPSTREAM/CMake/platforms/ios.toolchain.cmake" \
	-DPLATFORM=OS64 \
	-DDEVILTOUCH_IOS_ASSET_CATALOG="$ROOT/platform/ios/Assets.xcassets" \
	-DENABLE_BITCODE=OFF \
	-DDISABLE_ZERO_TIER=ON \
	-DCMAKE_BUILD_TYPE=Release

# Dependency sources exist only after the first configure pass.
"$ROOT/scripts/apply-patches.sh" "$BUILD_DIR"

echo "Configured: $BUILD_DIR"
