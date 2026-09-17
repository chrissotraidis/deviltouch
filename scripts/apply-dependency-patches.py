#!/usr/bin/env python3
"""Bounded, hash-verified package compatibility exceptions (not engine patches)."""
import hashlib, json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parents[1]
if len(sys.argv) != 2:
    sys.exit('Usage: apply-dependency-patches.py BUILD_DIR')
for item in json.loads((root / 'sources.lock.json').read_text())['package_patch_exceptions']:
    source = pathlib.Path(sys.argv[1]) / '_deps' / (item['name'] + '-src')
    target = source / item['file']
    if not target.is_file():
        sys.exit('Missing configured dependency: ' + str(target))
    digest = lambda: hashlib.sha256(target.read_bytes()).hexdigest()
    if digest() == item['after_sha256']:
        print(item['name'] + ': verified existing compatibility fix')
        continue
    if digest() != item['before_sha256']:
        sys.exit('Unexpected dependency content; refusing to rewrite ' + str(target))
    subprocess.run(['patch', '-p1', '-f', '-d', str(source), '-i', str(root / item['patch'])], check=True)
    if digest() != item['after_sha256']:
        sys.exit('Dependency patch output mismatch: ' + item['name'])
