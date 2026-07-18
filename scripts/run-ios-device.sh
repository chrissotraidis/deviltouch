#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-"$ROOT/build/ios-device"}
APP="$BUILD_DIR/Release-iphoneos/devilutionx.app"
BUNDLE_ID=com.chrissotraidis.deviltouch

if [ -z "${DEVELOPMENT_TEAM:-}" ]; then
	echo "Set DEVELOPMENT_TEAM to the 10-character team ID from your Apple Development certificate." >&2
	exit 1
fi

if [ "${SKIP_BUILD:-0}" != 1 ]; then
	"$ROOT/scripts/build-ios-device.sh"
fi

if [ -z "${DEVICE_ID:-}" ]; then
	available_devices=$(xcrun devicectl list devices \
		--filter "Name CONTAINS 'iPad' AND State BEGINSWITH 'available'" \
		--columns Identifier \
		--hide-default-columns \
		--hide-headers)
	DEVICE_ID=$(printf '%s\n' "$available_devices" | sed -n '1p')
	second_device=$(printf '%s\n' "$available_devices" | sed -n '2p')
	if [ -n "$second_device" ]; then
		echo "More than one available iPad was found. Set DEVICE_ID to the intended CoreDevice identifier." >&2
		exit 1
	fi
fi

if [ -z "$DEVICE_ID" ]; then
	echo "No available paired iPad was found. Connect it, unlock it, and enable Developer Mode." >&2
	exit 1
fi

xcrun devicectl device install app --device "$DEVICE_ID" "$APP"
xcrun devicectl device process launch --device "$DEVICE_ID" --terminate-existing "$BUNDLE_ID"

echo "Installed and launched $BUNDLE_ID on iPad $DEVICE_ID"
