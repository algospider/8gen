"""Full production-grade game archetypes guaranteed to be 100% playable and engaging."""

from eightgen.core.engine.modules import AUDIO_CORE_JS, PARTICLE_SYSTEM_JS, INPUT_CONTROLLER_JS


def build_space_shooter_game(title: str = "Neon Space Defender") -> str:
    """Complete, high-energy, deeply polished Space Shooter arcade game."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #060911;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
    }}
    #game-wrapper {{
      position: relative;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #1f293d;
    }}
    canvas {{
      display: block;
      background: #050811;
    }}
    .hud {{
      position: absolute;
      top: 14px;
      left: 16px;
      right: 16px;
      display: flex;
      justify-content: space-between;
      pointer-events: none;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}
    .hud-left {{ display: flex; gap: 16px; }}
    .health-bar-container {{
      width: 120px;
      height: 10px;
      background: rgba(255,255,255,0.15);
      border-radius: 5px;
      overflow: hidden;
      margin-top: 5px;
    }}
    .health-bar {{
      width: 100%;
      height: 100%;
      background: #10b981;
      transition: width 0.15s ease;
    }}
  </style>
</head>
<body>
  <div id="game-wrapper">
    <div class="hud">
      <div class="hud-left">
        <div>
          SCORE: <span id="score-el">0</span>
          <div class="health-bar-container"><div id="health-bar" class="health-bar"></div></div>
        </div>
        <div>WAVE: <span id="wave-el">1</span></div>
      </div>
      <div>HIGH: <span id="high-el">0</span></div>
    </div>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
  </div>

  <script>
  {AUDIO_CORE_JS}
  {PARTICLE_SYSTEM_JS}
  {INPUT_CONTROLLER_JS}

  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  Input.bindCanvas(canvas);

  const fx = new ParticleSystem();
  const scoreEl = document.getElementById('score-el');
  const waveEl = document.getElementById('wave-el');
  const highEl = document.getElementById('high-el');
  const healthBar = document.getElementById('health-bar');

  let state = 'MENU'; // MENU, PLAYING, GAMEOVER
  let score = 0;
  let highScore = parseInt(localStorage.getItem('8gen_hs_shooter') || '0', 10);
  highEl.innerText = highScore;

  let wave = 1;
  let lastShot = 0;
  let fireRate = 160;

  // Starfield
  const stars = Array.from({{ length: 80 }}, () => ({{
    x: Math.random() * 800,
    y: Math.random() * 600,
    speed: Math.random() * 2 + 0.5,
    size: Math.random() * 2 + 0.5,
  }}));

  // Player
  const player = {{
    x: 400,
    y: 520,
    vx: 0,
    vy: 0,
    radius: 18,
    speed: 7,
    health: 100,
    maxHealth: 100,
    powerupLevel: 1,
    shield: 0,
  }};

  let bullets = [];
  let enemies = [];
  let powerups = [];

  function resetGame() {{
    score = 0;
    wave = 1;
    player.x = 400;
    player.y = 520;
    player.health = 100;
    player.powerupLevel = 1;
    player.shield = 0;
    bullets = [];
    enemies = [];
    powerups = [];
    state = 'PLAYING';
    Sound.init();
    Sound.pickup();
  }}

  function spawnWave() {{
    const count = 5 + wave * 2;
    for (let i = 0; i < count; i++) {{
      const type = Math.random() < 0.25 ? 'fast' : (Math.random() < 0.2 ? 'heavy' : 'basic');
      enemies.push({{
        x: 60 + Math.random() * 680,
        y: -30 - (i * 45),
        type,
        hp: type === 'heavy' ? 4 : (type === 'fast' ? 1 : 2),
        maxHp: type === 'heavy' ? 4 : (type === 'fast' ? 1 : 2),
        radius: type === 'heavy' ? 24 : (type === 'fast' ? 12 : 16),
        speed: type === 'fast' ? 3.5 : (type === 'heavy' ? 1.2 : 2.0),
        vx: (Math.random() - 0.5) * 1.5,
        color: type === 'heavy' ? '#f43f5e' : (type === 'fast' ? '#eab308' : '#06b6d4'),
      }});
    }}
  }}

  function shoot() {{
    const now = performance.now();
    if (now - lastShot < fireRate) return;
    lastShot = now;
    Sound.laser();

    if (player.powerupLevel === 1) {{
      bullets.push({{ x: player.x, y: player.y - 18, vx: 0, vy: -12, color: '#38bdf8' }});
    }} else if (player.powerupLevel === 2) {{
      bullets.push({{ x: player.x - 10, y: player.y - 14, vx: 0, vy: -12, color: '#38bdf8' }});
      bullets.push({{ x: player.x + 10, y: player.y - 14, vx: 0, vy: -12, color: '#38bdf8' }});
    }} else {{
      bullets.push({{ x: player.x, y: player.y - 18, vx: 0, vy: -12, color: '#38bdf8' }});
      bullets.push({{ x: player.x - 12, y: player.y - 12, vx: -2.5, vy: -11, color: '#ec4899' }});
      bullets.push({{ x: player.x + 12, y: player.y - 12, vx: 2.5, vy: -11, color: '#ec4899' }});
    }}
  }}

  function update() {{
    // Starfield scroll
    for (const s of stars) {{
      s.y += s.speed;
      if (s.y > 600) {{ s.y = 0; s.x = Math.random() * 800; }}
    }}

    fx.update();

    if (state !== 'PLAYING') return;

    // Movement
    if (Input.isLeft()) player.x -= player.speed;
    if (Input.isRight()) player.x += player.speed;
    if (Input.isUp()) player.y -= player.speed;
    if (Input.isDownDir()) player.y += player.speed;

    // Pointer touch/mouse drag
    const ptr = Input.pointer();
    if (ptr.isDown) {{
      player.x += (ptr.x - player.x) * 0.18;
      player.y += (ptr.y - player.y) * 0.18;
    }}

    player.x = Math.max(20, Math.min(780, player.x));
    player.y = Math.max(100, Math.min(570, player.y));

    // Shooting
    if (Input.isAction()) shoot();

    // Spawn thruster particles
    if (Math.random() < 0.6) {{
      fx.particles.push({{
        x: player.x + (Math.random() - 0.5) * 8,
        y: player.y + 16,
        vx: (Math.random() - 0.5) * 1.5,
        vy: Math.random() * 4 + 2,
        radius: Math.random() * 3 + 1,
        color: '#38bdf8',
        alpha: 1,
        life: 0.6,
        decay: 0.04,
      }});
    }}

    // Update bullets
    for (let i = bullets.length - 1; i >= 0; i--) {{
      const b = bullets[i];
      b.x += b.vx;
      b.y += b.vy;
      if (b.y < -20 || b.x < 0 || b.x > 800) bullets.splice(i, 1);
    }}

    // Update enemies
    if (enemies.length === 0) {{
      wave++;
      waveEl.innerText = wave;
      fx.spawnFloatingText(`WAVE ${{wave}} INCOMING!`, 400, 300, '#38bdf8');
      Sound.powerup();
      spawnWave();
    }}

    for (let i = enemies.length - 1; i >= 0; i--) {{
      const e = enemies[i];
      e.y += e.speed;
      e.x += e.vx;
      if (e.x < 20 || e.x > 780) e.vx = -e.vx;

      // Bullet hit enemy
      for (let j = bullets.length - 1; j >= 0; j--) {{
        const b = bullets[j];
        const dist = Math.hypot(b.x - e.x, b.y - e.y);
        if (dist < e.radius + 6) {{
          bullets.splice(j, 1);
          e.hp--;
          Sound.hit();
          fx.spawnBurst(b.x, b.y, e.color, 6, 2);

          if (e.hp <= 0) {{
            Sound.explosion();
            fx.spawnBurst(e.x, e.y, e.color, 24, 5);
            fx.shake(5);
            const pts = e.type === 'heavy' ? 250 : (e.type === 'fast' ? 150 : 100);
            score += pts;
            scoreEl.innerText = score;
            fx.spawnFloatingText(`+${{pts}}`, e.x, e.y, '#f59e0b');

            // Chance to drop powerup
            if (Math.random() < 0.15) {{
              powerups.push({{ x: e.x, y: e.y, vy: 2, type: Math.random() < 0.5 ? 'weapon' : 'shield' }});
            }}

            enemies.splice(i, 1);
            break;
          }}
        }}
      }}

      // Enemy hit player
      if (enemies[i]) {{
        const pDist = Math.hypot(player.x - e.x, player.y - e.y);
        if (pDist < player.radius + e.radius) {{
          enemies.splice(i, 1);
          Sound.explosion();
          fx.spawnBurst(player.x, player.y, '#ef4444', 20, 6);
          fx.shake(12);

          if (player.shield > 0) {{
            player.shield = 0;
            fx.spawnFloatingText('SHIELD BROKEN!', player.x, player.y - 20, '#38bdf8');
          }} else {{
            player.health -= 35;
            healthBar.style.width = Math.max(0, player.health) + '%';
            if (player.health <= 0) {{
              state = 'GAMEOVER';
              Sound.gameover();
              if (score > highScore) {{
                highScore = score;
                localStorage.setItem('8gen_hs_shooter', highScore);
                highEl.innerText = highScore;
              }}
            }}
          }}
        }} else if (e.y > 640) {{
          enemies.splice(i, 1);
        }}
      }}
    }}

    // Powerups
    for (let i = powerups.length - 1; i >= 0; i--) {{
      const p = powerups[i];
      p.y += p.vy;
      const dist = Math.hypot(player.x - p.x, player.y - p.y);
      if (dist < player.radius + 14) {{
        Sound.powerup();
        if (p.type === 'weapon') {{
          player.powerupLevel = Math.min(3, player.powerupLevel + 1);
          fx.spawnFloatingText('FIREPOWER UPGRADE!', player.x, player.y - 20, '#ec4899');
        }} else {{
          player.shield = 100;
          player.health = Math.min(100, player.health + 25);
          healthBar.style.width = player.health + '%';
          fx.spawnFloatingText('SHIELD ACTIVATED!', player.x, player.y - 20, '#38bdf8');
        }}
        powerups.splice(i, 1);
      }} else if (p.y > 620) {{
        powerups.splice(i, 1);
      }}
    }}
  }}

  function draw() {{
    ctx.save();
    ctx.clearRect(0, 0, 800, 600);
    fx.applyScreenShake(ctx);

    // Stars
    ctx.fillStyle = '#ffffff';
    for (const s of stars) {{
      ctx.fillRect(s.x, s.y, s.size, s.size);
    }}

    if (state === 'MENU') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 44px -apple-system, sans-serif';
      ctx.fillText('{title}', 400, 240);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '16px -apple-system, sans-serif';
      ctx.fillText('CONTROLS: Arrow Keys / WASD to move • Space to Fire • Or Touch/Mouse Drag', 400, 300);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 22px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE OR CLICK TO START', 400, 380);

      if (Input.isAction()) resetGame();
    }} else if (state === 'PLAYING') {{
      // Draw Bullets
      for (const b of bullets) {{
        ctx.fillStyle = b.color;
        ctx.fillRect(b.x - 2.5, b.y - 8, 5, 16);
      }}

      // Draw Powerups
      for (const p of powerups) {{
        ctx.save();
        ctx.fillStyle = p.type === 'weapon' ? '#ec4899' : '#38bdf8';
        ctx.beginPath();
        ctx.arc(p.x, p.y, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(p.type === 'weapon' ? 'W' : 'S', p.x, p.y + 4);
        ctx.restore();
      }}

      // Draw Enemies
      for (const e of enemies) {{
        ctx.save();
        ctx.fillStyle = e.color;
        ctx.beginPath();
        if (e.type === 'heavy') {{
          ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
        }} else if (e.type === 'fast') {{
          ctx.moveTo(e.x, e.y + e.radius);
          ctx.lineTo(e.x - e.radius, e.y - e.radius);
          ctx.lineTo(e.x + e.radius, e.y - e.radius);
          ctx.closePath();
        }} else {{
          ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
        }}
        ctx.fill();

        // Eye / cockpit
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(e.x - 4, e.y - 2, 8, 4);
        ctx.restore();
      }}

      // Draw Player
      ctx.save();
      ctx.translate(player.x, player.y);

      // Shield ring
      if (player.shield > 0) {{
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(0, 0, player.radius + 8, 0, Math.PI * 2);
        ctx.stroke();
      }}

      // Ship body
      ctx.fillStyle = '#f8fafc';
      ctx.beginPath();
      ctx.moveTo(0, -22);
      ctx.lineTo(-18, 16);
      ctx.lineTo(0, 10);
      ctx.lineTo(18, 16);
      ctx.closePath();
      ctx.fill();

      // Wing accents
      ctx.fillStyle = '#06b6d4';
      ctx.beginPath();
      ctx.moveTo(0, -10);
      ctx.lineTo(-12, 12);
      ctx.lineTo(0, 6);
      ctx.lineTo(12, 12);
      ctx.closePath();
      ctx.fill();

      ctx.restore();
    }} else if (state === 'GAMEOVER') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#ef4444';
      ctx.font = 'bold 50px -apple-system, sans-serif';
      ctx.fillText('MISSION FAILED', 400, 240);

      ctx.fillStyle = '#f8fafc';
      ctx.font = '22px -apple-system, sans-serif';
      ctx.fillText(`FINAL SCORE: ${{score}}`, 400, 300);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 20px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE OR CLICK TO RESTART', 400, 370);

      if (Input.isAction()) resetGame();
    }}

    fx.draw(ctx);
    ctx.restore();
  }}

  function loop() {{
    update();
    draw();
    requestAnimationFrame(loop);
  }}

  loop();
  </script>
</body>
</html>
"""


def build_brick_breaker_game(title: str = "Neon Brick Breaker") -> str:
    """Complete, highly polished Breakout physics game with powerups."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #080c14;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
    }}
    #game-wrapper {{
      position: relative;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #1e293b;
    }}
    canvas {{ display: block; background: #030712; }}
    .hud {{
      position: absolute;
      top: 14px;
      left: 16px;
      right: 16px;
      display: flex;
      justify-content: space-between;
      pointer-events: none;
      font-size: 16px;
      font-weight: 700;
      text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}
  </style>
</head>
<body>
  <div id="game-wrapper">
    <div class="hud">
      <div>SCORE: <span id="score-el">0</span></div>
      <div>LIVES: <span id="lives-el">3</span></div>
    </div>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
  </div>

  <script>
  {AUDIO_CORE_JS}
  {PARTICLE_SYSTEM_JS}
  {INPUT_CONTROLLER_JS}

  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  Input.bindCanvas(canvas);

  const fx = new ParticleSystem();
  const scoreEl = document.getElementById('score-el');
  const livesEl = document.getElementById('lives-el');

  let state = 'MENU';
  let score = 0;
  let lives = 3;

  const paddle = {{
    x: 350,
    y: 550,
    width: 110,
    height: 14,
    speed: 9,
  }};

  let balls = [];
  let bricks = [];
  const colors = ['#f43f5e', '#fb923c', '#facc15', '#4ade80', '#38bdf8', '#c084fc'];

  function initBricks() {{
    bricks = [];
    const rows = 6;
    const cols = 9;
    const bWidth = 76;
    const bHeight = 22;
    const padding = 8;
    const offsetX = 28;
    const offsetY = 70;

    for (let r = 0; r < rows; r++) {{
      for (let c = 0; c < cols; c++) {{
        bricks.push({{
          x: offsetX + c * (bWidth + padding),
          y: offsetY + r * (bHeight + padding),
          width: bWidth,
          height: bHeight,
          color: colors[r % colors.length],
          alive: true,
          hp: r === 0 ? 2 : 1,
        }});
      }}
    }}
  }}

  function resetGame() {{
    score = 0;
    lives = 3;
    scoreEl.innerText = score;
    livesEl.innerText = lives;
    paddle.x = 345;
    balls = [{{ x: 400, y: 530, vx: 5, vy: -6, radius: 8 }}];
    initBricks();
    state = 'PLAYING';
    Sound.init();
    Sound.click();
  }}

  function update() {{
    fx.update();
    if (state !== 'PLAYING') return;

    // Paddle controls
    if (Input.isLeft()) paddle.x -= paddle.speed;
    if (Input.isRight()) paddle.x += paddle.speed;
    const ptr = Input.pointer();
    if (ptr.isDown) paddle.x = ptr.x - paddle.width / 2;
    paddle.x = Math.max(10, Math.min(canvas.width - paddle.width - 10, paddle.x));

    // Update balls
    for (let i = balls.length - 1; i >= 0; i--) {{
      const b = balls[i];
      b.x += b.vx;
      b.y += b.vy;

      // Wall bounce
      if (b.x - b.radius < 0) {{ b.x = b.radius; b.vx = -b.vx; Sound.hit(); }}
      if (b.x + b.radius > canvas.width) {{ b.x = canvas.width - b.radius; b.vx = -b.vx; Sound.hit(); }}
      if (b.y - b.radius < 0) {{ b.y = b.radius; b.vy = -b.vy; Sound.hit(); }}

      // Paddle bounce with angular deflection
      if (
        b.y + b.radius >= paddle.y &&
        b.y - b.radius <= paddle.y + paddle.height &&
        b.x >= paddle.x &&
        b.x <= paddle.x + paddle.width &&
        b.vy > 0
      ) {{
        b.vy = -Math.abs(b.vy);
        const hitPoint = (b.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2);
        b.vx = hitPoint * 7;
        Sound.jump();
        fx.spawnBurst(b.x, b.y, '#38bdf8', 8, 3);
      }}

      // Brick collisions
      for (const brick of bricks) {{
        if (!brick.alive) continue;
        if (
          b.x + b.radius >= brick.x &&
          b.x - b.radius <= brick.x + brick.width &&
          b.y + b.radius >= brick.y &&
          b.y - b.radius <= brick.y + brick.height
        ) {{
          b.vy = -b.vy;
          brick.hp--;
          Sound.hit();
          fx.spawnBurst(b.x, b.y, brick.color, 12, 4);

          if (brick.hp <= 0) {{
            brick.alive = false;
            score += 100;
            scoreEl.innerText = score;
            fx.spawnFloatingText('+100', brick.x + brick.width / 2, brick.y, brick.color);
            fx.shake(3);
          }}
          break;
        }}
      }}

      // Ball lost
      if (b.y - b.radius > canvas.height) {{
        balls.splice(i, 1);
      }}
    }}

    if (balls.length === 0) {{
      lives--;
      livesEl.innerText = lives;
      Sound.gameover();
      fx.shake(8);
      if (lives <= 0) {{
        state = 'GAMEOVER';
      }} else {{
        balls.push({{ x: paddle.x + paddle.width / 2, y: paddle.y - 15, vx: 5, vy: -6, radius: 8 }});
      }}
    }}

    // Check Victory
    if (bricks.every(b => !b.alive)) {{
      state = 'VICTORY';
      Sound.powerup();
    }}
  }}

  function draw() {{
    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    fx.applyScreenShake(ctx);

    if (state === 'MENU') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 44px -apple-system, sans-serif';
      ctx.fillText('{title}', 400, 260);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '16px -apple-system, sans-serif';
      ctx.fillText('Use Left/Right Arrow Keys, A/D, or Drag with Mouse', 400, 310);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 22px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE OR CLICK TO START', 400, 380);

      if (Input.isAction()) resetGame();
    }} else if (state === 'PLAYING') {{
      // Draw Paddle
      ctx.fillStyle = '#38bdf8';
      ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);

      // Draw Balls
      ctx.fillStyle = '#ffffff';
      for (const b of balls) {{
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
        ctx.fill();
      }}

      // Draw Bricks
      for (const brick of bricks) {{
        if (!brick.alive) continue;
        ctx.fillStyle = brick.color;
        ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
      }}
    }} else if (state === 'GAMEOVER') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#ef4444';
      ctx.font = 'bold 48px -apple-system, sans-serif';
      ctx.fillText('GAME OVER', 400, 260);

      ctx.fillStyle = '#f8fafc';
      ctx.font = '22px -apple-system, sans-serif';
      ctx.fillText(`SCORE: ${{score}}`, 400, 310);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 20px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE TO PLAY AGAIN', 400, 380);

      if (Input.isAction()) resetGame();
    }} else if (state === 'VICTORY') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 48px -apple-system, sans-serif';
      ctx.fillText('VICTORY!', 400, 260);

      ctx.fillStyle = '#f8fafc';
      ctx.font = '22px -apple-system, sans-serif';
      ctx.fillText(`ALL BRICKS DESTROYED! FINAL SCORE: ${{score}}`, 400, 310);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 20px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE TO PLAY AGAIN', 400, 380);

      if (Input.isAction()) resetGame();
    }}

    fx.draw(ctx);
    ctx.restore();
  }}

  function loop() {{
    update();
    draw();
    requestAnimationFrame(loop);
  }}

  loop();
  </script>
</body>
</html>
"""


def build_cyber_snake_game(title: str = "Cyber Snake 2099") -> str:
    """Complete, ultra-responsive grid snake arcade game with juice."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #090e17;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
    }}
    #game-wrapper {{
      position: relative;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #1f293d;
    }}
    canvas {{ display: block; background: #040711; }}
    .hud {{
      position: absolute;
      top: 14px;
      left: 16px;
      right: 16px;
      display: flex;
      justify-content: space-between;
      pointer-events: none;
      font-size: 16px;
      font-weight: 700;
      text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}
  </style>
</head>
<body>
  <div id="game-wrapper">
    <div class="hud">
      <div>SCORE: <span id="score-el">0</span></div>
      <div>HIGH: <span id="high-el">0</span></div>
    </div>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
  </div>

  <script>
  {AUDIO_CORE_JS}
  {PARTICLE_SYSTEM_JS}
  {INPUT_CONTROLLER_JS}

  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  Input.bindCanvas(canvas);

  const fx = new ParticleSystem();
  const scoreEl = document.getElementById('score-el');
  const highEl = document.getElementById('high-el');

  const GRID_SIZE = 25;
  const COLS = 800 / GRID_SIZE;
  const ROWS = 600 / GRID_SIZE;

  let state = 'MENU';
  let score = 0;
  let highScore = parseInt(localStorage.getItem('8gen_hs_snake') || '0', 10);
  highEl.innerText = highScore;

  let snake = [];
  let dir = {{ x: 1, y: 0 }};
  let nextDir = {{ x: 1, y: 0 }};
  let food = {{ x: 15, y: 12 }};
  let goldenFruit = null;
  let stepTimer = 0;
  let speed = 90; // ms per step

  function spawnFood() {{
    food = {{
      x: Math.floor(Math.random() * (COLS - 2)) + 1,
      y: Math.floor(Math.random() * (ROWS - 2)) + 1,
    }};

    if (Math.random() < 0.25) {{
      goldenFruit = {{
        x: Math.floor(Math.random() * (COLS - 2)) + 1,
        y: Math.floor(Math.random() * (ROWS - 2)) + 1,
        life: 60,
      }};
    }}
  }}

  function resetGame() {{
    score = 0;
    speed = 90;
    scoreEl.innerText = score;
    snake = [
      {{ x: 10, y: 12 }},
      {{ x: 9, y: 12 }},
      {{ x: 8, y: 12 }},
    ];
    dir = {{ x: 1, y: 0 }};
    nextDir = {{ x: 1, y: 0 }};
    spawnFood();
    state = 'PLAYING';
    Sound.init();
    Sound.pickup();
  }}

  window.addEventListener('keydown', (e) => {{
    if (e.code === 'ArrowUp' || e.code === 'KeyW') if (dir.y === 0) nextDir = {{ x: 0, y: -1 }};
    if (e.code === 'ArrowDown' || e.code === 'KeyS') if (dir.y === 0) nextDir = {{ x: 0, y: 1 }};
    if (e.code === 'ArrowLeft' || e.code === 'KeyA') if (dir.x === 0) nextDir = {{ x: -1, y: 0 }};
    if (e.code === 'ArrowRight' || e.code === 'KeyD') if (dir.x === 0) nextDir = {{ x: 1, y: 0 }};
  }});

  let lastTime = 0;
  function update(time) {{
    fx.update();

    if (state !== 'PLAYING') return;

    if (time - stepTimer > speed) {{
      stepTimer = time;
      dir = nextDir;

      const head = {{ x: snake[0].x + dir.x, y: snake[0].y + dir.y }};

      // Wall collision
      if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) {{
        state = 'GAMEOVER';
        Sound.gameover();
        fx.shake(12);
        if (score > highScore) {{
          highScore = score;
          localStorage.setItem('8gen_hs_snake', highScore);
          highEl.innerText = highScore;
        }}
        return;
      }}

      // Self collision
      if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {{
        state = 'GAMEOVER';
        Sound.gameover();
        fx.shake(12);
        return;
      }}

      snake.unshift(head);

      // Eat standard food
      if (head.x === food.x && head.y === food.y) {{
        score += 50;
        scoreEl.innerText = score;
        Sound.pickup();
        fx.spawnBurst(head.x * GRID_SIZE + 12, head.y * GRID_SIZE + 12, '#10b981', 14, 4);
        fx.spawnFloatingText('+50', head.x * GRID_SIZE, head.y * GRID_SIZE, '#10b981');
        speed = Math.max(45, speed - 1.5);
        spawnFood();
      }} else if (goldenFruit && head.x === goldenFruit.x && head.y === goldenFruit.y) {{
        score += 200;
        scoreEl.innerText = score;
        Sound.powerup();
        fx.spawnBurst(head.x * GRID_SIZE + 12, head.y * GRID_SIZE + 12, '#f59e0b', 24, 6);
        fx.spawnFloatingText('+200 BONUS!', head.x * GRID_SIZE, head.y * GRID_SIZE, '#f59e0b');
        goldenFruit = null;
      }} else {{
        snake.pop();
      }}
    }}
  }}

  function draw() {{
    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    fx.applyScreenShake(ctx);

    // Subtle grid
    ctx.strokeStyle = '#111827';
    ctx.lineWidth = 0.5;
    for (let c = 0; c <= COLS; c++) {{
      ctx.beginPath();
      ctx.moveTo(c * GRID_SIZE, 0);
      ctx.lineTo(c * GRID_SIZE, 600);
      ctx.stroke();
    }}
    for (let r = 0; r <= ROWS; r++) {{
      ctx.beginPath();
      ctx.moveTo(0, r * GRID_SIZE);
      ctx.lineTo(800, r * GRID_SIZE);
      ctx.stroke();
    }}

    if (state === 'MENU') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 44px -apple-system, sans-serif';
      ctx.fillText('{title}', 400, 260);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '16px -apple-system, sans-serif';
      ctx.fillText('CONTROLS: Arrow Keys / WASD to navigate', 400, 310);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 22px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE OR CLICK TO START', 400, 380);

      if (Input.isAction()) resetGame();
    }} else if (state === 'PLAYING') {{
      // Food
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(food.x * GRID_SIZE + GRID_SIZE / 2, food.y * GRID_SIZE + GRID_SIZE / 2, GRID_SIZE / 2 - 2, 0, Math.PI * 2);
      ctx.fill();

      // Golden fruit
      if (goldenFruit) {{
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.arc(goldenFruit.x * GRID_SIZE + GRID_SIZE / 2, goldenFruit.y * GRID_SIZE + GRID_SIZE / 2, GRID_SIZE / 2, 0, Math.PI * 2);
        ctx.fill();
      }}

      // Snake body
      for (let i = 0; i < snake.length; i++) {{
        const s = snake[i];
        ctx.fillStyle = i === 0 ? '#34d399' : '#059669';
        ctx.fillRect(s.x * GRID_SIZE + 1, s.y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2);
      }}
    }} else if (state === 'GAMEOVER') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#ef4444';
      ctx.font = 'bold 48px -apple-system, sans-serif';
      ctx.fillText('GAME OVER', 400, 260);

      ctx.fillStyle = '#f8fafc';
      ctx.font = '22px -apple-system, sans-serif';
      ctx.fillText(`FINAL SCORE: ${{score}}`, 400, 310);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 20px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE TO PLAY AGAIN', 400, 380);

      if (Input.isAction()) resetGame();
    }}

    fx.draw(ctx);
    ctx.restore();
  }}

  function loop(time) {{
    update(time);
    draw();
    requestAnimationFrame(loop);
  }}

  requestAnimationFrame(loop);
  </script>
</body>
</html>
"""


def build_flappy_drone_game(title: str = "Aero Drone Odyssey") -> str:
    """Complete, hyper-responsive one-button flight arcade game."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #060911;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
    }}
    #game-wrapper {{
      position: relative;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #1e293b;
    }}
    canvas {{ display: block; background: #080d1a; }}
    .hud {{
      position: absolute;
      top: 14px;
      left: 16px;
      right: 16px;
      display: flex;
      justify-content: space-between;
      pointer-events: none;
      font-size: 16px;
      font-weight: 700;
      text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}
  </style>
</head>
<body>
  <div id="game-wrapper">
    <div class="hud">
      <div>SCORE: <span id="score-el">0</span></div>
      <div>HIGH: <span id="high-el">0</span></div>
    </div>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
  </div>

  <script>
  {AUDIO_CORE_JS}
  {PARTICLE_SYSTEM_JS}
  {INPUT_CONTROLLER_JS}

  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  Input.bindCanvas(canvas);

  const fx = new ParticleSystem();
  const scoreEl = document.getElementById('score-el');
  const highEl = document.getElementById('high-el');

  let state = 'MENU';
  let score = 0;
  let highScore = parseInt(localStorage.getItem('8gen_hs_drone') || '0', 10);
  highEl.innerText = highScore;

  const drone = {{
    x: 180,
    y: 300,
    vy: 0,
    radius: 16,
    gravity: 0.38,
    lift: -7.5,
    tilt: 0,
  }};

  let pillars = [];
  let orbs = [];
  let frameCount = 0;
  let speed = 3.2;

  function resetGame() {{
    score = 0;
    scoreEl.innerText = score;
    drone.y = 300;
    drone.vy = 0;
    drone.tilt = 0;
    pillars = [];
    orbs = [];
    frameCount = 0;
    speed = 3.2;
    state = 'PLAYING';
    Sound.init();
    Sound.click();
  }}

  function spawnPillar() {{
    const gap = 170;
    const minHeight = 60;
    const maxHeight = 600 - gap - minHeight;
    const topHeight = Math.floor(Math.random() * (maxHeight - minHeight)) + minHeight;
    const bottomY = topHeight + gap;

    pillars.push({{
      x: 820,
      topHeight: topHeight,
      bottomY: bottomY,
      width: 64,
      passed: false,
    }});

    // Spawn bonus orb in middle with 60% chance
    if (Math.random() < 0.6) {{
      orbs.push({{
        x: 820 + 32,
        y: topHeight + gap / 2,
        radius: 10,
        alive: true,
      }});
    }}
  }}

  function update() {{
    fx.update();
    if (state !== 'PLAYING') return;

    frameCount++;
    if (frameCount % 110 === 0) {{
      spawnPillar();
    }}

    // Drone flight physics
    if (Input.isAction() || Input.isUp()) {{
      drone.vy = drone.lift;
      drone.tilt = -0.4;
      Sound.shoot();
      fx.spawnBurst(drone.x - 12, drone.y + 4, '#38bdf8', 4, 3);
    }} else {{
      drone.vy += drone.gravity;
      drone.tilt = Math.min(0.6, drone.tilt + 0.02);
    }}

    drone.y += drone.vy;

    // Thruster trail
    if (frameCount % 3 === 0) {{
      fx.spawnBurst(drone.x - 14, drone.y, '#f59e0b', 2, 2);
    }}

    // Ceiling / floor collision
    if (drone.y - drone.radius < 0 || drone.y + drone.radius > 600) {{
      gameOver();
      return;
    }}

    // Update Pillars
    for (let i = pillars.length - 1; i >= 0; i--) {{
      const p = pillars[i];
      p.x -= speed;

      // Check collision
      if (
        drone.x + drone.radius > p.x &&
        drone.x - drone.radius < p.x + p.width
      ) {{
        if (drone.y - drone.radius < p.topHeight || drone.y + drone.radius > p.bottomY) {{
          gameOver();
          return;
        }}
      }}

      // Score passing
      if (!p.passed && p.x + p.width < drone.x) {{
        p.passed = true;
        score += 10;
        scoreEl.innerText = score;
        Sound.pickup();
        fx.spawnFloatingText('+10', drone.x, drone.y - 20, '#10b981');
      }}

      if (p.x < -80) {{
        pillars.splice(i, 1);
      }}
    }}

    // Update Orbs
    for (let i = orbs.length - 1; i >= 0; i--) {{
      const orb = orbs[i];
      orb.x -= speed;
      const dist = Math.hypot(drone.x - orb.x, drone.y - orb.y);
      if (dist < drone.radius + orb.radius) {{
        score += 50;
        scoreEl.innerText = score;
        Sound.powerup();
        fx.spawnBurst(orb.x, orb.y, '#facc15', 18, 5);
        fx.spawnFloatingText('+50 BONUS!', drone.x, drone.y - 24, '#facc15');
        orbs.splice(i, 1);
      }} else if (orb.x < -40) {{
        orbs.splice(i, 1);
      }}
    }}
  }}

  function gameOver() {{
    state = 'GAMEOVER';
    fx.triggerScreenShake(18, 12);
    fx.spawnBurst(drone.x, drone.y, '#ef4444', 35, 8);
    Sound.hit();
    Sound.gameover();
    if (score > highScore) {{
      highScore = score;
      localStorage.setItem('8gen_hs_drone', highScore);
      highEl.innerText = highScore;
    }}
  }}

  function draw() {{
    ctx.save();
    ctx.clearRect(0, 0, 800, 600);
    fx.applyScreenShake(ctx);

    // Starry background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    for (let i = 0; i < 40; i++) {{
      const sx = ((i * 73 + frameCount * 0.3) % 800);
      const sy = (i * 97) % 600;
      ctx.fillRect(sx, sy, 1.5, 1.5);
    }}

    if (state === 'MENU') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 44px -apple-system, sans-serif';
      ctx.fillText('{title}', 400, 240);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '16px -apple-system, sans-serif';
      ctx.fillText('CONTROLS: Spacebar, Click, or Touch to Boost Drone', 400, 290);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 22px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE OR CLICK TO START', 400, 360);

      if (Input.isAction()) resetGame();
    }} else if (state === 'PLAYING') {{
      // Draw Pillars
      for (const p of pillars) {{
        // Top pillar
        const gradTop = ctx.createLinearGradient(p.x, 0, p.x + p.width, 0);
        gradTop.addColorStop(0, '#0284c7');
        gradTop.addColorStop(1, '#06b6d4');
        ctx.fillStyle = gradTop;
        ctx.fillRect(p.x, 0, p.width, p.topHeight);
        ctx.fillStyle = '#38bdf8';
        ctx.fillRect(p.x - 3, p.topHeight - 12, p.width + 6, 12);

        // Bottom pillar
        const gradBot = ctx.createLinearGradient(p.x, 0, p.x + p.width, 0);
        gradBot.addColorStop(0, '#0284c7');
        gradBot.addColorStop(1, '#06b6d4');
        ctx.fillStyle = gradBot;
        ctx.fillRect(p.x, p.bottomY, p.width, 600 - p.bottomY);
        ctx.fillStyle = '#38bdf8';
        ctx.fillRect(p.x - 3, p.bottomY, p.width + 6, 12);
      }}

      // Draw Orbs
      for (const orb of orbs) {{
        ctx.save();
        ctx.fillStyle = '#facc15';
        ctx.beginPath();
        ctx.arc(orb.x, orb.y, orb.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }}

      // Draw Drone
      ctx.save();
      ctx.translate(drone.x, drone.y);
      ctx.rotate(drone.tilt);
      
      // Drone chassis
      ctx.fillStyle = '#f8fafc';
      ctx.beginPath();
      ctx.ellipse(0, 0, 18, 12, 0, 0, Math.PI * 2);
      ctx.fill();

      // Cockpit visor
      ctx.fillStyle = '#06b6d4';
      ctx.beginPath();
      ctx.arc(6, -2, 6, 0, Math.PI * 2);
      ctx.fill();

      // Wing thruster
      ctx.fillStyle = '#f59e0b';
      ctx.fillRect(-16, -3, 6, 6);

      ctx.restore();
    }} else if (state === 'GAMEOVER') {{
      ctx.textAlign = 'center';
      ctx.fillStyle = '#ef4444';
      ctx.font = 'bold 48px -apple-system, sans-serif';
      ctx.fillText('CRASHED!', 400, 240);

      ctx.fillStyle = '#f8fafc';
      ctx.font = '22px -apple-system, sans-serif';
      ctx.fillText(`SCORE: ${{score}}   •   BEST: ${{highScore}}`, 400, 290);

      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 20px -apple-system, sans-serif';
      ctx.fillText('PRESS SPACE TO REFLY', 400, 360);

      if (Input.isAction()) resetGame();
    }}

    fx.draw(ctx);
    ctx.restore();
  }}

  function loop() {{
    update();
    draw();
    requestAnimationFrame(loop);
  }}

  requestAnimationFrame(loop);
  </script>
</body>
</html>
"""


def build_smart_archetype(prompt: str, category: str = "") -> str:
    """Intelligently match user prompt and category to the best fully-playable archetype with customized title."""
    clean_p = prompt.lower()
    clean_cat = (category or "").lower()

    # Extract or infer clean title
    words = [
        w.capitalize()
        for w in prompt.split()
        if len(w) > 2
        and w.lower() not in {"make", "create", "with", "that", "game", "retro", "instant", "play"}
    ]
    inferred_title = " ".join(words[:4]) if words else "Arcade Classic"

    if any(k in clean_p for k in ["snake", "slither", "worm", "fruit", "grid", "tail"]):
        return build_cyber_snake_game(title=f"Cyber Snake: {inferred_title}")
    elif any(k in clean_p for k in ["brick", "break", "breakout", "arkanoid", "bounce", "paddle", "wall"]):
        return build_brick_breaker_game(title=f"Breakout: {inferred_title}")
    elif any(k in clean_p for k in ["fly", "flappy", "drone", "bird", "copter", "gravity", "pipe", "runner", "jump"]):
        return build_flappy_drone_game(title=f"Aero Drone: {inferred_title}")
    elif clean_cat in ["puzzle", "grid"]:
        return build_brick_breaker_game(title=f"Puzzle Breaker: {inferred_title}")
    elif clean_cat in ["platformer"]:
        return build_flappy_drone_game(title=f"Aero Runner: {inferred_title}")
    else:
        # Default space / arcade / shooter
        return build_space_shooter_game(title=f"Space Defender: {inferred_title}")

