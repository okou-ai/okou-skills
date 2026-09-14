(function(){
  'use strict';
  const $=id=>document.getElementById(id),library=window.VIDEO_MOTION_TEMPLATES,items=library.templates,defs=new Map(items.map(x=>[x.id,x]));
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let selected=items[0],group='all',search='',controller=null,loadId=0;
  if(parent!==window)document.body.classList.add('embedded');
  function size(){if(parent!==window)parent.postMessage({type:'video-motion-library-height',height:Math.ceil(document.querySelector('main').getBoundingClientRect().height+30)},location.origin==='null'?'*':location.origin)}
  function config(){return {templateId:selected.id,theme:$('theme').value,holdSeconds:Number($('hold').value),speed:$('speed').value,direction:$('direction').value,placement:$('placement').value}}
  function setHash(){history.replaceState(null,'','#'+selected.id);if(parent!==window)parent.postMessage({type:'video-motion-selection',templateId:selected.id},location.origin==='null'?'*':location.origin)}
  function renderCards(){
    const q=search.toLowerCase().trim(),visible=items.filter(x=>(group==='all'||x.collection===group)&&(!q||[x.name,x.nameEn,x.code,x.id,x.description,x.useCase,library.families[x.family]].join(' ').toLowerCase().includes(q)));
    $('cards').innerHTML=visible.map(x=>'<button class="template-card" data-template="'+x.id+'" aria-pressed="'+(x.id===selected.id)+'" aria-label="'+esc(x.code+' '+x.name)+'"><img src="'+x.previewImage+'" width="480" height="270" alt="" loading="lazy"><span class="card-body"><span class="card-top"><strong>'+esc(x.name)+'</strong><small>'+x.code+'</small></span><span class="card-bottom"><span>'+esc(library.families[x.family])+'</span><span>'+x.defaultDurationSeconds.toFixed(2)+'s · '+(x.collection==='brand'?'品牌':'出现')+'</span></span></span></button>').join('');
    $('result-count').textContent=visible.length+' / 36 条模板';$('empty').hidden=visible.length!==0;size();
  }
  function syncDetails(){
    $('template-code').textContent=selected.code+' / '+selected.nameEn;$('collection').textContent=selected.collection==='brand'?'品牌动画':'出现方式';
    $('template-name').textContent=selected.name;$('description').textContent=selected.description;$('use-case').textContent=selected.useCase;
    $('speed-label').hidden=selected.speeds.length===1;if(!selected.speeds.includes($('speed').value))$('speed').value='standard';
    $('direction').querySelector('[value="out"]').disabled=!selected.directions.includes('out');
    if(!selected.directions.includes($('direction').value))$('direction').value='in';
    $('action-status').textContent='';
  }
  function controls(ready){for(const id of ['play','restart','download','copy','seek'])$(id).disabled=!ready}
  async function waitController(gen){
    for(let n=0;n<600;n++){
      if(gen!==loadId)return null;
      const api=$('player').contentWindow?.VideoMotionTemplate;
      if(api){await api.ready;return api}
      await new Promise(r=>setTimeout(r,50));
    }
    throw Error('播放器未能载入');
  }
  async function load({autoplay=true}={}){
    const gen=++loadId;controls(false);$('load-message').hidden=false;syncDetails();
    try{
      const api=controller||await waitController(gen);if(gen!==loadId||!api)return;
      controller=api;const desired=config(),current=controller.state();
      if(current.ready&&Object.entries(desired).every(([key,value])=>current.config[key]===value))controller.seek(0);
      else await controller.configure(desired);
      if(gen!==loadId)return;
      $('load-message').hidden=true;controls(true);
      if(matchMedia('(prefers-reduced-motion: reduce)').matches)controller.seek(controller.state().duration);
      else if(autoplay)controller.play();
      update();size();
    }catch(error){if(gen!==loadId)return;$('load-message').hidden=false;$('load-message').textContent='动画未能载入，请刷新重试';console.error(error)}
  }
  async function select(id,options={}){if(!defs.has(id))return;selected=defs.get(id);syncDetails();renderCards();setHash();await load(options)}
  function update(){
    if(!controller||!controller.state().ready)return;
    const s=controller.state();$('seek').value=Math.round(s.time/s.duration*1000);$('time').textContent=s.time.toFixed(2)+' / '+s.duration.toFixed(2)+'s';
    $('play').textContent=s.playing?'暂停':'播放';
    $('timing').textContent=(s.config.direction==='out'?'退出 ':'成形 ')+s.formationSeconds.toFixed(2)+' 秒 + 停留 '+s.config.holdSeconds.toFixed(2)+' 秒';
  }
  function shareLink(){const recipe=controller.recipe(),url=new URL('index.html',location.href);url.hash=selected.id;for(const key of ['theme','holdSeconds','speed','direction','placement'])url.searchParams.set(key,String(recipe[key]));return url.href}
  $('cards').addEventListener('click',event=>{const card=event.target.closest('[data-template]');if(card)select(card.dataset.template)});
  document.querySelectorAll('[data-group]').forEach(button=>button.addEventListener('click',()=>{group=button.dataset.group;document.querySelectorAll('[data-group]').forEach(x=>x.setAttribute('aria-pressed',x===button));renderCards()}));
  $('search').addEventListener('input',event=>{search=event.target.value;renderCards()});
  for(const id of ['theme','hold','direction','speed','placement'])$(id).addEventListener('change',()=>load());
  $('play').addEventListener('click',()=>{controller.state().playing?controller.pause():controller.play();update()});
  $('restart').addEventListener('click',()=>{controller.seek(0);controller.play();update()});
  $('seek').addEventListener('input',event=>{controller.seek(Number(event.target.value)/1000*controller.state().duration);update()});
  $('download').addEventListener('click',()=>{const recipe=controller.recipe(),blob=new Blob([JSON.stringify(recipe,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=selected.code+'-'+selected.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('action-status').textContent='已保存当前模板与设置'});
  $('copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(shareLink());$('action-status').textContent='模板链接已复制'}catch{$('action-status').textContent='可复制当前地址栏链接'}});
  window.addEventListener('hashchange',()=>{const id=location.hash.slice(1);if(defs.has(id)&&id!==selected.id)select(id)});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)controller?.pause()});
  new ResizeObserver(size).observe(document.querySelector('main'));
  function tick(){update();requestAnimationFrame(tick)}requestAnimationFrame(tick);
  const query=new URLSearchParams(location.search);for(const [key,id] of [['theme','theme'],['holdSeconds','hold'],['speed','speed'],['direction','direction'],['placement','placement']]){const value=query.get(key);if(value!==null&&[...$(id).options].some(x=>x.value===value))$(id).value=value}
  window.videoMotionLibrary={manifest:library,select,controller:()=>controller,state:()=>({selected:selected.id,group,search,player:controller?.state()}),shareLink};
  select(defs.has(location.hash.slice(1))?location.hash.slice(1):items[0].id);
})();
