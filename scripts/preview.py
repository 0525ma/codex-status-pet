#!/usr/bin/env python3
import argparse,functools,http.server,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
def build():
 out=ROOT/'.build/preview';out.mkdir(parents=True,exist_ok=True)
 subprocess.run(['python3',str(ROOT/'guardian/patch-agent.py'),str(ROOT/'tests/fixtures/upstream-agent-0.9.4.cjs'),str(out/'agent.cjs')],check=True)
 shutil.copytree(ROOT/'runtime',out/'status-pet',dirs_exist_ok=True)
 subprocess.run(['node','-e',"const fs=require('fs'),path=require('path'),a=require(path.resolve(process.argv[1]));fs.writeFileSync(process.argv[2],a.buildBootstrapScript());",str(out/'agent.cjs'),str(out/'bootstrap.js')],check=True)
 shutil.copy2(ROOT/'docs/preview.html',out/'index.html');return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--build-only',action='store_true');ap.add_argument('--port',type=int,default=8792);a=ap.parse_args();out=build()
 if not a.build_only:
  print(f'Preview with simulated data: http://127.0.0.1:{a.port}',flush=True)
  http.server.ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(out))).serve_forever()
