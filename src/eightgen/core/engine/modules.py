"""Core game engine JavaScript modules embedded into synthesized games.

Provides zero-dependency Web Audio, particle effects, input handling,
screen shake, floating score text, and game state loops.
"""

AUDIO_CORE_JS = """
// ─── 8Gen Procedural Web Audio Engine ────────────────────────
const Sound = (() => {
  let ctx = null;
  let muted = false;

  function init() {
    if (!ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) ctx = new AudioCtx();
    }
    if (ctx && ctx.state === 'suspended') {
      ctx.resume();
    }
  }

  function playTone(freq, type = 'sine', duration = 0.1, endFreq = null, gainVal = 0.2) {
    if (muted) return;
    try {
      init();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const now = ctx.currentTime;
      osc.type = type;
      osc.frequency.setValueAtTime(freq, now);
      if (endFreq) {
        osc.frequency.exponentialRampToValueAtTime(Math.max(10, endFreq), now + duration);
      }
      gain.gain.setValueAtTime(gainVal, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + duration);
    } catch (e) {}
  }

  return {
    init,
    laser: () => playTone(880, 'sawtooth', 0.12, 110, 0.15),
    explosion: () => playTone(140, 'square', 0.25, 20, 0.25),
    hit: () => playTone(300, 'triangle', 0.08, 60, 0.2),
    pickup: () => playTone(440, 'sine', 0.15, 880, 0.2),
    jump: () => playTone(150, 'sine', 0.18, 450, 0.2),
    powerup: () => {
      playTone(330, 'sine', 0.1, 440, 0.15);
      setTimeout(() => playTone(440, 'sine', 0.15, 880, 0.18), 80);
    },
    gameover: () => {
      playTone(350, 'sawtooth', 0.2, 180, 0.2);
      setTimeout(() => playTone(180, 'sawtooth', 0.4, 60, 0.25), 200);
    },
    click: () => playTone(600, 'sine', 0.04, 800, 0.1),
    toggleMute: () => { muted = !muted; return muted; },
  };
})();
"""

PARTICLE_SYSTEM_JS = """
// ─── Particle Effects & Screen Juice ────────────────────────
class ParticleSystem {
  constructor() {
    this.particles = [];
    this.floatingTexts = [];
    this.shakeIntensity = 0;
  }

  spawnBurst(x, y, color = '#38bdf8', count = 16, speed = 4) {
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5);
      const vel = (Math.random() * 0.7 + 0.3) * speed;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * vel,
        vy: Math.sin(angle) * vel,
        radius: Math.random() * 3.5 + 1.5,
        color,
        alpha: 1,
        life: 1,
        decay: Math.random() * 0.03 + 0.02,
      });
    }
  }

  spawnFloatingText(text, x, y, color = '#ffffff') {
    this.floatingTexts.push({
      text,
      x,
      y,
      color,
      alpha: 1,
      vy: -1.5,
      life: 1,
    });
  }

  shake(amount = 6) {
    this.shakeIntensity = Math.max(this.shakeIntensity, amount);
  }

  triggerScreenShake(amount = 12) {
    this.shake(amount);
  }

  update() {
    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.96;
      p.vy *= 0.96;
      p.life -= p.decay;
      p.alpha = Math.max(0, p.life);
      if (p.life <= 0) this.particles.splice(i, 1);
    }

    // Update floating text
    for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
      const ft = this.floatingTexts[i];
      ft.y += ft.vy;
      ft.life -= 0.025;
      ft.alpha = Math.max(0, ft.life);
      if (ft.life <= 0) this.floatingTexts.splice(i, 1);
    }

    // Decay shake
    if (this.shakeIntensity > 0) {
      this.shakeIntensity *= 0.88;
      if (this.shakeIntensity < 0.2) this.shakeIntensity = 0;
    }
  }

  draw(ctx) {
    ctx.save();
    for (const p of this.particles) {
      ctx.globalAlpha = p.alpha;
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fill();
    }

    for (const ft of this.floatingTexts) {
      ctx.globalAlpha = ft.alpha;
      ctx.fillStyle = ft.color;
      ctx.font = 'bold 16px -apple-system, sans-serif';
      ctx.textAlign = 'center';
      ctx.shadowColor = 'rgba(0,0,0,0.8)';
      ctx.shadowBlur = 4;
      ctx.fillText(ft.text, ft.x, ft.y);
    }
    ctx.restore();
  }

  applyScreenShake(ctx) {
    if (this.shakeIntensity > 0) {
      const dx = (Math.random() - 0.5) * this.shakeIntensity * 2;
      const dy = (Math.random() - 0.5) * this.shakeIntensity * 2;
      ctx.translate(dx, dy);
    }
  }
}
"""

INPUT_CONTROLLER_JS = """
// ─── Universal Cross-Platform Input Controller ──────────────
const Input = (() => {
  const keys = {};
  let pointerX = 0;
  let pointerY = 0;
  let isPointerDown = false;
  let hasInteracted = false;

  window.addEventListener('keydown', (e) => {
    Sound.init();
    hasInteracted = true;
    keys[e.code] = true;
    keys[e.key] = true;
    if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
      e.preventDefault();
    }
  });

  window.addEventListener('keyup', (e) => {
    keys[e.code] = false;
    keys[e.key] = false;
  });

  function bindCanvas(canvas) {
    canvas.setAttribute('tabindex', '0');
    canvas.style.outline = 'none';

    function updatePos(e) {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      if (e.touches && e.touches[0]) {
        pointerX = (e.touches[0].clientX - rect.left) * scaleX;
        pointerY = (e.touches[0].clientY - rect.top) * scaleY;
      } else {
        pointerX = (e.clientX - rect.left) * scaleX;
        pointerY = (e.clientY - rect.top) * scaleY;
      }
    }

    canvas.addEventListener('mousemove', (e) => { updatePos(e); });
    canvas.addEventListener('mousedown', (e) => {
      canvas.focus();
      Sound.init();
      hasInteracted = true;
      isPointerDown = true;
      updatePos(e);
    });
    window.addEventListener('mouseup', () => { isPointerDown = false; });

    canvas.addEventListener('touchstart', (e) => {
      canvas.focus();
      Sound.init();
      hasInteracted = true;
      isPointerDown = true;
      updatePos(e);
      e.preventDefault();
    }, { passive: false });

    canvas.addEventListener('touchmove', (e) => {
      updatePos(e);
      e.preventDefault();
    }, { passive: false });

    window.addEventListener('touchend', () => { isPointerDown = false; });
  }

  return {
    bindCanvas,
    isDown: (code) => Boolean(keys[code]),
    isAction: () => Boolean(keys['Space'] || keys['KeyZ'] || keys['Enter'] || isPointerDown),
    isLeft: () => Boolean(keys['ArrowLeft'] || keys['KeyA']),
    isRight: () => Boolean(keys['ArrowRight'] || keys['KeyD']),
    isUp: () => Boolean(keys['ArrowUp'] || keys['KeyW']),
    isDownDir: () => Boolean(keys['ArrowDown'] || keys['KeyS']),
    pointer: () => ({ x: pointerX, y: pointerY, isDown: isPointerDown }),
    hasInteracted: () => hasInteracted,
  };
})();
"""
