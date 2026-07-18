#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SOURCE_DIR=${1:-"$ROOT/ref/Diablo"}
DEVICE=${2:-booted}
BUNDLE_ID=com.chrissotraidis.deviltouch

if [ ! -d "$SOURCE_DIR" ]; then
	echo "Game-data directory not found: $SOURCE_DIR" >&2
	exit 1
fi

APP_DATA=$(xcrun simctl get_app_container "$DEVICE" "$BUNDLE_ID" data)
DOCUMENTS="$APP_DATA/Documents"
mkdir -p "$DOCUMENTS"

find_asset()
{
	find "$SOURCE_DIR" -type f -iname "$1" -print -quit
}

copied_base=0
for asset in diabdat.mpq spawn.mpq hellfire.mpq hfmonk.mpq hfmusic.mpq hfvoice.mpq; do
	source_file=$(find_asset "$asset")
	if [ -z "$source_file" ]; then
		continue
	fi
	cp "$source_file" "$DOCUMENTS/$asset"
	echo "Imported $asset"
	case "$asset" in
		diabdat.mpq|spawn.mpq) copied_base=1 ;;
	esac
done

if [ "$copied_base" -ne 1 ]; then
	echo "No diabdat.mpq or spawn.mpq was found under $SOURCE_DIR" >&2
	exit 1
fi

echo "Imported user-owned game data into the Simulator app container."
