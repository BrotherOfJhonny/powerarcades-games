'use strict';
const assert = require('node:assert/strict');
const {test} = require('node:test');
const {Game} = require('../games/devfest-galactic/engine.js');
test('limites da nave e dois tiros simultâneos',()=>{
  const g=new Game(180,2);for(let i=0;i<100;i++)g.update(1/60,-1,true);
  assert.ok(g.playerX>=303);assert.ok(g.bullets.filter(b=>b.friendly).length<=2);
  for(let i=0;i<220;i++)g.update(1/60,1);assert.ok(g.playerX<=657);
});
test('expiração e fim das vidas',()=>{
  const g=new Game(1,1);for(let i=0;i<61;i++)g.update(1/60);assert.equal(g.over,true);
  const a=new Game();for(let i=0;i<3;i++){a.invincible=0;a.hitPlayer();}assert.equal(a.lives,0);assert.equal(a.over,true);
});
test('captura, chefe com dois acertos e resgate da nave dupla',()=>{
  const g=new Game(180,1),e=g.enemies[0];Object.assign(e,{x:400,y:200,age:5,mode:'beam',sx:400,sy:200,dive:1.5,beam:true});
  g.playerX=400;g.invincible=0;g.update(1/60);assert.equal(g.captive,e);assert.equal(g.lives,2);
  for(let i=0;i<2;i++){Object.assign(e,{mode:'beam',sx:400,dive:0,beam:true});g.bullets.push({x:400,y:245,vx:0,vy:0,friendly:true});g.update(1/60);}
  assert.ok(!g.enemies.includes(e));assert.equal(g.dual,true);assert.equal(g.captive,null);assert.equal(g.hits,2);
});
test('onda bônus e avanço sem inimigos',()=>{
  const g=new Game(180,1);g.wave=2;g.enemies=[];g.nextWave();assert.equal(g.challenge,true);
  g.enemies=[];g.bonusHits=32;for(let i=0;i<130;i++)g.update(1/60);assert.equal(g.score,10000);assert.equal(g.wave,4);
});
test('simulação repetível com seed e entradas iguais',()=>{
  const a=new Game(180,77),b=new Game(180,77);for(let i=0;i<600;i++){a.update(1/60,.3,true);b.update(1/60,.3,true);}
  assert.deepEqual(a,b);
});
test('dano à nave dupla preserva uma vida e remove o modo duplo',()=>{
  const g=new Game();g.dual=true;g.invincible=0;g.hitPlayer();assert.equal(g.lives,3);assert.equal(g.dual,false);
});
