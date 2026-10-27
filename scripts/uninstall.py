#!/usr/bin/env python3
"""Restore the installation backup. Keep user backups and local assets."""
import json,os,pathlib,shutil,subprocess,sys,time
home=pathlib.Path.home();root=home/'Library/Application Support/CodexStatusPetGuardian';settings=root/'settings.json'
if not settings.exists():raise SystemExit('No installed addon receipt found.')
s=json.loads(settings.read_text());backup=pathlib.Path(s['backup']);base=pathlib.Path(s['baseDir'])
for name in ['agent.cjs','updater/worker.cjs','update-settings.json']:
 if not (backup/name).is_file():raise SystemExit('Missing recovery file: '+name)
subprocess.run(['launchctl','bootout',f'gui/{os.getuid()}/com.codexstatuspet.guardian'],check=False)
plist=home/'Library/LaunchAgents/com.codexstatuspet.guardian.plist'
if plist.exists():plist.rename(root/'disabled-launch-agent.plist')
for name in ['agent.cjs','updater/worker.cjs','update-settings.json']:shutil.copy2(backup/name,base/name)
for label in ['agent','startup']:
 name=f'com.codexusagebadge.{label}.plist';src=backup/name
 if src.exists():shutil.copy2(src,home/'Library/LaunchAgents'/name)
for label in ['agent','startup']:
 job=f'gui/{os.getuid()}/com.codexusagebadge.{label}'
 subprocess.run(['launchctl','bootout',job],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for _ in range(40):
  if subprocess.run(['launchctl','print',job],capture_output=True).returncode:break
  time.sleep(.25)
 subprocess.run(['launchctl','bootstrap',f'gui/{os.getuid()}',str(home/f'Library/LaunchAgents/com.codexusagebadge.{label}.plist')],check=True)
settings.rename(root/'uninstalled-settings.json')
print('Restored the prior badge files. Backups and custom assets remain on disk. Reopen Codex manually if stale UI remains.')
