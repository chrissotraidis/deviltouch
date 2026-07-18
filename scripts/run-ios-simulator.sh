#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-"$ROOT/build/ios-simulator"}
APP="$BUILD_DIR/Release-iphonesimulator/devilutionx.app"
BUNDLE_ID=com.chrissotraidis.deviltouch
GAME_DATA_DIR=${1:-}

if [ "${SKIP_BUILD:-0}" != 1 ]; then
	"$ROOT/scripts/build-ios-simulator.sh"
fi

DEVICE=$(xcrun simctl list devices booted | sed -nE 's/^[[:space:]]*iPad.*\(([0-9A-Fa-f-]{36})\) \(Booted\).*/\1/p' | head -n 1)
if [ -z "$DEVICE" ]; then
	DEVICE=$(xcrun simctl list devices available | sed -nE 's/^[[:space:]]*iPad.*\(([0-9A-Fa-f-]{36})\) \(Shutdown\).*/\1/p' | head -n 1)
	if [ -z "$DEVICE" ]; then
		echo "No available iPad Simulator device was found." >&2
		exit 1
	fi
	xcrun simctl boot "$DEVICE"
	xcrun simctl bootstatus "$DEVICE" -b
fi

xcrun simctl terminate "$DEVICE" "$BUNDLE_ID" >/dev/null 2>&1 || true
xcrun simctl install "$DEVICE" "$APP"

if [ -n "$GAME_DATA_DIR" ]; then
	"$ROOT/scripts/import-game-data.sh" "$GAME_DATA_DIR" "$DEVICE"
fi

open -a Simulator --args -CurrentDeviceUDID "$DEVICE"
xcrun simctl launch "$DEVICE" "$BUNDLE_ID"

echo "Launched $BUNDLE_ID on iPad Simulator $DEVICE"
