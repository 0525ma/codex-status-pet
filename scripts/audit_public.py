#!/usr/bin/env python3
import pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
try:files=[ROOT/p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).splitlines()]
except subprocess.CalledProcessError:files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','.build','__pycache__'])]
if not files:files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','.build','__pycache__'])]
patterns=[r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'/Users/[^/\s]+/',r'pet_[a-f0-9]{32}']
errors=[]
for p in files:
 rel=str(p.relative_to(ROOT))
 if p.name in ['auth.json','status.json','settings.json','geometry-data.js'] or any(x in p.parts for x in ['backups','sessions','memories_v2']):errors.append(rel+': disallowed artifact')
 if rel=='docs/preview.png':continue
 if p.suffix in ['.png','.gif','.webp','.mp4','.apk','.sqlite']:errors.append(rel+': unexpected binary asset')
 try:s=p.read_text()
 except UnicodeDecodeError:errors.append(rel+': unexpected binary');continue
 if p.name=='audit_public.py':continue
 for pat in patterns:
  if re.search(pat,s):errors.append(rel+': sensitive-pattern match')
 if re.search(r'window\.GROK_GEO\s*=|class GrokCharacter',s):errors.append(rel+': restricted study implementation')
if errors:print('\n'.join(errors));sys.exit(1)
print(f'Public audit passed: {len(files)} files, no detected restricted assets, machine paths, or common secret patterns.')
