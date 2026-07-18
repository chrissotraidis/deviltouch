#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

blocked=$(git -C "$ROOT" ls-files | awk '
	BEGIN { IGNORECASE = 1 }
	/^ref\// || /\.(mpq|exe|dll|bik|smk|snp)$/ { print }
')

if [ -n "$blocked" ]; then
	echo "Proprietary game files are tracked:" >&2
	echo "$blocked" >&2
	exit 1
fi

if ! git -C "$ROOT" check-ignore -q ref/.asset-sentinel; then
	echo "The ref/ asset directory is not ignored." >&2
	exit 1
fi

echo "No proprietary game assets are tracked; ref/ is ignored."
