#!/bin/sh
# Fetch the iOS SDL pinned in sources.lock.json (SDL 2.32.10 plus the Pad ports
# UIKit scene startup commit) and print its path. Apps built with the iOS 27 SDK
# must start through UIKit scenes or iOS 27 closes them at launch; DevilutionX
# otherwise downloads plain SDL 2.32.0, which has none.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SDL_DIR="$ROOT/build/deps/sdl2-scenes"
SDL_URL=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["ios_sdl"]["repository"])' "$ROOT/sources.lock.json")
SDL_PIN=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["ios_sdl"]["commit"])' "$ROOT/sources.lock.json")

if [ "$(git -C "$SDL_DIR" rev-parse HEAD 2>/dev/null || true)" != "$SDL_PIN" ]; then
	rm -rf "$SDL_DIR"
	git init -q "$SDL_DIR"
	git -C "$SDL_DIR" fetch -q --depth 1 "$SDL_URL" "$SDL_PIN"
	git -C "$SDL_DIR" checkout -q --detach FETCH_HEAD
fi
echo "$SDL_DIR"
