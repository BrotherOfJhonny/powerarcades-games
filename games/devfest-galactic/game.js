(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const canvas = $('screen'), ctx = canvas.getContext('2d');
  const C = {bg:'#060a18',panel:'#0c1427',ink:'#e9f2ff',muted:'#8fa5bf',cyan:'#45e1ff',gold:'#ffd159',red:'#ff5473',green:'#50e19f'};
  const SHIP=['00000100000','00001110000','00001210000','01001211010','01011211010','11111211111','11122222111','11001110011','00003030000','00000300000'];
  const BUG=['010000010','001000100','011111110','112111211','111111111','001111100','011000110','110000011'];
  const BOSS=['001000100','011101110','111111111','121111121','112222211','011111110','110101011','100000001'];
  const LETTERS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -⌫✓';
  const STORE='devfest-galactic-site-v1', ORIGIN='SITE · REGISTRO NESTE NAVEGADOR';
  const images={}, keys=new Set(), held=new Set(), reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let state='title', game=null, result=null, selected=0, records=[], storageError='', ready=false;
  let last=0, acc=0, age=0, started=0, runId='', sequence=0, soundOn=true, audio=null, controlRepeat=0;
  let previousButtons=[], lastSound=0;
  const stars=Array.from({length:85},(_,i)=>({x:(i*173+31)%960,y:(i*113+53)%540,r:i%5===0?2:1}));
  function cleanName(s){return s.normalize('NFC').replace(/[^\p{L}\p{N} _-]/gu,'').trim().slice(0,12);}
  function loadRecords(){
    try {
      const raw=localStorage.getItem(STORE), values=raw?JSON.parse(raw):[];
      if(!Array.isArray(values)) throw new Error('formato inválido');
      records=values.filter(r=>r && typeof r.id==='string' && typeof r.name==='string' &&
        Number.isSafeInteger(r.score) && r.score>=0 && r.score<=100000000 &&
        Number.isSafeInteger(r.sequence) && Number.isFinite(Date.parse(r.createdAt)) && r.origin==='site')
        .map(r=>({...r,name:cleanName(r.name)}));
      sequence=records.reduce((n,r)=>Math.max(n,r.sequence),0);
    } catch(e){storageError='O ranking local não pôde ser lido. Seus dados existentes não foram substituídos.';}
  }
  function top(){return [...records].sort((a,b)=>b.score-a.score || a.sequence-b.sequence);}
  function stamp(value){return new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date(value));}
  function text(g,value,x,y,size=16,color=C.ink,align='left',font='monospace'){
    g.fillStyle=color;g.font='700 '+size+'px '+font;g.textAlign=align;g.textBaseline='top';g.fillText(String(value),x,y);
  }
  function fit(g,value,x,y,width,size=24,color=C.ink){
    g.font='700 '+size+'px system-ui';while(g.measureText(value).width>width && size>9){size--;g.font='700 '+size+'px system-ui';}
    text(g,value,x,y,size,color,'center','system-ui');
  }
  function image(g,name,x,y,w,h){
    const im=images[name],ratio=Math.min(w/im.width,h/im.height),iw=im.width*ratio,ih=im.height*ratio;
    const xx=x+(w-iw)/2,yy=y+(h-ih)/2;
    if(name==='owasp'){g.fillStyle='#dceafa';g.fillRect(xx,yy,iw,ih);}
    g.imageSmoothingEnabled=!name.endsWith('qr');g.drawImage(im,xx,yy,iw,ih);g.imageSmoothingEnabled=true;
  }
  function sprite(g,kind,x,y,color=C.cyan,scale=2,frame=0){
    const rows=kind==='ship'?SHIP:kind==='boss'?BOSS:BUG;
    rows.forEach((row,yy)=>Array.from(row).forEach((v,xx)=>{
      if(v==='0')return;g.fillStyle=v==='2'?C.ink:v==='3'?(frame%2?C.gold:C.red):color;
      g.fillRect(Math.round(x-row.length*scale/2+xx*scale),Math.round(y-rows.length*scale/2+yy*scale),scale,scale);
    }));
  }
  function panel(g,x,y,w,h){g.fillStyle=C.panel;g.fillRect(x,y,w,h);g.strokeStyle='#284461';g.strokeRect(x+.5,y+.5,w,h);}
  function background(t){
    ctx.fillStyle=C.bg;ctx.fillRect(0,0,960,540);
    stars.forEach(s=>{ctx.fillStyle='#3b526d';ctx.fillRect(s.x,reduced?s.y:(s.y+t*(s.r===2?24:12))%540,s.r,s.r);});
    ['#4285f4','#ea4335','#fbbc04','#34a853'].forEach((v,i)=>{ctx.fillStyle=v;ctx.fillRect(24+i*228,0,228,3);});
    text(ctx,'DEVFEST / GALACTIC',28,22,15);text(ctx,'ESTANDE OWASP SÃO JOSÉ DOS CAMPOS',645,24,12,C.cyan);
    ctx.strokeStyle='#23394e';ctx.beginPath();ctx.moveTo(24,58);ctx.lineTo(936,58);ctx.stroke();
    text(ctx,'05 DEZ 2026 · PIT · SÃO JOSÉ DOS CAMPOS',28,515,11,C.muted);
    text(ctx,'ORIGEM: SITE · RANKING LOCAL',665,515,11,C.gold);
  }
  function intro(t){
    background(t);image(ctx,'devfest',42,82,243,89);image(ctx,'gdg',43,180,148,45);image(ctx,'owasp',386,84,210,76);
    text(ctx,'GALACTIC',37,240,62);text(ctx,'CODE. PLAY. CONQUER.',43,318,19,C.cyan);
    text(ctx,'JOGUE NO ESTANDE OWASP SÃO JOSÉ DOS CAMPOS',43,355,12,C.gold);
    text(ctx,'www.owasp.community/chapters/sjc',43,380,12,C.muted);
    ctx.fillStyle=C.cyan;ctx.fillRect(43,407,337,39);text(ctx,'ENTER / A / TOQUE · JOGAR',211,418,15,C.bg,'center');
    text(ctx,'← → MOVER   ESPAÇO / A  TIRO',43,461,12,C.muted);
    sprite(ctx,'ship',503,398,C.cyan,5,Math.floor(t*10));
    for(let j=0;j<3;j++)sprite(ctx,j===0?'boss':'bug',510+Math.sin(t+j)*24,223+j*52,[C.gold,C.red,C.green][j],3);
    panel(ctx,624,86,292,390);text(ctx,'RANKING NESTE NAVEGADOR',646,110,15,C.gold);
    text(ctx,'CATEGORIA SITE · SEM VALIDAÇÃO ONLINE',646,143,10,C.muted);
    const rows=top().slice(0,5);
    rows.forEach((r,i)=>{const yy=186+i*51;text(ctx,String(i+1).padStart(2,'0'),645,yy,14,C.gold);fit(ctx,r.name,766,yy,157,15);text(ctx,String(r.score).padStart(7,'0'),808,yy+23,12,C.cyan);});
    if(!rows.length){text(ctx,'SEJA O PRIMEIRO',770,223,16,C.cyan,'center');text(ctx,'Seu apelido fica neste navegador.',770,259,11,C.muted,'center');}
  }
  function play(){
    const g=game;background(g.time);panel(ctx,24,77,237,421);image(ctx,'devfest',43,94,195,76);
    text(ctx,'SEU SCORE',46,199,12,C.muted);text(ctx,String(g.score).padStart(7,'0'),43,220,35,C.cyan);
    text(ctx,'RECORDE LOCAL · SITE',46,283,11,C.muted);text(ctx,String(top()[0]?.score||0).padStart(7,'0'),46,305,23,C.gold);
    text(ctx,'VIDAS',46,362,11,C.muted);for(let i=0;i<Math.min(6,g.lives);i++)sprite(ctx,'ship',58+i*30,405,C.cyan,2);
    text(ctx,g.dual?'PODER DUPLO ATIVADO':'DEFENDA A COMUNIDADE',46,455,11,C.green);
    ctx.fillStyle='#040812';ctx.fillRect(276,76,408,422);ctx.strokeStyle='#284461';ctx.strokeRect(276,76,408,422);
    ctx.save();ctx.beginPath();ctx.rect(278,78,404,418);ctx.clip();
    stars.slice(0,50).forEach(s=>{ctx.fillStyle='#304563';ctx.fillRect(286+s.x%380,80+(s.y+g.time*25)%410,s.r,s.r);});
    g.enemies.forEach(e=>{
      if(e.age<e.delay)return;
      if(e.beam){ctx.fillStyle='#104142';ctx.beginPath();ctx.moveTo(e.x-9,e.y+8);ctx.lineTo(e.x+9,e.y+8);ctx.lineTo(e.x+32,488);ctx.lineTo(e.x-32,488);ctx.fill();}
      sprite(ctx,e.boss?'boss':'bug',e.x,e.y,e.boss&&e.hp===2?C.gold:e.row%2===0?C.red:C.green,2);
      if(e.captive)sprite(ctx,'ship',e.x,e.y-25,C.red,2);
    });
    g.bullets.forEach(b=>{ctx.fillStyle=b.friendly?C.cyan:C.red;ctx.fillRect(b.x-1,b.y-4,3,9);});
    g.effects.forEach(p=>{ctx.fillStyle=C[p.color];ctx.fillRect(p.x,p.y,3,3);});
    if(g.invincible<=0||Math.floor(g.time*10)%2===0)for(const off of g.dual?[-10,10]:[0])sprite(ctx,'ship',g.playerX+off,474,C.cyan,2,Math.floor(g.time*12));
    if(g.bannerTime>0){ctx.fillStyle='#0a172b';ctx.fillRect(282,290,396,45);fit(ctx,g.banner,480,305,380,15,C.cyan);}
    ctx.restore();panel(ctx,700,77,236,421);text(ctx,'TEMPO DE MISSÃO',720,99,11,C.muted);
    const sec=Math.max(0,Math.ceil(g.remaining));text(ctx,String(Math.floor(sec/60)).padStart(2,'0')+':'+String(sec%60).padStart(2,'0'),719,125,36,sec<30?C.red:C.ink);
    text(ctx,'ONDA '+String(g.wave).padStart(2,'0'),720,193,22,C.gold);
    text(ctx,'PRECISÃO '+(g.shots?Math.round(g.hits/g.shots*100):0)+'%',720,240,13,C.cyan);
    ['← →  MOVER','A / ESPAÇO  TIRO','SEGURE PARA RAJADA','','CHEFE CAPTUROU?','DESTRUA E RESGATE!'].forEach((v,i)=>text(ctx,v,720,295+i*23,11,C.muted));
  }
  function endScreen(){
    background(0);image(ctx,'owasp',35,95,237,81);image(ctx,'devfest',40,205,225,80);image(ctx,'chapter-qr',91,330,118,118);
    panel(ctx,296,81,615,392);text(ctx,state==='name'?'MISSÃO CUMPRIDA':'MISSÃO REGISTRADA',603,104,14,C.cyan,'center');
    text(ctx,ORIGIN,603,135,11,C.gold,'center');
    fit(ctx,state==='name'?'QUAL É SEU APELIDO?':result.name,603,187,540,36);
    text(ctx,String(game.score).padStart(7,'0'),603,247,61,C.cyan,'center');
    if(result){text(ctx,result.rank+'º LUGAR NESTE NAVEGADOR',603,333,20,C.gold,'center');text(ctx,stamp(result.createdAt)+' · UTC−03',603,375,15,C.ink,'center');}
    else text(ctx,'Use o teclado virtual abaixo para salvar.',603,365,15,C.muted,'center');
    text(ctx,'COMUNIDADE OWASP SÃO JOSÉ DOS CAMPOS',603,423,15,C.ink,'center');
    text(ctx,'Registro local · sem verificação por servidor',603,451,10,C.muted,'center');
  }
  function drawCard(kind){
    const c=document.createElement('canvas');c.width=1080;c.height=kind==='story'?1920:1350;const g=c.getContext('2d');g.scale(2,2);
    const h=c.height/2,inset=kind==='story'?95:35,y=inset+193;
    g.fillStyle=C.bg;g.fillRect(0,0,540,h);
    ['#4285f4','#ea4335','#fbbc04','#34a853'].forEach((v,i)=>{g.fillStyle=v;g.fillRect(i*135,0,135,5);});
    for(let i=0;i<120;i++){g.fillStyle='#223a57';g.fillRect((i*173+31)%540,(i*113+53)%h,2,2);}
    image(g,'devfest',122,inset,296,103);image(g,'gdg',184,inset+112,172,48);
    text(g,'EU JOGUEI COM A OWASP SJC',270,y,14,C.cyan,'center');text(g,'ORIGEM: SITE · REGISTRO NESTE NAVEGADOR',270,y+22,9,C.gold,'center');
    fit(g,result.name,270,y+35,466,40);text(g,String(result.score).padStart(7,'0'),270,y+94,62,C.cyan,'center');text(g,'PONTOS',270,y+169,12,C.muted,'center');
    text(g,result.rank+'º LUGAR',270,y+201,35,C.gold,'center');text(g,'RANKING LOCAL · CATEGORIA SITE',270,y+249,10,C.muted,'center');
    text(g,stamp(result.createdAt)+' · UTC−03',270,y+276,13,C.ink,'center');text(g,'#DevFestSJC2026  #GDGSJC  #OWASPSJC',270,y+313,14,C.gold,'center');
    text(g,'www.owasp.community/chapters/sjc',270,y+345,11,C.ink,'center');
    if(kind==='story'){
      sprite(g,'ship',90,577,C.cyan,5);sprite(g,'boss',448,577,C.gold,5);
      fit(g,'ENCONTRE-NOS NO ESTANDE OWASP SJC',270,685,480,17);
      text(g,'05 DEZ 2026 · PIT · SÃO JOSÉ DOS CAMPOS',270,720,11,C.muted,'center');
    }
    const bottom=h-(kind==='story'?152:89);
    text(g,'CONHEÇA A COMUNIDADE',34,bottom+8,10,C.gold);image(g,'owasp',32,bottom+(kind==='story'?31:22),290,kind==='story'?65:48);
    image(g,'chapter-qr',398,bottom,kind==='story'?100:70,kind==='story'?100:70);
    text(g,'REGISTRO LOCAL · SEM VERIFICAÇÃO ONLINE',270,h-15,8,C.muted,'center');return c;
  }
  function updateKeyboard(){Array.from($('keyboard').children).forEach((b,i)=>{b.classList.toggle('selected',i===selected);b.setAttribute('aria-pressed',i===selected?'true':'false');});}
  function showState(next){state=next;age=0;$('name-panel').hidden=next!=='name';$('result-panel').hidden=next!=='result';}
  function start(){
    if(!ready||state==='play')return;
    unlockSound();game=new window.DevfestEngine.Game(180,crypto.getRandomValues(new Uint32Array(1))[0]);
    runId=crypto.randomUUID?crypto.randomUUID():Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join('');
    result=null;selected=0;acc=0;started=performance.now();$('player-name').value='';$('save-error').textContent='';
    $('ranking-panel').hidden=true;showState('play');$('status').textContent='Missão em andamento · categoria SITE · ranking neste navegador';canvas.focus({preventScroll:true});
  }
  function finish(){if(state!=='play')return;game.over=true;held.clear();keys.clear();showState('name');updateKeyboard();$('status').textContent='Missão encerrada. Insira seu apelido abaixo e confirme ✓ com o botão de tiro.';$('name-panel').scrollIntoView({block:'nearest',behavior:reduced?'auto':'smooth'});}
  function save(){
    const name=cleanName($('player-name').value);
    if(!name){$('save-error').textContent='Digite ou selecione seu apelido antes de salvar.';return;}
    if(storageError){$('save-error').textContent=storageError;return;}
    try{
      result=records.find(r=>r.id===runId);
      if(!result){
        const rank=1+records.filter(r=>r.score>=game.score).length;
        const row={id:runId,name,score:game.score,wave:game.wave,shots:game.shots,hits:game.hits,createdAt:new Date().toISOString(),rank,sequence:sequence+1,origin:'site'};
        const next=[...records,row];localStorage.setItem(STORE,JSON.stringify(next));records=next;sequence=row.sequence;result=row;
      }
      showState('result');const card=drawCard('feed');$('card').getContext('2d').drawImage(card,0,0);
      $('status').textContent='Pontuação salva neste navegador · origem SITE. O cartão não é um certificado de pontuação.';
      $('result-panel').scrollIntoView({block:'start',behavior:reduced?'auto':'smooth'});
    }catch(e){result=null;$('save-error').textContent='Não foi possível salvar neste navegador. Libere armazenamento ou permita dados locais e tente novamente.';}
  }
  function choose(){
    const key=LETTERS[selected];if(key==='✓'){save();return;}
    if(key==='⌫')$('player-name').value=$('player-name').value.slice(0,-1);
    else if($('player-name').value.length<12)$('player-name').value+=key;
  }
  function action(a){
    if(state==='title'&&(a==='fire'||a==='start')){start();return;}
    if(state==='name'){
      if(a==='fire')choose();else if(a==='start')save();else if(a==='back')$('player-name').value=$('player-name').value.slice(0,-1);
      else{
        let row=Math.floor(selected/10),col=selected%10;
        if(a==='left')col=(col+9)%10;if(a==='right')col=(col+1)%10;if(a==='up')row=(row+3)%4;if(a==='down')row=(row+1)%4;
        selected=row*10+col;updateKeyboard();
      }
    }else if(state==='result'&&a==='start'&&age>1)start();
  }
  function ranking(){
    if(state==='play')return;
    const list=$('score-list');list.textContent='';
    top().slice(0,15).forEach(r=>{const li=document.createElement('li');li.textContent=r.name+'  ·  '+r.score+' pts  ·  '+stamp(r.createdAt);list.appendChild(li);});
    if(!records.length){const li=document.createElement('li');li.textContent='Nenhuma missão registrada neste navegador.';list.appendChild(li);}
    $('ranking-panel').hidden=false;$('ranking-panel').scrollIntoView({block:'nearest',behavior:reduced?'auto':'smooth'});
  }
  function download(kind){if(!result)return;drawCard(kind).toBlob(blob=>{if(!blob){$('status').textContent='Falha ao gerar imagem. Tente novamente.';return;}const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='devfest-owasp-SITE-'+result.id+'-'+kind+'.png';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);},'image/png');}
  function unlockSound(){try{if(!audio)audio=new (window.AudioContext||window.webkitAudioContext)();if(audio.state==='suspended')audio.resume().catch(()=>{});}catch(e){audio=null;}}
  function beep(name){
    if(!soundOn||!audio||audio.state!=='running'||performance.now()-lastSound<30)return;
    lastSound=performance.now();const o=audio.createOscillator(),v=audio.createGain(),now=audio.currentTime;
    o.type='square';o.frequency.setValueAtTime(({shot:980,enemy:180,hit:65,bonus:660})[name]||180,now);v.gain.setValueAtTime(.035,now);v.gain.exponentialRampToValueAtTime(.001,now+.1);o.connect(v);v.connect(audio.destination);o.start();o.stop(now+.11);
  }
  function gamepad(dt){
    const pad=Array.from(navigator.getGamepads?navigator.getGamepads():[]).find(Boolean);
    if(!pad){previousButtons=[];return {move:0,fire:false};}
    const b=pad.buttons.map(v=>v.pressed),x=b[15]?1:b[14]?-1:Math.abs(pad.axes[0]||0)>.4?Math.sign(pad.axes[0]):0,y=b[13]?1:b[12]?-1:Math.abs(pad.axes[1]||0)>.4?Math.sign(pad.axes[1]):0;
    if(b[0]&&!previousButtons[0])action('fire');if(b[9]&&!previousButtons[9])action('start');if(b[1]&&!previousButtons[1])action('back');
    controlRepeat-=dt;if(state==='name'&&controlRepeat<=0&&(x||y)){action(x?(x>0?'right':'left'):(y>0?'down':'up'));controlRepeat=.17;}
    previousButtons=b;return {move:x,fire:!!b[0]};
  }
  function frame(now){
    const dt=last?Math.min((now-last)/1000,.1):0;last=now;age+=dt;
    const pad=gamepad(dt);
    if(state==='play'){
      const move=pad.move||Number(keys.has('ArrowRight')||keys.has('d')||held.has('right'))-Number(keys.has('ArrowLeft')||keys.has('a')||held.has('left'));
      const fire=pad.fire||keys.has(' ')||keys.has('z')||held.has('fire');acc+=dt;
      while(acc>=1/60&&state==='play'){
        game.update(1/60,move,fire);for(const e of new Set(game.events))beep(e);acc-=1/60;if(game.over)finish();
      }
      game.remaining=Math.max(0,180-(now-started)/1000);if(game.remaining<=0)finish();
    }
    ctx.setTransform(2,0,0,2,0,0);
    if(state==='play')play();else if(state==='title')intro(now/1000);else endScreen();
    requestAnimationFrame(frame);
  }
  LETTERS.split('').forEach((c,i)=>{const b=document.createElement('button');b.type='button';b.textContent=c;b.setAttribute('aria-label',c==='✓'?'Salvar nome e pontuação':c==='⌫'?'Apagar última letra':c===' '?'Adicionar espaço':'Adicionar letra '+c);b.addEventListener('click',()=>{selected=i;updateKeyboard();choose();});$('keyboard').appendChild(b);});
  $('name-form').addEventListener('submit',e=>{e.preventDefault();save();});
  $('start').addEventListener('click',start);$('again').addEventListener('click',start);$('ranking').addEventListener('click',ranking);
  $('sound').addEventListener('click',()=>{soundOn=!soundOn;$('sound').setAttribute('aria-pressed',String(soundOn));$('sound').textContent=soundOn?'Som ligado':'Som desligado';if(soundOn)unlockSound();});
  $('fullscreen').addEventListener('click',()=>{const target=$('jogo');if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});else if(target.requestFullscreen)target.requestFullscreen().catch(()=>{$('status').textContent='Tela cheia indisponível neste navegador.';});});
  $('download-feed').addEventListener('click',()=>download('feed'));$('download-story').addEventListener('click',()=>download('story'));
  canvas.addEventListener('click',()=>{if(state==='title')start();});
  document.querySelectorAll('[data-hold]').forEach(b=>{
    const a=b.dataset.hold;
    b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);held.add(a);action(a);});
    ['pointerup','pointercancel','lostpointercapture'].forEach(type=>b.addEventListener(type,()=>held.delete(a)));
  });
  window.addEventListener('keydown',e=>{
    if(!ready||e.altKey||e.ctrlKey||e.metaKey)return;
    if(e.target===$('player-name')){if(e.key==='Enter'){e.preventDefault();save();}return;}
    const k=e.key.length===1?e.key.toLowerCase():e.key;
    if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' ','z','Enter','Backspace'].includes(k)){
      if(e.target instanceof HTMLButtonElement && state!=='play')return;
      e.preventDefault();keys.add(k);
      if(!e.repeat){const a=({ArrowLeft:'left',ArrowRight:'right',ArrowUp:'up',ArrowDown:'down',' ':'fire',z:'fire',Enter:'start',Backspace:'back'})[k];action(a);}
    }else if(k==='a'||k==='d')keys.add(k);
  });
  window.addEventListener('keyup',e=>keys.delete(e.key.length===1?e.key.toLowerCase():e.key));
  window.addEventListener('blur',()=>{keys.clear();held.clear();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&state==='play')finish();});
  loadRecords();updateKeyboard();
  Promise.all(['devfest','gdg','gdg-symbol','owasp','chapter-qr'].map(name=>new Promise((resolve,reject)=>{
    const im=new Image();im.onload=()=>{images[name]=im;resolve();};im.onerror=()=>reject(new Error(name));im.src='assets/'+name+'.png';
  }))).then(()=>{
    const gdg=document.createElement('canvas');gdg.width=405;gdg.height=138;const g=gdg.getContext('2d');g.drawImage(images.gdg,0,0);g.drawImage(images['gdg-symbol'],4,14,139,95);images.gdg=gdg;
    ready=true;$('loading').hidden=true;$('start').disabled=false;$('ranking').disabled=false;
    $('status').textContent=storageError||'Pronto para jogar · origem SITE · ranking apenas neste navegador';requestAnimationFrame(frame);
  }).catch(()=>{$('loading').textContent='Não foi possível carregar as marcas. Recarregue a página.';$('status').textContent='Falha ao carregar os arquivos locais do jogo.';});
})();
