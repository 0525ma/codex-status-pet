/* Original default renderer for codex-status-pet. MIT License.
 * No extracted geometry, raster artwork, or Grok engine code is included. */
(function (g) {
  'use strict';
  const NS='http://www.w3.org/2000/svg';
  class StatusPet {
    constructor(svg, opts={}) {
      this.svg=svg;this.state=opts.state||'idle';this.paused=!!opts.paused;this.follow=opts.followPointer!==false;
      this.reduced=typeof matchMedia==='function'&&matchMedia('(prefers-reduced-motion: reduce)').matches;
      this.gaze={x:0,y:0};this.shown={x:0,y:0};this.hop=-Infinity;this.start=performance.now();this.dead=false;
      svg.setAttribute('viewBox','0 0 100 100');svg.innerHTML='';
      const make=(tag,attrs,parent=svg)=>{const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,String(v));parent.append(e);return e;};
      this.body=make('g',{});make('path',{d:'M50 25V15',stroke:'#222b38','stroke-width':4,'stroke-linecap':'round'},this.body);
      this.lamp=make('circle',{cx:50,cy:12,r:4,fill:'#62b59a'},this.body);
      make('rect',{x:15,y:24,width:70,height:62,rx:21,fill:'#17202d'},this.body);
      this.face=make('g',{},this.body);
      this.eyes=[make('rect',{x:32,y:44,width:11,height:17,rx:3,fill:'#f7fbff'},this.face),make('rect',{x:57,y:44,width:11,height:17,rx:3,fill:'#f7fbff'},this.face)];
      make('path',{d:'M42 72H58',stroke:'#94a7ba','stroke-width':3,'stroke-linecap':'round'},this.body);
      this.move=e=>{if(!this.follow)return;const r=svg.getBoundingClientRect();if(!r.width||!r.height)return;this.gaze={x:Math.max(-5,Math.min(5,(e.clientX-r.left-r.width/2)/r.width*8)),y:Math.max(-4,Math.min(4,(e.clientY-r.top-r.height/2)/r.height*8))};};
      this.leave=()=>{this.gaze={x:0,y:0}};window.addEventListener('pointermove',this.move);window.addEventListener('blur',this.leave);
      this.setState(this.state);this.tick=this.tick.bind(this);this.raf=requestAnimationFrame(this.tick);
    }
    setState(state){this.state=state;this.lamp.setAttribute('fill',['alerting','angry','sad','scared'].includes(state)?'#e58472':['happy','celebrate','excited'].includes(state)?'#6bc79f':'#7ca5d2');}
    setPaused(v){this.paused=!!v;} setMode(){} setFollowPointer(v){this.follow=!!v;} setColor(){} setShape(){} setEmphasis(){}
    bounceOnce(){this.hop=performance.now();} burstOnce(){this.bounceOnce();} spinOnce(){this.bounceOnce();}
    tick(now){if(this.dead)return;this.raf=requestAnimationFrame(this.tick);if(this.paused)return;
      const t=(now-this.start)/1000,fast=['working','searching','spawning','orbit'].includes(this.state),sleep=['sleeping','drowsy','powering-down'].includes(this.state);
      const amount=this.reduced?0:1;this.shown.x+=(this.gaze.x-this.shown.x)*.14;this.shown.y+=(this.gaze.y-this.shown.y)*.14;
      const bounce=Math.max(0,1-(now-this.hop)/650);const y=amount*(Math.sin(t*(fast?5:2))*(fast?2:1)-Math.sin(bounce*Math.PI)*13);
      this.body.setAttribute('transform',`translate(0 ${y.toFixed(2)}) rotate(${(amount*Math.sin(t*2)*(fast?3:1)).toFixed(2)} 50 85)`);
      const blink=!this.reduced&&t%5.5>5.32;let h=sleep||blink?3:['happy','celebrate','playful'].includes(this.state)?8:this.state==='surprised'?22:17;
      this.eyes.forEach((eye,i)=>{eye.setAttribute('height',h);eye.setAttribute('y',String(52-h/2+(this.state==='thinking'&&i? -3:0)));});
      this.face.setAttribute('transform',`translate(${this.shown.x.toFixed(2)} ${this.shown.y.toFixed(2)})`);
    }
    destroy(){this.dead=true;cancelAnimationFrame(this.raf);window.removeEventListener('pointermove',this.move);window.removeEventListener('blur',this.leave);}
  }
  g.StatusPet=StatusPet;
})(window);
