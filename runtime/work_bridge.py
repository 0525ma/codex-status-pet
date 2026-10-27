import json,time
from monitor import scan,DATA
while True:
 try:
  scan();print(json.dumps({'threads':DATA['threads'],'checkedAt':time.time(),'connection':DATA['connection']},ensure_ascii=False),flush=True)
 except (BrokenPipeError,KeyboardInterrupt):break
 time.sleep(1.5)
