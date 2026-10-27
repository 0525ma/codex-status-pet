'use strict';
const net=require('node:net');
function classifyConnection({clientRunning,transportReady}){
 if(!clientRunning)return {health:'idle',debugTransport:'unavailable',uiMounted:null,healthError:null,requiredAction:null};
 if(!transportReady)return {health:'attention',debugTransport:'unavailable',uiMounted:false,healthError:'Codex正在运行，但扩展连接端口未开启，侧栏无法挂载。',requiredAction:'quit_then_launch_with_status_bar'};
 return {health:'transport_ready',debugTransport:'available',uiMounted:null,healthError:null,requiredAction:null};
}
function portReady(port=39222){return new Promise(resolve=>{const s=net.connect({host:'127.0.0.1',port});let ended=false;const done=v=>{if(ended)return;ended=true;s.destroy();resolve(v)};s.once('connect',()=>done(true));s.once('error',()=>done(false));s.setTimeout(700,()=>done(false));});}
module.exports={classifyConnection,portReady};
