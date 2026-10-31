/* Simulação original de arcade. Edição web com ranking separado do bartop. */
(function (root) {
  'use strict';
  class Game {
    constructor(seconds = 180, seed = Date.now()) {
      this.seed = seed >>> 0; this.duration = seconds; this.time = 0; this.remaining = seconds;
      this.playerX = 480; this.lives = 3; this.score = 0; this.shots = 0; this.hits = 0;
      this.wave = 0; this.enemies = []; this.bullets = []; this.effects = [];
      this.shotTimer = 0; this.attackTimer = 0; this.invincible = 2;
      this.dual = false; this.captive = null; this.over = false; this.events = [];
      this.banner = ''; this.bannerTime = 0; this.transition = 0; this.nextLife = 15000;
      this.nextWave();
    }
    random() {
      this.seed = (this.seed + 0x6D2B79F5) >>> 0;
      let t = this.seed; t = Math.imul(t ^ t >>> 15, t | 1);
      t ^= t + Math.imul(t ^ t >>> 7, t | 61);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }
    nextWave() {
      this.wave++; this.challenge = this.wave % 3 === 0; this.bonusHits = 0; this.waveElapsed = 0;
      this.banner = this.challenge ? 'ONDA BÔNUS · SEM TIROS INIMIGOS' : 'ONDA ' + this.wave + ' · PREPARE-SE';
      this.bannerTime = 2.5;
      for (let row = 0; row < 4; row++) for (let col = 0; col < 8; col++) {
        const boss = row === 0 && !this.challenge;
        this.enemies.push({x: -50, y: -50, tx: 320 + col * 45, ty: 116 + row * 36,
          row, col, hp: boss ? 2 : 1, boss, mode: 'entry', age: 0, delay: (row * 8 + col) * .075,
          dive: 0, captive: false, beam: false, fired: false});
      }
      this.attackTimer = 2.8;
    }
    particle(x, y, color) {
      for (let i = 0; i < 12; i++) {
        const a = this.random() * Math.PI * 2, speed = 25 + this.random() * 95;
        this.effects.push({x, y, vx: Math.cos(a) * speed, vy: Math.sin(a) * speed, life: .5, color});
      }
    }
    hitPlayer() {
      if (this.invincible > 0 || this.over) return;
      this.particle(this.playerX, 474, 'red'); this.events.push('hit');
      if (this.dual) this.dual = false; else this.lives--;
      this.invincible = 2.5; if (this.lives <= 0) this.over = true;
    }
    enemyShot(e) {
      if (this.bullets.filter(b => !b.friendly).length >= 18) return;
      const speed = 125 + Math.min(this.wave, 15) * 6, dx = this.playerX - e.x, dy = 474 - e.y;
      const len = Math.max(1, Math.hypot(dx, dy));
      this.bullets.push({x: e.x, y: e.y + 10, vx: dx / len * speed, vy: Math.abs(dy) / len * speed, friendly: false});
    }
    update(dt, move = 0, fire = false) {
      if (this.over) return;
      this.events = []; this.time += dt; this.waveElapsed += dt; this.remaining = Math.max(0, this.duration - this.time);
      if (this.remaining <= 0) { this.over = true; return; }
      this.invincible = Math.max(0, this.invincible - dt); this.bannerTime = Math.max(0, this.bannerTime - dt);
      this.playerX = Math.min(657, Math.max(303, this.playerX + move * 235 * dt));
      this.shotTimer -= dt;
      if (fire && this.shotTimer <= 0 && this.bullets.filter(b => b.friendly).length < (this.dual ? 4 : 2)) {
        for (const offset of this.dual ? [-9, 9] : [0]) {
          this.bullets.push({x: this.playerX + offset, y: 460, vx: 0, vy: -390, friendly: true}); this.shots++;
        }
        this.shotTimer = .17; this.events.push('shot');
      }
      this.attackTimer -= dt;
      if (this.attackTimer <= 0) {
        const available = this.enemies.filter(e => e.mode === 'formation');
        if (available.length) {
          const e = available[Math.floor(this.random() * available.length)];
          Object.assign(e, {mode: 'dive', dive: 0, sx: e.x, sy: e.y, target: this.playerX});
          if (e.boss && !this.captive && !this.dual && this.lives > 1) Object.assign(e, {mode: 'beam', beam: true});
        }
        this.attackTimer = Math.max(.45, 2 - this.wave * .12);
      }
      for (const e of [...this.enemies]) {
        e.age += dt; const age = e.age - e.delay; if (age < 0) continue;
        if (e.mode === 'entry') {
          const p = Math.min(1, age / 1.6); e.x = e.tx + Math.sin(p * Math.PI * 2) * 150 * (1 - p); e.y = -30 + (e.ty + 30) * p;
          if (p >= 1) e.mode = 'formation';
        } else if (e.mode === 'formation') {
          e.x = e.tx + Math.sin(this.time * 1.1) * 14; e.y = e.ty + Math.sin(this.time * 1.6 + e.col * .3) * 4;
        } else if (e.mode === 'beam') {
          e.dive += dt; e.x = e.sx; e.y = 245;
          if (e.dive > 1 && e.dive < 2.7 && Math.abs(this.playerX - e.x) < 25 && this.invincible <= 0) {
            this.captive = e; e.captive = true; e.mode = 'formation'; e.beam = false;
            this.lives--; this.playerX = 480; this.invincible = 3;
            this.banner = 'NAVE CAPTURADA! DESTRUA O CHEFE'; this.bannerTime = 3; this.events.push('hit');
          } else if (e.dive > 3.2) { e.mode = 'formation'; e.beam = false; }
        } else {
          e.dive += dt; const p = e.dive / (2.7 - Math.min(this.wave, 12) * .07);
          e.x = e.sx + (e.target - e.sx) * Math.min(1, p * 1.7) + Math.sin(p * Math.PI * 2) * 58; e.y = e.sy + p * 460;
          if (p > .4 && p < .42 && !this.challenge && !e.fired) { this.enemyShot(e); e.fired = true; }
          if (e.y > 530) {
            if (this.challenge) { this.enemies.splice(this.enemies.indexOf(e), 1); continue; }
            Object.assign(e, {mode: 'entry', age: 0, delay: 0, fired: false});
          }
        }
        if (!this.challenge && this.random() < dt * (.035 + this.wave * .008) && e.mode === 'formation') this.enemyShot(e);
        if (Math.abs(e.x - this.playerX) < 19 && Math.abs(e.y - 474) < 16) this.hitPlayer();
      }
      if (this.challenge && this.waveElapsed > 5) for (const e of this.enemies) if (e.mode === 'formation') {
        Object.assign(e, {mode: 'dive', dive: 0, sx: e.x, sy: e.y, target: 480});
      }
      for (const b of [...this.bullets]) {
        b.x += b.vx * dt; b.y += b.vy * dt;
        let remove = b.y < 51 || b.y > 528 || b.x < 246 || b.x > 714;
        if (b.friendly) {
          for (const e of [...this.enemies]) {
            if (e.age < e.delay || Math.abs(b.x - e.x) > 14 || Math.abs(b.y - e.y) > 13) continue;
            this.hits++; e.hp--; remove = true; this.events.push('enemy');
            if (e.hp <= 0) {
              this.score += e.boss ? (e.mode === 'dive' ? 400 : 150) : (e.mode === 'dive' ? 160 : 80);
              this.bonusHits++; this.particle(e.x, e.y, e.boss ? 'gold' : 'cyan'); this.enemies.splice(this.enemies.indexOf(e), 1);
              if (e.captive) { this.dual = true; this.captive = null; this.banner = 'RESGATE! PODER DUPLO ATIVADO'; this.bannerTime = 3; this.events.push('bonus'); }
            }
            break;
          }
        } else if (Math.abs(b.x - this.playerX) < 10 && Math.abs(b.y - 474) < 12) { this.hitPlayer(); remove = true; }
        if (remove) this.bullets.splice(this.bullets.indexOf(b), 1);
      }
      for (const p of this.effects) { p.x += p.vx * dt; p.y += p.vy * dt; p.life -= dt; }
      this.effects = this.effects.filter(p => p.life > 0);
      if (this.score >= this.nextLife) { this.lives++; this.nextLife += 30000; this.events.push('bonus'); }
      if (!this.enemies.length) {
        if (this.transition === 0) {
          this.transition = 2;
          if (this.challenge) {
            const bonus = this.bonusHits === 32 ? 10000 : this.bonusHits * 100; this.score += bonus;
            this.banner = 'BÔNUS +' + bonus + ' · ' + this.bonusHits + '/32 ALVOS'; this.bannerTime = 2;
          }
        }
        this.transition -= dt;
        if (this.transition <= 0) { this.transition = 0; this.bullets = []; this.nextWave(); }
      }
    }
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {Game};
  else root.DevfestEngine = Object.freeze({Game});
})(typeof window !== 'undefined' ? window : globalThis);
