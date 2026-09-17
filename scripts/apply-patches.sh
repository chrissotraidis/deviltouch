#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
echo "Engine patch replay is retired. Verifying maintained source instead."
exec python3 "$ROOT/scripts/verify-sources.py"
