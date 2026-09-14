(function(){
  'use strict';
  const library=window.VIDEO_MOTION_TEMPLATES,defs=new Map(library.templates.map(x=>[x.id,x]));
  const $=id=>document.getElementById(id),speedSeconds={fast:.96,standard:1.92,slow:3.2};
  // Keep frame capture on one raster backend when consumers repeatedly read pixels.
  $('canvas').getContext('2d',{willReadFrequently:true});
  let config=null,template=null,timeline=null,frame=null,time=0,playing=false,loaded=false,loadId=0,previous=performance.now(),elapsed=0;
  const api={ready:null,configure,seek,play,pause,state,recipe};
  function normalize(input){
    const item=defs.get(input.templateId||input.template||library.templates[0].id);
    if(!item)throw Error('未知的动画模板');
    const result={templateId:item.id,brandPreset:input.brandPreset??'okou',theme:input.theme??'dark',holdSeconds:Number(input.holdSeconds??.25),speed:input.speed??'standard',direction:input.direction??'in',placement:input.placement??'intro'};
    if(result.brandPreset!=='okou')throw Error('当前模板使用 Okou 品牌预设');
    if(!item.controls.themes.includes(result.theme))throw Error('不支持的配色');
    if(!item.controls.holdSeconds.includes(result.holdSeconds))throw Error('不支持的结束停留');
    if(!item.speeds.includes(result.speed))throw Error('该模板不支持此节奏');
    if(!item.directions.includes(result.direction))throw Error('该模板不支持此运动方向');
    if(!item.placements.includes(result.placement))throw Error('不支持的位置');
    return result;
  }
  function duration(){
    return template.runtime.kind==='canvas'?OkouMotion.timing(1,options(),template.runtime.scene).total:template.formationSeconds+config.holdSeconds;
  }
  function formation(){return duration()-config.holdSeconds}
  function options(){return {motionDuration:speedSeconds[config.speed],hold:config.holdSeconds,direction:config.direction}}
  function state(){return {ready:loaded,playing,time,duration:config?duration():0,formationSeconds:config?formation():0,config:config?{...config}:null}}
  function recipe(){
    if(!loaded)throw Error('模板尚未就绪');
    const url=new URL('player.html',location.href),params={template:config.templateId,theme:config.theme,hold:config.holdSeconds,speed:config.speed,direction:config.direction,placement:config.placement};
    for(const [key,value] of Object.entries(params))url.searchParams.set(key,String(value));
    return {schema:'video-motion-clip/v1',libraryId:library.id,libraryVersion:library.version,templateVersion:template.version,...config,stage:library.stage,durationSeconds:duration(),formationSeconds:formation(),playerUrl:url.href};
  }
  function size(){if(frame)frame.style.transform='scale('+($('stage').clientWidth/1920)+')'}
  function paint(){
    if(!loaded)return;
    if(template.runtime.kind==='canvas')OkouMotion.render($('canvas'),template.runtime.scene,time/duration(),config.theme,options());
    else timeline.seek(time,false);
  }
  function seek(seconds){
    if(!loaded)throw Error('模板尚未就绪');
    if(!Number.isFinite(seconds))throw Error('时间必须为有限数字');
    playing=false;time=Math.max(0,Math.min(duration(),seconds));paint();return state();
  }
  function play(){if(!loaded)return;if(time>=duration())time=0;previous=performance.now();playing=true;paint()}
  function pause(){playing=false;return state()}
  async function waitTimeline(element,id,gen){
    const started=performance.now();
    while(performance.now()-started<25000){
      if(gen!==loadId)throw Error('cancelled');
      const candidate=element.contentWindow?.__timelines?.[id];
      if(candidate&&typeof candidate.seek==='function')return {timeline:candidate};
      await new Promise(resolve=>setTimeout(resolve,40));
    }
    throw Error('动画未能载入，请重试');
  }
  function configure(input={}){
    const promise=load(input);api.ready=promise;return promise;
  }
  async function load(input){
    const next=normalize(input),gen=++loadId;
    playing=false;loaded=false;time=0;timeline=null;frame=null;config=next;template=defs.get(config.templateId);
    document.documentElement.dataset.ready='false';document.documentElement.dataset.template=template.id;
    $('message').hidden=false;$('message').textContent='载入动画…';$('composition').replaceChildren();
    const background=library.brand.themes[config.theme].background;
    document.body.style.background=background;$('stage').style.background=background;$('message').style.background=background;
    $('canvas').hidden=template.runtime.kind!=='canvas';
    try{
      if(template.runtime.kind==='canvas')await OkouMotion.ready;
      else{
        frame=document.createElement('iframe');frame.title=template.name;frame.tabIndex=-1;
        frame.src=template.runtime.sources[config.theme]+'&hold='+config.holdSeconds;
        $('composition').append(frame);size();
        timeline=(await waitTimeline(frame,template.runtime.scene,gen)).timeline;timeline.pause();
      }
      if(gen!==loadId)return state();
      loaded=true;$('message').hidden=true;document.documentElement.dataset.ready='true';paint();
      dispatchEvent(new CustomEvent('video-motion-ready',{detail:state()}));
      if(parent!==window)parent.postMessage({type:'video-motion-ready',state:state()},location.origin==='null'?'*':location.origin);
      if(input.autoplay===true&&!matchMedia('(prefers-reduced-motion: reduce)').matches)play();
      return state();
    }catch(error){
      if(gen!==loadId)return state();
      $('message').textContent=error.message;dispatchEvent(new CustomEvent('video-motion-error',{detail:error.message}));throw error;
    }
  }
  function tick(){
    const now=performance.now();
    elapsed=Math.max(0,(now-previous)/1000);previous=now;
    if(playing&&loaded){time=Math.min(duration(),time+elapsed);paint();if(time>=duration())playing=false;}
    requestAnimationFrame(tick);
  }
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});
  new ResizeObserver(size).observe($('stage'));requestAnimationFrame(tick);
  window.VideoMotionTemplate=api;
  const p=new URLSearchParams(location.search);
  configure({templateId:p.get('template')||library.templates[0].id,theme:p.get('theme')||'dark',holdSeconds:p.has('hold')?Number(p.get('hold')):.25,speed:p.get('speed')||'standard',direction:p.get('direction')||'in',placement:p.get('placement')||'intro',autoplay:p.get('autoplay')==='1'}).catch(error=>{loaded=false;$('message').hidden=false;$('message').textContent=error.message;console.error(error)});
})();
