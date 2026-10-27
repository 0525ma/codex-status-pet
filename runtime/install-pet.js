function installStatusQuotaPet() {
  const VERSION=1,KEY='__statusQuotaPet';
  const badge=document.getElementById('codex-usage-badge'),api=window.__codexUsageBadge;
  if(!badge||!api||!window.StatusPet)return;
  if(window[KEY]?.badge===badge&&window[KEY]?.version===VERSION)return;
  window[KEY]?.destroy();
  let disposed=false,snapshot=null,state='idle',label='休息',target='',evidence='',lastKey='',pulse=null,affection=0,clickTimer=null;
  try{affection=Number(localStorage.getItem('status-pet-affection')||0);}catch{}
  const ns='http://www.w3.org/2000/svg';const face=document.createElementNS(ns,'svg');face.classList.add('status-quota-face');face.setAttribute('aria-hidden','true');badge.prepend(face);
  const statusLabel=document.createElement('span');statusLabel.className='status-work-label';statusLabel.textContent='休息';badge.append(statusLabel);
  const style=document.createElement('style');style.id='status-quota-pet-style';style.textContent=`
#codex-usage-badge{--usage-width:44px;height:110px;flex-basis:110px;padding:48px 2px 22px;border-radius:23px;gap:4px;cursor:pointer}
#codex-usage-badge .usage-primary>.usage-ring{visibility:hidden!important}
#codex-usage-badge .status-quota-face{position:absolute;top:4px;left:1px;width:40px;height:40px;overflow:visible;--fg:#000;--bg:#fff;color-scheme:light;pointer-events:none}
#codex-usage-badge .usage-number{font-size:12px;line-height:16px}#codex-usage-badge .usage-window{font-size:8px;line-height:10px}
#codex-usage-badge .status-work-label{position:absolute;bottom:8px;left:1px;right:1px;text-align:center;font-size:8px;line-height:10px;color:var(--usage-label);white-space:nowrap;pointer-events:none}
#codex-usage-badge[data-mode=dual]{height:164px;flex-basis:164px;padding-top:48px;padding-bottom:22px}#codex-usage-badge .usage-secondary{flex-basis:64px}
#status-pet-floating{position:fixed;z-index:2147482800;width:112px;height:138px;left:74px;bottom:70px;display:flex;flex-direction:column;align-items:center;justify-content:center;user-select:none;-webkit-app-region:no-drag;cursor:grab;border:1px solid #69778722;border-radius:24px;background:#f7f8faeb;box-shadow:0 4px 20px #23334218;color:#26303c;font:11px/1.5 -apple-system,BlinkMacSystemFont,sans-serif;touch-action:none}
#status-pet-floating[hidden]{display:none!important}#status-pet-floating svg{width:84px;height:84px;--fg:#000;--bg:#fff;color-scheme:light;overflow:visible;pointer-events:none}
#status-pet-floating .status-pet-caption{max-width:100%;padding:0 6px;text-align:center;pointer-events:none}#status-pet-floating button{position:absolute;right:3px;top:2px;border:0;background:transparent;color:#7d8795;font:14px sans-serif;padding:3px;cursor:pointer}
#codex-usage-badge:focus-visible{outline:2px solid #7f92aa;outline-offset:3px}
`;document.head.append(style);
  const opts={mode:'hold',state:'idle',shape:'blob',color:'black',scheme:'light',loginWrap:true,followPointer:true,inkFlat:'#000',eyeColor:'#fff'};
  const bot=new StatusPet(face,opts);
  const floating=document.createElement('div');floating.id='status-pet-floating';floating.hidden=true;floating.tabIndex=0;floating.setAttribute('role','group');floating.setAttribute('aria-label','Status Pet虚拟宠物，可拖动，点击互动');
  const floatSvg=document.createElementNS(ns,'svg'),caption=document.createElement('span'),close=document.createElement('button');caption.className='status-pet-caption';close.textContent='×';close.setAttribute('aria-label','收起虚拟宠物');floating.append(floatSvg,caption,close);document.body.append(floating);
  const pet=new StatusPet(floatSvg,{...opts,paused:true});
  function toggle(on){floating.hidden=!on;pet.setPaused(!on);try{localStorage.setItem('status-pet-floating',on?'1':'0')}catch{}}
  try{const pos=JSON.parse(localStorage.getItem('status-pet-position')||'null');if(pos){floating.style.left=Math.max(0,Math.min(innerWidth-112,pos.x))+'px';floating.style.top=Math.max(0,Math.min(innerHeight-138,pos.y))+'px';floating.style.bottom='auto';}toggle(localStorage.getItem('status-pet-floating')!=='0');}catch{}
  close.onclick=e=>{e.stopPropagation();toggle(false)};
  function respond(){affection++;try{localStorage.setItem('status-pet-affection',String(affection))}catch{};bot.bounceOnce();if(!floating.hidden)pet.bounceOnce();pulse={until:Date.now()+1800,state:'happy',label:'开心'};paint();}
  function click(e){if(e.detail>1)return;clearTimeout(clickTimer);clickTimer=setTimeout(respond,180)}
  function double(e){e.preventDefault();clearTimeout(clickTimer);toggle(floating.hidden)}
  badge.addEventListener('click',click);badge.addEventListener('dblclick',double);
  const keydown=e=>{if(e.key==='Enter'){e.preventDefault();respond()}if(e.key===' '){e.preventDefault();toggle(floating.hidden)}};badge.addEventListener('keydown',keydown);
  let drag=null,moved=false;
  const move=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>4)moved=true;floating.style.left=Math.max(0,Math.min(innerWidth-112,drag.left+dx))+'px';floating.style.top=Math.max(0,Math.min(innerHeight-138,drag.top+dy))+'px';floating.style.bottom='auto';};
  const up=()=>{if(!drag)return;drag=null;if(moved){const r=floating.getBoundingClientRect();try{localStorage.setItem('status-pet-position',JSON.stringify({x:r.left,y:r.top}))}catch{}}else respond()};
  floating.onpointerdown=e=>{if(e.target===close)return;const r=floating.getBoundingClientRect();drag={x:e.clientX,y:e.clientY,left:r.left,top:r.top};moved=false;e.preventDefault()};window.addEventListener('pointermove',move);window.addEventListener('pointerup',up);
  function selectedThread(){const ts=snapshot?.threads||[];const ids=location.href.match(/[a-f\d]{8}-(?:[a-f\d]{4}-){3}[a-f\d]{12}/ig)||[];let id=ids.find(id=>ts.some(t=>t.id===id));if(!id){const active=document.querySelector('[data-app-action-sidebar-thread-id][aria-current="page"], [data-app-action-sidebar-thread-id][data-state="active"]');id=active?.getAttribute('data-app-action-sidebar-thread-id');}return {thread:ts.find(t=>t.id===id)||ts[0],selected:!!id};}
  function paint(){if(disposed)return;const q=api.status(),chosen=selectedThread(),t=chosen.thread;const fresh=snapshot&&Date.now()/1000-snapshot.checkedAt<12;let next='idle',text='休息',detail='暂无本机任务事件';
   if(fresh&&t){next=t.state;text=t.label;target=t.id;detail=(chosen.selected?'当前聊天：':'最近活跃：')+t.title;const age=Date.now()/1000-t.eventAt;if(age>90&&!['happy','sad','alerting'].includes(next)){next='confused';text='待确认';detail+=' · 无新事件，不推断失败';}}
   else if(snapshot){next='confused';text='待连接';detail='工作状态采样已过期';}
   if(q.stale||q.percent===null){if(!fresh||!t){next='confused';text='待连接';}detail+='\n额度暂不可用';}
   else if(q.percent<=5){next='alerting';text='低额度';detail+='\n额度即将耗尽';}else if(q.percent<=20&&next==='idle'){next='drowsy';text='省着用';}
   if(pulse&&Date.now()<pulse.until){next=pulse.state;text=pulse.label;}else pulse=null;
   const short={thinking:'思考',searching:'搜索',working:'工作',writing:'书写',listening:'等你',orbit:'协作',spawning:'生成',humming:'等待',happy:'完成',sad:'中断',alerting:'注意',progress:'规划',sending:'回复',receiving:'接收',idle:'休息',confused:'待确认',drowsy:'低额度',celebrate:'恢复'};
   if(next!==state){bot.setState(next,{resetEyes:false});pet.setState(next,{resetEyes:false});state=next;}
   label=text;evidence=detail;statusLabel.textContent=pulse?'开心':short[next]||'工作';statusLabel.setAttribute('aria-label',text);badge.dataset.statusState=next;caption.textContent=text+' · '+(q.percent==null?'—':q.percent+'%');
   const tip=document.getElementById('codex-usage-tooltip');const base=(tip?.dataset.statusBase||'');if(tip){const raw=tip.textContent.split('\n\nStatus Pet 状态：')[0];tip.textContent=raw+'\n\nStatus Pet 状态：'+text+'\n'+detail+'\n互动 '+affection+' 次 · 单击回应 · 双击宠物浮窗';}
  }
  function updateWork(value){snapshot=value;paint();}
  api.updateWork=updateWork;
  const timer=setInterval(paint,1000),oldDestroy=api.destroy;
  function destroy(){if(disposed)return;disposed=true;clearInterval(timer);clearTimeout(clickTimer);bot.destroy();pet.destroy();badge.removeEventListener('click',click);badge.removeEventListener('dblclick',double);badge.removeEventListener('keydown',keydown);window.removeEventListener('pointermove',move);window.removeEventListener('pointerup',up);face.remove();statusLabel.remove();floating.remove();style.remove();delete window[KEY];}
  api.destroy=()=>{destroy();oldDestroy()};
  window[KEY]={version:VERSION,badge,updateWork,status:()=>({state,label,target,evidence,floating:!floating.hidden,affection,connected:!!snapshot}),destroy};paint();
}
