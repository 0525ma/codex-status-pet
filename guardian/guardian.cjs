'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),cp=require('node:child_process'),{promisify}=require('node:util');
const run=promisify(cp.execFile),ROOT=__dirname,DEFAULT_DEST=path.join(os.homedir(),'Library/Application Support/CodexUsageBadge'),CACHE=path.join(os.homedir(),'Library/Caches/CodexUsageBadge-updates'),STATE=path.join(ROOT,'status.json'),GUI='gui/'+process.getuid();
const settings=JSON.parse(fs.readFileSync(path.join(ROOT,'settings.json'),'utf8'));const NODE=settings.node;const APP=settings.app;const DEST=path.resolve(settings.baseDir||DEFAULT_DEST);
let updating=false,reconciling=false,lastPlistMtime={};const read=p=>{try{return JSON.parse(fs.readFileSync(p,'utf8'))}catch{return null}};
function record(fields){const old=read(STATE)||{};const next={...old,...fields,updatedAt:new Date().toISOString()};const temp=STATE+'.'+process.pid+'.tmp';fs.writeFileSync(temp,JSON.stringify(next,null,2)+'\n');fs.renameSync(temp,STATE);return next;}
function log(s){console.log(new Date().toISOString(),s)}
const {classifyConnection,portReady}=require('./connection-health.cjs');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
function workerStub(){return "'use strict';\n// CodexStatusPetGuardian preserves the robot while applying verified upstream updates.\nrequire("+JSON.stringify(path.join(ROOT,'guardian.cjs'))+").workerMain().then(()=>{}).catch(e=>{console.error(e.message);process.exitCode=1});\n";}
async function prepareAgent(input,output){await run('/usr/bin/python3',[path.join(ROOT,'patch-agent.py'),input,output],{timeout:10000});await run(process.execPath,['--check',output],{timeout:10000});const src=fs.readFileSync(output,'utf8');if(!src.includes('function installStatusQuotaPet()')||!src.includes('workBridge'))throw Error('机器人补丁预检未通过');return {sha256:hash(src)};}
async function ensureResident(label='com.codexusagebadge.agent'){
 const plist=path.join(os.homedir(),'Library/LaunchAgents',label+'.plist');
 const mtime=fs.statSync(plist).mtimeMs;
 if(mtime!==lastPlistMtime[label]){
  await run('/usr/bin/python3',['-c',"import plistlib,sys,os; p=sys.argv[1]; v=plistlib.load(open(p,'rb')); changed=v.get('KeepAlive') is not True or v['ProgramArguments'][0]!=sys.argv[2]; v['KeepAlive']=True; v['ProgramArguments'][0]=sys.argv[2]; plistlib.dump(v,open(p+'.tmp','wb')) if changed else None; os.replace(p+'.tmp',p) if changed else None",plist,NODE],{timeout:5000});
  lastPlistMtime[label]=fs.statSync(plist).mtimeMs;
 }

 let loaded;try{loaded=await run('/bin/launchctl',['print',GUI+'/'+label],{timeout:5000})}catch{}
 if(!loaded){await run('/bin/launchctl',['bootstrap',GUI,plist],{timeout:10000});return 'bootstrapped'}
 if(!/state = running/.test(loaded.stdout)){await run('/bin/launchctl',['kickstart',GUI+'/'+label],{timeout:10000});return 'restarted'}return 'running';
}
function activeInstallLock(){
 for(const dir of [path.join(CACHE,'check.lock'),path.join(os.homedir(),'Library/Caches/CodexUsageBadge-manage.lock')]){
  if(!fs.existsSync(dir))continue;const owner=read(path.join(dir,'owner.json'));
  if(owner?.pid){try{process.kill(owner.pid,0);return true}catch(e){if(e.code!=='ESRCH')return true}}
  else if(Date.now()-fs.statSync(dir).mtimeMs<120000)return true;
 }return false;
}
async function reconcile(){if(reconciling||updating||activeInstallLock())return;reconciling=true;
 try{
  const source=path.join(DEST,'agent.cjs');if(!fs.existsSync(source))throw Error('用量条安装目录缺失，未凭空重装');
  let patched=false;
  if(!fs.readFileSync(source,'utf8').includes('function installStatusQuotaPet()')){
   const b=path.join(ROOT,'backups','reconcile-'+Date.now());fs.mkdirSync(b,{recursive:true});fs.copyFileSync(source,path.join(b,'agent.cjs'));
   const temp=source+'.status-pet-new';await prepareAgent(source,temp);fs.renameSync(temp,source);patched=true;record({lastOverlayRestoreAt:new Date().toISOString()});log('已恢复机器人定制');
  }
  if(!fs.existsSync(path.join(DEST,'status-pet/work_bridge.py')))fs.cpSync(path.join(ROOT,'status-pet'),path.join(DEST,'status-pet'),{recursive:true});
  const worker=path.join(DEST,'updater/worker.cjs'),stub=workerStub();if(!fs.existsSync(worker)||fs.readFileSync(worker,'utf8')!==stub){const b=path.join(ROOT,'backups','worker-'+Date.now()+'.cjs');fs.mkdirSync(path.dirname(b),{recursive:true});if(fs.existsSync(worker))fs.copyFileSync(worker,b);fs.mkdirSync(path.dirname(worker),{recursive:true});fs.writeFileSync(worker,stub);}
  let bridge='running';const status=await ensureResident();const startup=await ensureResident('com.codexusagebadge.startup');if(status==='running'){try{await run('/usr/bin/pgrep',['-f',path.join(DEST,'status-pet/work_bridge.py')],{timeout:3000})}catch{bridge='restarting';await run('/bin/launchctl',['kickstart','-k',GUI+'/com.codexusagebadge.agent'],{timeout:10000});}}if(patched)await run('/bin/launchctl',['kickstart','-k',GUI+'/com.codexusagebadge.agent'],{timeout:10000});
  const processes=await run('/bin/ps',['-axo','comm='],{timeout:3000});
  const clientRunning=processes.stdout.split('\n').some(line=>line.trim()===settings.executable);
  const connection=classifyConnection({clientRunning,transportReady:await portReady()});
  const prior=read(STATE)||{};
  if(prior.debugTransport!==connection.debugTransport||prior.health!==connection.health)log(connection.healthError||('扩展连接状态：'+connection.health));
  record({resident:status,startup,workBridge:bridge,overlayFilesPresent:true,overlayInstalled:true,clientRunning,...connection,lastHealthAt:new Date().toISOString(),intervalSeconds:15,updateIntervalSeconds:3600});
 }catch(e){record({health:'attention',healthError:e.message});log('守护检查需关注：'+e.message)}finally{reconciling=false;}
}
async function checkForUpdate({force=false,checkOnly=false}={}){
 if(updating)return {event:'busy'};const state=read(STATE)||{};
 if(!force&&Date.now()-(state.lastUpdateCheckAt||0)<3600000)return {event:'cooldown'};
 updating=true;record({lastUpdateCheckAt:Date.now(),updateState:'checking'});
 try{
  const coreFile=path.join(DEST,'updater/core.cjs');delete require.cache[require.resolve(coreFile)];const core=require(coreFile);
  const result=await core.updateOnce({installDir:DEST,cacheDir:CACHE,force:true,checkOnly,signal:AbortSignal.timeout(180000),install:async(stage,current)=>{
   const baseline=path.join(stage,'agent.cjs'),candidate=path.join(stage,'agent.status-pet-preflight.cjs');
   const proof=await prepareAgent(baseline,candidate);
   // No installed files are touched until the verified release and overlay preflight pass.
   const b=path.join(ROOT,'backups','update-'+Date.now());fs.mkdirSync(b,{recursive:true});for(const name of ['agent.cjs','updater/worker.cjs','installed-version.json','update-settings.json']){const from=path.join(DEST,name),to=path.join(b,name);fs.mkdirSync(path.dirname(to),{recursive:true});fs.copyFileSync(from,to);}
   fs.copyFileSync(candidate,baseline);fs.writeFileSync(path.join(stage,'updater/worker.cjs'),workerStub());
   fs.cpSync(path.join(ROOT,'status-pet'),path.join(DEST,'status-pet'),{recursive:true});
   record({updateState:'installing',candidateAgentSha256:proof.sha256,backup:b});
   await run(process.execPath,[path.join(stage,'manage.cjs'),'install','--from-update'],{env:{...process.env,CODEX_BADGE_APP:current.app,CODEX_HOME:current.codexHome||''},timeout:120000,maxBuffer:1024*1024});
   const actual=fs.readFileSync(path.join(DEST,'agent.cjs'),'utf8');if(!actual.includes('function installStatusQuotaPet()')||hash(actual)!==proof.sha256)throw Error('升级后机器人定制校验失败');
  }});
  record({updateState:result.event,updateError:null,currentVersion:result.currentVersion,availableVersion:result.availableVersion||null,lastUpdateResult:result});log('版本检查：'+result.event);return result;
 }catch(e){record({updateState:'attention',updateError:e.message});log('更新保留当前版本：'+e.message);return {event:'attention',message:e.message};}finally{updating=false;}
}
async function workerMain(args=process.argv.slice(2)){
 const mode=args[0]||'run',file=path.join(DEST,'update-settings.json');
 if(['enable','disable'].includes(mode)){const settings=read(file);if(settings?.owner!=='codex-usage-badge-updater-v1')throw Error('更新配置不匹配');fs.writeFileSync(file,JSON.stringify({...settings,enabled:mode==='enable'})+'\n');console.log(mode==='enable'?'自动更新已开启':'自动更新已关闭');return;}
 if(mode==='status'){console.log(JSON.stringify({settings:read(file),status:read(STATE)},null,2));return;}
 if(!['run','check'].includes(mode))throw Error('未知更新操作');
 console.log(JSON.stringify(await checkForUpdate({force:mode==='check',checkOnly:mode==='check'})));
}
module.exports={reconcile,checkForUpdate,prepareAgent,record,workerMain};
if(require.main===module){const mode=process.argv[2]||'daemon';(async()=>{await reconcile();if(mode==='once')return;await checkForUpdate({force:mode==='check',checkOnly:mode==='check'});if(mode==='check')return;setInterval(reconcile,15000);setInterval(()=>checkForUpdate(),60000);log('后台守护运行中；15秒健康检查，1小时版本检查。');})().catch(e=>{record({health:'attention',healthError:e.message});process.exitCode=1})}
