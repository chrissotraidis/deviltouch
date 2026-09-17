#!/usr/bin/env python3
"""Record the source identity and executable produced by a completed build."""
import hashlib, json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parents[1]
app = pathlib.Path(sys.argv[1])
if (root/'SOURCE_PROVENANCE.json').exists():
    source=json.loads((root/'SOURCE_PROVENANCE.json').read_text())
else:
    source={'app_commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(), 'dirty':bool(subprocess.check_output(['git','-C',str(root),'status','--porcelain']).strip())}
source['executable_sha256']=hashlib.sha256((app/'devilutionx').read_bytes()).hexdigest()
(app.parent/'deviltouch-build.json').write_text(json.dumps(source,indent=2)+'\n')
