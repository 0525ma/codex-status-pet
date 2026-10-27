import datetime,json,os,pathlib,re,sqlite3,time,threading
CODEX=pathlib.Path(os.environ.get('CODEX_HOME',str(pathlib.Path.home()/'.codex')))
LOCK=threading.RLock(); DATA={'threads':[],'events':[],'connection':'starting'}
POS={};THREADS={};TARGET=None
TOOL_MAP=[('request_user_input','listening','等待输入'),('web__|search_query|search_plugins|search_notes|web_search','searching','检索资料'),('imagegen|image_generate','spawning','生成图像'),('compile|assemble|build|gradle','working','构建执行'),('apply_patch|write_file|writeFile|edit_file','writing','修改文件'),('spawn_agent|followup_task|send_message','orbit','协同任务'),('wait_agent|wait_threads|sleep|write_stdin|functions.wait','humming','等待工具'),('exec_command|exec|shell','working','执行工具')]
def classify(v):
 typ=v.get('type');p=v.get('payload',{});k=p.get('type');name=p.get('name','')
 if typ=='event_msg':
  if k in ('task_started','turn_started'):return 'thinking','开始处理','event'
  if k in ('task_complete','task_completed','turn_complete','turn_completed'):return 'happy','本轮完成','event'
  if k in ('turn_aborted','task_aborted'):return 'sad','已中断','event'
  if k in ('error','stream_error'):return 'alerting','执行出错','event'
  if k in ('request_user_input','user_input_requested'):return 'listening','等待输入','event'
  if k=='item_completed':
   item=p.get('item',{});it=item.get('type','')
   if it in ('reasoning','Reasoning'):return 'thinking','思考中','event'
   if it in ('webSearch','web_search'):return 'searching','搜索中','event'
   if it in ('plan','Plan'):return 'progress','规划进度','event'
 if typ=='response_item':
  if k=='reasoning':return 'thinking','思考中','event'
  if k=='message' and p.get('role')=='user':return 'receiving','收到任务','event'
  if k=='message' and p.get('role')=='assistant':
   if p.get('phase')=='final_answer':return 'happy','回复已完成','event'
   return 'sending','输出回复','event'
  if k in ('function_call','custom_tool_call'):
   # Classify names only. Tool arguments are never persisted or exposed.
   hints=name+' '+str(p.get('namespace',''))+' '+' '.join(re.findall(r'tools\.([a-zA-Z0-9_]+)\s*\(',str(p.get('input',''))[:12000]))
   for pattern,state,label in TOOL_MAP:
    if re.search(pattern,hints):return state,label,'mapped'
   return 'working','调用工具','event'
  if k in ('function_call_output','custom_tool_call_output'):
   out=p.get('output','')
   if isinstance(out,str):
    try:out=json.loads(out)
    except ValueError:pass
   if isinstance(out,dict) and (out.get('isError') or out.get('exit_code',0)):return 'alerting','工具返回错误','event'
   return 'thinking','工具返回，继续处理','event'
 return None

def read_threads():
 db=CODEX/'state_5.sqlite'
 if not db.exists():raise RuntimeError('未找到本机Codex任务数据库')
 c=sqlite3.connect(f'file:{db}?mode=ro',uri=True,timeout=1)
 try:
  rows=c.execute('SELECT id,COALESCE(name,id),rollout_path,updated_at FROM threads WHERE archived=0 ORDER BY updated_at DESC LIMIT 24').fetchall()
  if TARGET and not any(r[0]==TARGET for r in rows):
   rows+=c.execute('SELECT id,COALESCE(name,id),rollout_path,updated_at FROM threads WHERE id=?',(TARGET,)).fetchall()
  return rows
 finally:c.close()

def scan():
 try:
  rows=read_threads()
  for tid,title,filename,updated in rows:
   if len(title)>100 or "\n" in title:title="聊天 "+tid[:8]
   path=pathlib.Path(filename)
   if not path.exists():continue
   size=path.stat().st_size;start=POS.get(tid,max(0,size-100000))
   if start>size:start=max(0,size-100000)
   if size==start:continue
   with path.open('rb') as f:
    f.seek(start)
    if tid not in POS and start:f.readline()
    while True:
     pos=f.tell();line=f.readline()
     if not line:POS[tid]=f.tell();break
     if not line.endswith(b'\n'):POS[tid]=pos;break
     try:v=json.loads(line)
     except (ValueError,UnicodeDecodeError):continue
     state=classify(v)
     if not state:continue
     stamp=v.get('timestamp','');ts=time.time()
     try:ts=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00')).timestamp()
     except (ValueError,AttributeError):pass
     old=THREADS.get(tid)
     info={'id':tid,'title':title,'state':state[0],'label':state[1],'evidence':state[2],'eventAt':ts}
     THREADS[tid]=info
     if old and old['state']!=info['state'] and time.time()-ts<10:
      with LOCK:DATA['events']=(DATA['events']+[{'thread':title,'state':info['state'],'label':info['label'],'at':ts}])[-24:]
  with LOCK:
   DATA['threads']=sorted(THREADS.values(),key=lambda t:t['eventAt'],reverse=True);DATA['connection']='local-events';DATA['error']=None
 except Exception as e:
  with LOCK:DATA['connection']='unavailable';DATA['error']=type(e).__name__
