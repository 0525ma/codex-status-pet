#!/usr/bin/env python3
"""User-invoked launcher; never closes an active Codex window."""
import json,pathlib,plistlib,subprocess,sys
root=pathlib.Path.home()/'Library/Application Support/CodexStatusPetGuardian';s=json.loads((root/'settings.json').read_text())
processes=subprocess.check_output(['/bin/ps','-axo','comm='],text=True).splitlines()
if s['executable'] in [p.strip() for p in processes]:raise SystemExit('Codex is running. Quit it manually with Cmd+Q, then run this launcher again.')
subprocess.run(['/usr/bin/open','-a',s['app'],'--args','--remote-debugging-address=127.0.0.1','--remote-debugging-port=39222'],check=True)
print('Launch requested. The background addon will attempt to attach; this is not visual verification.')
