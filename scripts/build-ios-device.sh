#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-"$ROOT/build/ios-device"}
DERIVED_DATA_DIR=${DERIVED_DATA_DIR:-"$ROOT/build/ios-device-derived"}
PROJECT="$BUILD_DIR/DevilutionX.xcodeproj"
APP="$BUILD_DIR/Release-iphoneos/devilutionx.app"

"$ROOT/scripts/configure-ios-device.sh"

if [ -n "${DEVELOPMENT_TEAM:-}" ]; then
	xcodebuild \
		-project "$PROJECT" \
		-scheme devilutionx \
		-configuration Release \
		-destination generic/platform=iOS \
		-derivedDataPath "$DERIVED_DATA_DIR" \
		-allowProvisioningUpdates \
		DEVELOPMENT_TEAM="$DEVELOPMENT_TEAM" \
		CODE_SIGN_STYLE=Automatic \
		CODE_SIGNING_ALLOWED=YES \
		CODE_SIGNING_REQUIRED=YES \
		-quiet \
		-jobs "${JOBS:-8}" \
		build
else
	xcodebuild \
		-project "$PROJECT" \
		-scheme devilutionx \
		-configuration Release \
		-destination generic/platform=iOS \
		-derivedDataPath "$DERIVED_DATA_DIR" \
		CODE_SIGNING_ALLOWED=NO \
		CODE_SIGNING_REQUIRED=NO \
		-quiet \
		-jobs "${JOBS:-8}" \
		build
fi

if [ ! -x "$APP/devilutionx" ]; then
	echo "Expected app was not produced: $APP" >&2
	exit 1
fi

if ! file "$APP/devilutionx" | grep -q 'Mach-O 64-bit executable arm64'; then
	echo "Device app is not a native ARM64 executable: $APP/devilutionx" >&2
	exit 1
fi

if [ -n "${DEVELOPMENT_TEAM:-}" ]; then
	codesign --verify --deep --strict "$APP"
	echo "Built and signed for Apple team $DEVELOPMENT_TEAM: $APP"
else
	echo "Built unsigned ARM64 device app: $APP"
	echo "Set DEVELOPMENT_TEAM to create an installable development build."
fi

python3 "$ROOT/scripts/record-build.py" "$APP"
