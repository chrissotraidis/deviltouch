#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-"$ROOT/build/ios-simulator"}

"$ROOT/scripts/configure-ios-simulator.sh"
cmake --build "$BUILD_DIR" --config Release --target devilutionx -- -quiet -jobs "${JOBS:-8}"

APP="$BUILD_DIR/Release-iphonesimulator/devilutionx.app"
if [ ! -x "$APP/devilutionx" ]; then
	echo "Expected app was not produced: $APP" >&2
	exit 1
fi

echo "Built: $APP"
