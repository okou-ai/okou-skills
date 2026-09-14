/* Okou reveal templates. Pure, deterministic frame rendering; no external renderer. */
(function(){
'use strict';
const G=window.OKOU_GEOMETRY,W=G.stage.width,H=G.stage.height,L=G.lockup.x,T=G.lockup.y,LW=G.lockup.width,LH=G.lockup.height;
const mark=G.mark,word=G.word,markCut=G.cuts[1];
const clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v));
const mix=(a,b,p)=>a+(b-a)*p;
const ease=v=>1-Math.pow(1-clamp(v),3);
const smooth=v=>{v=clamp(v);return v*v*(3-2*v)};
const step=(v,a,b)=>clamp((v-a)/(b-a));
const hash=n=>{const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const images={},particles={};let iconCache=null;
const iconPath=()=>iconCache||(iconCache=new Path2D(G.iconPath));
const palette=window.OKOU_PALETTE;
const rgba=(hex,alpha)=>'rgba('+[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)).join(',')+','+alpha+')';
function image(src){return new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=src})}
function stamp(c,im,x=L,y=T,w=LW,h=LH,a=1){if(a<=0)return;c.save();c.globalAlpha*=clamp(a);c.drawImage(im,x,y,w,h);c.restore()}
function clipRect(c,x,y,w,h,fn){if(w<=0||h<=0)return;c.save();c.beginPath();c.rect(x,y,w,h);c.clip();fn();c.restore()}
function rounded(c,x,y,w,h,r){c.beginPath();c.roundRect(x,y,w,h,r)}
function base(c,im,q,scale=1,dx=0,dy=0,a=1){c.save();c.translate(W/2+dx,H/2+dy);c.scale(scale,scale);stamp(c,im,-LW/2,-LH/2,LW,LH,a);c.restore()}
function region(c,im,x,y,w,h,dx=0,dy=0,sx=1,sy=1,rot=0,alpha=1){c.save();c.translate(x+w/2+dx,y+h/2+dy);c.rotate(rot);c.scale(sx,sy);c.globalAlpha*=clamp(alpha);c.beginPath();c.rect(-w/2,-h/2,w+.5,h+.5);c.clip();stamp(c,im,L-x-w/2,T-y-h/2);c.restore()}
function buildParticles(im){
 const b=document.createElement('canvas');b.width=Math.ceil(LW*2);b.height=Math.ceil(LH*2);
 const c=b.getContext('2d',{willReadFrequently:true});c.drawImage(im,0,0,b.width,b.height);
 const d=c.getImageData(0,0,b.width,b.height).data,pts=[];
 for(let y=0;y<b.height;y+=10)for(let x=0;x<b.width;x+=10){
  const k=(y*b.width+x)*4;if(d[k+3]>80)pts.push({x:L+x/b.width*LW,y:T+y/b.height*LH,c:'rgb('+d[k]+','+d[k+1]+','+d[k+2]+')',r:hash(x*3+y/2),s:hash(x/2+y*4)});
 }
 return pts;
}
// Preparation and reveal retain their original speed. Hold is an independent tail.
const completionPhases={"particles": 0.98, "shards": 0.85, "tiles": 0.9415384615384615, "monogram": 0.93, "letters": 0.94, "ribbon": 0.954, "orbit": 0.94, "portal": 0.95, "fold": 0.935, "flash": 0.65};
function timing(progress,options={},id=''){
 const motionDuration=options.motionDuration??1.92,hold=options.hold??.25,endPhase=completionPhases[id]??1;
 const preparation=motionDuration/16,revealDuration=motionDuration-preparation;
 const formationDuration=preparation+revealDuration*endPhase,total=formationDuration+hold,time=clamp(progress)*total;
 const forward=Math.min(endPhase,Math.max(0,(time-preparation)/revealDuration)),direction=options.direction??'in',holding=time>=formationDuration-1e-9;
 return {time,motionDuration,formationDuration,preparation,hold,total,endPhase,direction,q:direction==='out'?endPhase-forward:forward,holding};
}
const temp=document.createElement('canvas');temp.width=W;temp.height=H;const tc=temp.getContext('2d');
function render(canvas,id,p,mode='light',options={}){
 const c=canvas.getContext('2d');const im=images[mode];if(!im)return;
 c.save();c.setTransform(canvas.width/W,0,0,canvas.height/H,0,0);c.clearRect(0,0,W,H);c.fillStyle=palette[mode].bg;c.fillRect(0,0,W,H);
 const phase=timing(p,options,id),q=phase.q,e=ease(q),accent=palette[mode].accent;
 if(phase.holding){if(phase.direction==='in')stamp(c,im);c.restore();return}
 if(phase.direction==='out'&&phase.time<=phase.preparation){stamp(c,im);c.restore();return}
 if(q<=0){c.restore();return}if(q>=1){stamp(c,im);c.restore();return}
 switch(id){
 case 'mask':{const edge=L-50+(LW+100)*e;clipRect(c,0,0,edge,H,()=>stamp(c,im,L+24*(1-e),T));c.fillStyle=accent;c.globalAlpha=Math.sin(q*Math.PI)*.7;c.fillRect(edge-2,T-34,3,LH+68);break}
 case 'iris':{c.save();c.beginPath();c.arc(mark.cx,mark.cy,mix(0,570,e),0,Math.PI*2);c.clip();base(c,im,q,mix(1.1,1,e));c.restore();c.strokeStyle=accent;c.globalAlpha=(1-e)*.4;c.lineWidth=1.5;c.beginPath();c.arc(mark.cx,mark.cy,mix(0,570,e)+6,0,Math.PI*2);c.stroke();break}
 case 'stroke':{
  const trace=ease(step(q,0,.62)),icon=iconPath(),iw=G.iconViewBox[2],ih=G.iconViewBox[3];
  c.save();c.translate(mark.x,mark.y);c.scale(mark.width/iw,mark.height/ih);
  c.strokeStyle=accent;c.lineWidth=7;c.lineJoin='round';c.lineCap='round';
  c.setLineDash([2000,2000]);c.lineDashOffset=2000*(1-trace);c.stroke(icon);
  c.setLineDash([]);c.globalAlpha=smooth(step(q,.5,.88));c.fillStyle=palette[mode].fg;c.fill(icon);
  c.restore();c.globalAlpha=1;
  clipRect(c,L+markCut,T,(LW-markCut)*ease(step(q,.42,.9)),LH,()=>stamp(c,im,L,T,LW,LH,step(q,.45,.6)));
  stamp(c,im,L,T,LW,LH,smooth(step(q,.86,1)));break;
 }
 case 'negative':{const v=ease(step(q,0,.68)),fade=1-smooth(step(q,.62,1));tc.clearRect(0,0,W,H);tc.globalCompositeOperation='source-over';tc.fillStyle=accent;tc.fillRect(L-45,T-34,LW+90,LH+68);tc.globalCompositeOperation='destination-out';stamp(tc,im);tc.globalCompositeOperation='source-over';c.save();c.globalAlpha=fade;clipRect(c,W/2-(LW+90)*v/2,0,(LW+90)*v,H,()=>c.drawImage(temp,0,0));c.restore();stamp(c,im,L,T,LW,LH,smooth(step(q,.56,1)));break}
 case 'particles':{const pts=particles[mode],fade=1-smooth(step(q,.72,.98));for(let i=0;i<pts.length;i++){const d=pts[i],f=ease(step(q,d.r*.16,.88)),a=d.s*Math.PI*2+(1-f)*1.2,r=110+240*d.r,x=d.x+(1-f)*Math.cos(a)*r,y=d.y+(1-f)*Math.sin(a)*r*.58;c.fillStyle=d.c;c.globalAlpha=fade*step(q,0,.12);c.beginPath();c.arc(x,y,1.3+(1-f)*1.3,0,Math.PI*2);c.fill()}c.globalAlpha=1;stamp(c,im,L,T,LW,LH,smooth(step(q,.7,.96)));break}
 case 'dissolve':{const size=9;for(let y=0;y<LH;y+=size)for(let x=0;x<LW;x+=size){const threshold=hash(x*3+y),a=smooth(step(q,threshold*.77,threshold*.77+.23));if(a>0)region(c,im,L+x,T+y,size,size,0,0,1,1,0,a)}break}
 case 'shards':{const cols=12,rows=4,w=LW/cols,h=LH/rows;for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const n=y*cols+x,r=hash(n+3),v=ease(step(q,r*.13,.85));region(c,im,L+x*w,T+y*h,w,h,(x-cols/2)*(1-v)*60,(y-rows/2)*(1-v)*78,1,1,(1-v)*(r-.5)*2,step(q,0,.16))}break}
 case 'tiles':{const cols=20,rows=6,w=LW/cols,h=LH/rows;for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const delay=(x+y)/26*.5,f=ease(step(q,delay,delay+.48));region(c,im,L+x*w,T+y*h,w,h,0,16*(1-f),f, f,0,f)}break}
 case 'monogram':{const settle=ease(step(q,.18,.75)),pop=ease(step(q,0,.35));region(c,im,L,T,markCut,LH,(W/2-mark.cx)*(1-settle),0,mix(.7,1,pop),mix(.7,1,pop),0,pop);const v=ease(step(q,.3,.93));clipRect(c,L+markCut,T,(LW-markCut)*v,LH,()=>region(c,im,L+markCut,T,LW-markCut,LH,-55*(1-v),0,1,1,0,v));break}
 case 'letters':{const cuts=G.cuts;for(let i=0;i<cuts.length-1;i++){const x=cuts[i],w=cuts[i+1]-cuts[i],v=ease(step(q,i*.06,i*.06+.64));region(c,im,L+x,T,w,LH,0,(i%2? -1:1)*100*(1-v),1,1,(1-v)*(i%2?.24:-.24),v)}break}
 case 'spring':{const f=step(q,0,.92),spring=1-Math.exp(-f*7)*Math.cos(f*10);c.save();c.translate(480,270+45*(1-e));c.scale(.2+.8*spring,1.55-.55*spring);stamp(c,im,-LW/2,-LH/2,LW,LH,step(q,0,.16));c.restore();break}
 case 'ribbon':{const n=9,w=LW/n;for(let i=0;i<n;i++){const f=ease(step(q,i*.038,i*.038+.65));region(c,im,L+i*w,T,w,LH,0,(i%2?1:-1)*(1-f)*100,1,f,(i%2?1:-1)*(1-f)*.12,f)}break}
 case 'liquid':{const y=mix(T+LH+35,T-45,smooth(q));c.save();c.beginPath();c.moveTo(0,H);for(let x=0;x<=W;x+=8)c.lineTo(x,y+Math.sin(x*.019-q*6)*14*Math.sin(q*Math.PI));c.lineTo(W,H);c.closePath();c.clip();stamp(c,im);c.restore();c.strokeStyle=accent;c.globalAlpha=Math.sin(q*Math.PI)*.3;c.lineWidth=1;c.beginPath();for(let x=L-50;x<L+LW+50;x+=6){const yy=y+Math.sin(x*.019-q*6)*14*Math.sin(q*Math.PI);if(x===L-50)c.moveTo(x,yy);else c.lineTo(x,yy)}c.stroke();break}
 case 'light':{
  const x=mix(L-150,L+LW+130,e);
  tc.globalCompositeOperation='source-over';tc.clearRect(0,0,W,H);tc.drawImage(im,L,T,LW,LH);
  tc.globalCompositeOperation='destination-in';
  let gr=tc.createLinearGradient(x-86,0,x,0);
  gr.addColorStop(0,'rgba(0,0,0,1)');gr.addColorStop(1,'rgba(0,0,0,0)');
  tc.fillStyle=gr;tc.fillRect(0,0,W,H);tc.globalCompositeOperation='source-over';
  c.drawImage(temp,0,0);
  tc.clearRect(0,0,W,H);tc.drawImage(im,L,T,LW,LH);tc.globalCompositeOperation='source-in';
  gr=tc.createLinearGradient(x-104,0,x+26,0);
  gr.addColorStop(0,'rgba(255,255,255,0)');gr.addColorStop(.66,'rgba(255,255,255,.8)');
  gr.addColorStop(1,'rgba(255,255,255,0)');tc.fillStyle=gr;tc.fillRect(0,0,W,H);
  tc.globalCompositeOperation='source-over';c.drawImage(temp,0,0);break;
 }
 case 'glass':{const x=mix(L-100,L+LW+100,e);clipRect(c,0,0,x,H,()=>stamp(c,im));clipRect(c,x-48,T-14,78,LH+28,()=>base(c,im,q,1.075,-8,0,.85));const gr=c.createLinearGradient(x-48,0,x+30,0);gr.addColorStop(0,rgba(accent,0));gr.addColorStop(.35,rgba(accent,.19));gr.addColorStop(.7,'rgba(255,255,255,.64)');gr.addColorStop(1,rgba(accent,0));c.fillStyle=gr;rounded(c,x-48,T-32,78,LH+64,30);c.fill();break}
 case 'focus':{c.filter='blur('+(1-e)*25+'px)';base(c,im,q,mix(1.17,1,e),0,0,smooth(step(q,0,.65)));c.filter='none';break}
 case 'depth':{const a=(1-e)*1.46;c.save();c.translate(480,270);c.transform(Math.cos(a),-.08*Math.sin(a),0,1,0,0);for(let i=12;i>0;i--){c.globalAlpha=(1-e)*.12;stamp(c,im,-LW/2-i*2.1*Math.sin(a),-LH/2+i*.4)}c.globalAlpha=step(q,0,.15);stamp(c,im,-LW/2,-LH/2);c.restore();break}
 case 'orbit':{const n=8,w=LW/n;for(let i=0;i<n;i++){const f=ease(step(q,i*.02,.94)),a=i/n*Math.PI*2+(1-f)*3,rr=(1-f)*180;region(c,im,L+i*w,T,w,LH,Math.cos(a)*rr,Math.sin(a)*rr*.65,1,1,Math.sin(a)*(1-f)*.25,step(q,0,.18))}break}
 case 'portal':{const f=ease(step(q,0,.66)),size=mix(1450,mark.width,f),cx=mix(W/2,mark.cx,f);c.save();c.translate(cx,mark.cy);c.rotate((1-f)*.4);c.drawImage(images['mark_'+mode],-size/2,-size/2,size,size);c.restore();clipRect(c,L+markCut,T,LW-markCut,LH,()=>stamp(c,im,L,T,LW,LH,smooth(step(q,.53,.95))));break}
 case 'fold':{const n=6,w=LW/n;for(let i=0;i<n;i++){const f=smooth(step(q,i*.045,i*.045+.71)),s=Math.sin(f*Math.PI/2);region(c,im,L+i*w,T,w,LH,-(1-s)*w/2,0,s,1,0,step(q,0,.15));if(f>.03&&f<.99){c.fillStyle=mode==='light'?'rgba(20,20,40,.1)':'rgba(255,255,255,.07)';c.fillRect(L+i*w,T,w*(1-s)*.55,LH)}}break}
 case 'flash':{const f=ease(step(q,.18,.65));base(c,im,q,mix(1.22,1,f),0,0,f);const pulse=Math.exp(-Math.pow((q-.24)/.09,2));c.fillStyle=mode==='dark'?'rgba(255,255,255,'+pulse*.87+')':rgba(accent,pulse*.16);c.fillRect(0,0,W,H);break}
 case 'glitch':{const n=12,h=LH/n,amp=(1-e)*54;for(let i=0;i<n;i++){const tick=Math.floor(q*12),shift=(hash(tick+i*7)-.5)*amp;region(c,im,L,T+i*h,LW,h,shift,0,1,1,0,step(q,0,.12));if(q<.65){c.save();c.globalAlpha=(1-e)*.24;c.globalCompositeOperation='screen';region(c,im,L,T+i*h,LW,h,-shift-8,0);c.restore()}}break}
 case 'scan':{const edge=T-15+(LH+30)*smooth(q);clipRect(c,0,0,W,edge,()=>stamp(c,im));for(let y=T;y<T+LH;y+=7){if(y>edge)region(c,im,L,y,LW,1,0,0,1,1,0,.09)}c.strokeStyle=accent;c.lineWidth=2;c.globalAlpha=Math.sin(q*Math.PI)*.75;c.beginPath();c.moveTo(L-18,edge);c.lineTo(L+LW+18,edge);c.stroke();break}
 case 'echo':{for(let i=4;i>=1;i--){const off=(1-e)*i*42;base(c,im,q,1,off,-off*.12,.08*(1-e)*step(q,0,.1));base(c,im,q,1,-off,off*.12,.08*(1-e)*step(q,0,.1))}base(c,im,q,1,0,0,smooth(step(q,0,.76)));break}
 default:stamp(c,im);
 }
 c.restore();
}
window.OkouMotion={render,timing,completionPhases,geometry:G,defaultTiming:{motionDuration:1.92,hold:.25},ready:Promise.all(Object.entries(window.OKOU_LOGOS).map(async ([k,src])=>{images[k]=await image(src)})).then(()=>{particles.light=buildParticles(images.light);particles.dark=buildParticles(images.dark)})};
})();
