#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UPSTREAM="$ROOT/upstream/DevilutionX"
BUILD_DIR=${BUILD_DIR:-"$ROOT/build/ios-simulator"}

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
python3 "$ROOT/scripts/verify-sources.py"

case "$(uname -m)" in
	arm64) platform=SIMULATORARM64 ;;
	x86_64) platform=SIMULATOR64 ;;
	*)
		echo "Unsupported Mac architecture: $(uname -m)" >&2
		exit 1
		;;
esac

set --
if [ -f "$ROOT/dependencies.cmake" ]; then
	set -- -C "$ROOT/dependencies.cmake"
fi

cmake "$@" \
	-S "$UPSTREAM" \
	-B "$BUILD_DIR" \
	-G Xcode \
	-DCMAKE_TOOLCHAIN_FILE="$UPSTREAM/CMake/platforms/ios.toolchain.cmake" \
	-DPLATFORM="$platform" \
	-DDEVILTOUCH_IOS_ASSET_CATALOG="$ROOT/platform/ios/Assets.xcassets" \
	-DENABLE_BITCODE=OFF \
	-DDISABLE_ZERO_TIER=ON \
	-DCMAKE_BUILD_TYPE=Release

# Dependency sources exist only after the first configure pass.
python3 "$ROOT/scripts/apply-dependency-patches.py" "$BUILD_DIR"

echo "Configured: $BUILD_DIR"
