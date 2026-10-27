from pathlib import Path
import sys,re
root=Path(__file__).resolve().parent
s=Path(sys.argv[1]).read_text();pet=(root/'install-pet.js' if (root/'install-pet.js').exists() else root.parent/'runtime/install-pet.js').read_text()
if 'function installStatusQuotaPet()' in s:
 Path(sys.argv[2]).write_text(s);sys.exit(0)
s=s.replace('function buildBootstrapScript() {',pet+'\n\nfunction buildBootstrapScript() {',1)
old="return [installUsageBadge,installProjectColors,installProjectSizes,installThreadTokens].map(fn=>`(${fn.toString()})()`).join(';\\n');"
new="""const fs=require('node:fs'),path=require('node:path');
  const dir=path.join(__dirname,'status-pet');
  const engine=fs.readFileSync(path.join(dir,'pet-renderer.js'),'utf8');
  const setup=`if(window.__statusPetEngineVersion!==1){${engine};window.__statusPetEngineVersion=1;}`;
  return setup+';\\n'+[installUsageBadge,installProjectColors,installProjectSizes,installThreadTokens,installStatusQuotaPet].map(fn=>`(${fn.toString()})()`).join(';\\n');"""
assert old in s;s=s.replace(old,new)
s=s.replace("if(this.currentValue)await session.evaluate(`window.__codexUsageBadge?.update(${JSON.stringify(this.currentValue)})`);","if(this.currentValue)await session.evaluate(`window.__codexUsageBadge?.update(${JSON.stringify(this.currentValue)})`);\n          if(this.currentWork)await session.evaluate(`window.__statusQuotaPet?.updateWork(${JSON.stringify(this.currentWork)})`);")
needle='  async update(value){\n    this.currentValue=value;'
assert needle in s
s=s.replace(needle,"""  async updateWork(value){
    this.currentWork=value;
    await Promise.all([...this.sessions].map(async([id,s])=>{
      try{await s.evaluate(`window.__statusQuotaPet?.updateWork(${JSON.stringify(value)})`);}catch{}
    }));
  }
"""+needle)
s=s.replace("evaluate(expression){return this.request('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});}","async evaluate(expression){const r=await this.request('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text||'Renderer exception');return r;}")
s=s.replace('  const tokenReader = new ThreadTokenReader();',"""  const workBridge=require('node:child_process').spawn('/usr/bin/python3',[require('node:path').join(__dirname,'status-pet/work_bridge.py')],{stdio:['ignore','pipe','ignore']});
  const workLines=require('node:readline').createInterface({input:workBridge.stdout});
  workLines.on('line',line=>{try{injector.updateWork(JSON.parse(line)).catch(()=>{});}catch{}});
  workBridge.on('error',()=>log('StatusPet工作状态桥接暂不可用，额度显示不受影响。'));
  const tokenReader = new ThreadTokenReader();""",1)
s=s.replace('    projectSizeScanner.stop();','    workLines.close(); workBridge.kill();\n    projectSizeScanner.stop();',1)
s=s.replace("主窗口连接正常，进度条已注入。","主窗口连接正常，黑色StatusPet角色与额度组件已注入。")
s=s.replace("!badge.contains(r.target) && !tooltip.contains(r.target) && r.target !== style","!badge.contains(r.target) && !tooltip.contains(r.target) && !document.getElementById('status-pet-floating')?.contains(r.target) && r.target !== style",1)
s=s.replace("module.exports = { installUsageBadge,", "module.exports = { installStatusQuotaPet, installUsageBadge,",1)
s=re.sub(r"var AGENT_VERSION = '([^']+)';",lambda m: "var AGENT_VERSION = '"+m.group(1)+"-status-pet-local.1';",s,count=1)
s=s.replace("const fresh=snapshot&&Date.now()/1000-snapshot.checkedAt<12;","const fresh=snapshot&&snapshot.connection!=='unavailable'&&Date.now()/1000-snapshot.checkedAt<12;")
s=s.replace("selected:!!id","selected:ts.some(t=>t.id===id)")
assert all(x in s for x in ['function installStatusQuotaPet()', 'async updateWork(value)', 'const workBridge=', 'if(this.currentWork)'])
Path(sys.argv[2]).write_text(s)
