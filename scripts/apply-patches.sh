#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UPSTREAM="$ROOT/upstream/DevilutionX"
BUILD_DIR=${1:-"$ROOT/build/ios-simulator"}

apply_git_patch()
{
	target=$1
	patch_file=$2
	label=$3

	if git -C "$target" apply --reverse --check "$patch_file" >/dev/null 2>&1; then
		echo "$label already applied"
	elif git -C "$target" apply --check "$patch_file" >/dev/null 2>&1; then
		git -C "$target" apply "$patch_file"
		echo "Applied $label"
	else
		echo "Cannot apply $label cleanly" >&2
		exit 1
	fi
}

apply_source_patch()
{
	target=$1
	patch_file=$2
	label=$3

	if [ ! -d "$target" ]; then
		return
	fi

	if patch -p1 -d "$target" -R -f -s --dry-run < "$patch_file"; then
		echo "$label already applied"
	elif patch -p1 -d "$target" -N -f -s --dry-run < "$patch_file"; then
		patch -p1 -d "$target" -N -f -s < "$patch_file"
		echo "Applied $label"
	else
		echo "Cannot apply $label cleanly" >&2
		exit 1
	fi
}

if [ ! -f "$UPSTREAM/CMakeLists.txt" ]; then
	echo "DevilutionX is not initialized. Run scripts/configure-ios-simulator.sh first." >&2
	exit 1
fi

apply_git_patch \
	"$UPSTREAM" \
	"$ROOT/patches/ios/deviltouch-app-identity.patch" \
	"DevilTouch app-identity patch"

apply_git_patch \
	"$UPSTREAM" \
	"$ROOT/patches/ios/touch-controls-clear-hud.patch" \
	"iPad direct-touch patch"

apply_git_patch \
	"$UPSTREAM" \
	"$ROOT/patches/ios/xcode-managed-device-family.patch" \
	"Xcode-managed device-family patch"

apply_source_patch \
	"$BUILD_DIR/_deps/libpng-src" \
	"$ROOT/patches/dependencies/libpng-xcode26-target-os-mac.patch" \
	"libpng Xcode 26 patch"

apply_source_patch \
	"$BUILD_DIR/_deps/libfmt-src" \
	"$ROOT/patches/dependencies/fmt10-xcode26-consteval.patch" \
	"fmt 10 Xcode 26 patch"
