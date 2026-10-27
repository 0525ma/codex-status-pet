#!/usr/bin/env python3
"""Install the addon over a compatible, already-installed MIT Codex Usage Badge."""
import argparse,hashlib,json,os,pathlib,plistlib,shutil,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def assemble(base,out,node):
 out.mkdir(parents=True,exist_ok=True)
 for name in ['guardian.cjs','patch-agent.py','connection-health.cjs']:shutil.copy2(ROOT/'guardian'/name,out/name)
 shutil.copy2(ROOT/'runtime/install-pet.js',out/'install-pet.js')
 shutil.copytree(ROOT/'runtime',out/'status-pet',dirs_exist_ok=True)
 subprocess.run([sys.executable,str(out/'patch-agent.py'),str(base/'agent.cjs'),str(out/'agent.cjs')],check=True)
 subprocess.run([node,'--check',str(out/'agent.cjs')],check=True)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base-dir',type=pathlib.Path,default=pathlib.Path.home()/'Library/Application Support/CodexUsageBadge');ap.add_argument('--dry-run',action='store_true');ap.add_argument('--auto-update',action='store_true',help='Opt in to compatible upstream badge upgrades, never update the Codex desktop app itself.');args=ap.parse_args()
 node=shutil.which('node')
 if not node:raise SystemExit('Node.js 24+ is required.')
 major=int(subprocess.check_output([node,'-p','process.versions.node.split(".")[0]'],text=True));assert major>=24,'Node.js 24+ is required.'
 base=args.base_dir.resolve()
 for name in ['agent.cjs','installed-version.json','updater/core.cjs','updater/worker.cjs','update-settings.json']:
  if not (base/name).is_file():raise SystemExit('Install upstream Codex Usage Badge first; missing '+name)
 original=(base/'agent.cjs').read_text()
 if 'function installGrokQuotaPet()' in original:raise SystemExit('Existing private Grok customization detected. Back it up and restore upstream before installing the public addon.')
 with tempfile.TemporaryDirectory(prefix='codex-status-pet-') as temp:
  stage=assemble(base,pathlib.Path(temp),node)
  print('Preflight passed. SHA256:',hashlib.sha256((stage/'agent.cjs').read_bytes()).hexdigest())
  if args.dry_run:print('Dry run: no installed files or launch jobs changed.');return
  if sys.platform!='darwin':raise SystemExit('Installation currently supports macOS only; dry-run checks work elsewhere.')
  home=pathlib.Path.home();dest=home/'Library/Application Support/CodexStatusPetGuardian'
  if (dest/'settings.json').exists():raise SystemExit('Addon already installed. Uninstall or review an explicit upgrade before replacing it.')
  backup=dest/'backups'/time.strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True)
  for name in ['agent.cjs','updater/worker.cjs','update-settings.json']:
   (backup/name).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/name,backup/name)
  for label in ['agent','startup']:
   p=home/f'Library/LaunchAgents/com.codexusagebadge.{label}.plist'
   if p.exists():shutil.copy2(p,backup/p.name)
  receipt=json.loads((base/'installed-version.json').read_text());app=pathlib.Path(receipt['app']);info=plistlib.loads((app/'Contents/Info.plist').read_bytes());exe=app/'Contents/MacOS'/info['CFBundleExecutable']
  target=home/'Library/LaunchAgents/com.codexstatuspet.guardian.plist'
  if target.exists():raise SystemExit('An existing guardian launch file requires review; not overwritten.')
  try:
   for name in ['guardian.cjs','patch-agent.py','connection-health.cjs','install-pet.js']:shutil.copy2(stage/name,dest/name)
   shutil.copytree(stage/'status-pet',dest/'status-pet',dirs_exist_ok=True);shutil.copytree(stage/'status-pet',base/'status-pet',dirs_exist_ok=True)
   (dest/'settings.json').write_text(json.dumps({'node':node,'app':str(app),'executable':str(exe),'baseDir':str(base),'backup':str(backup)},indent=2))
   shutil.copy2(stage/'agent.cjs',base/'agent.cjs')
   settings=json.loads((base/'update-settings.json').read_text());settings['enabled']=args.auto_update;settings['allowPrerelease']=False;(base/'update-settings.json').write_text(json.dumps(settings)+'\n')
   plist={'Label':'com.codexstatuspet.guardian','ProgramArguments':[node,str(dest/'guardian.cjs'),'daemon'],'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':10,'ProcessType':'Background','StandardOutPath':str(home/'Library/Logs/CodexStatusPetGuardian.out.log'),'StandardErrorPath':str(home/'Library/Logs/CodexStatusPetGuardian.err.log')}
   target=home/'Library/LaunchAgents/com.codexstatuspet.guardian.plist';target.parent.mkdir(exist_ok=True);target.write_bytes(plistlib.dumps(plist))
   subprocess.run(['launchctl','bootstrap',f'gui/{os.getuid()}',str(target)],check=True)
   subprocess.run(['launchctl','kickstart','-k',f'gui/{os.getuid()}/com.codexusagebadge.agent'],check=True)
  except Exception:
   subprocess.run(['launchctl','bootout',f'gui/{os.getuid()}/com.codexstatuspet.guardian'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   for name in ['agent.cjs','updater/worker.cjs','update-settings.json']:shutil.copy2(backup/name,base/name)
   if target.exists():target.rename(dest/'failed-launch-agent.plist')
   if (dest/'settings.json').exists():(dest/'settings.json').rename(dest/'failed-settings.json')
   subprocess.run(['launchctl','kickstart','-k',f'gui/{os.getuid()}/com.codexusagebadge.agent'],check=False)
   raise
  print('Addon installed. The Codex window was not restarted. See README if the attachment port is unavailable.')
if __name__=='__main__':main()
