# 🎮 8Gen — Beginner's Quickstart Guide

Welcome! **8Gen** is an AI agent that creates playable games and game art on your computer in seconds. You don't need any coding experience!

---

## ⚡ The Easiest Way to Start (One Command)

Just run:
```bash
./start.sh
```

---

## 🎨 AI Image & Game Asset Studio (Gemini Image Gen)

8Gen now includes a built-in **AI Game Asset Generator** that can create:
- **16-bit Pixel Art Sprites** (characters, spaceships, monsters, powerups)
- **Game Background Scenes** (cyberpunk cities, deep space nebulas, dungeons)
- **Retro Arcade Graphics & Icons**

### Generate Images from Command Line
```bash
# Generate a pixel art starfighter sprite
8gen image "neon starfighter spaceship sprite" --style pixel-art

# Generate a retro game background
8gen image "cyberpunk city skyline with neon billboards" --style scifi-background

# Generate a game item icon
8gen image "golden pixel coin powerup with glowing aura"
```
The generated PNG is automatically saved to `games/assets/` and opened in your image viewer!

### Generate Images from Web Studio
Run:
```bash
8gen serve
```
Open **[http://localhost:8000](http://localhost:8000)** and scroll to the **🎨 AI Sprite & Asset Generator** section:
1. Type a description (e.g. *"glowing retro laser cannon"*).
2. Click **Generate Image**.
3. Click **Copy Data URL** to paste directly into your HTML game, or **Download PNG**!

---

## ⚡ How to Connect Gemini Web-to-API or Google Gemini

8Gen supports both:
1. **Gemini Web-to-API (from your `oorja` or `gemini-web2api` setup)**:
   - Connects automatically to `http://localhost:4981/openai/v1` or `http://localhost:8081/v1`
   - Gives access to Gemini Web models + Text-to-Image / Imagen models!
2. **Google Gemini API**:
   - Set key with `8gen config set-key YOUR_KEY` or in the web dashboard.
   - Ultra-fast 2-second game synthesis!

---

## 🕹️ 3 Fun Ways to Play & Create

### Option 1: The Interactive Wizard
```bash
8gen
```
Select a starter game (Space Invaders, Snake, Brick Breaker, Pong), and watch it create and launch the game in your browser!

### Option 2: The Visual Web Studio
```bash
8gen serve
```
Open [http://localhost:8000](http://localhost:8000) to browse your gallery, play games in fullscreen, generate new games with live streaming, and generate game art assets.

### Option 3: Instant One-Liner in Terminal
```bash
8gen generate "retro space shooter with laser cannons"
```

---

## 🪄 How to Improve / Change a Game ("Refining")

```bash
8gen refine last "make the ball faster and add explosion sound effects"
```
Or in the Web Studio, click the **⚡ Refine** button on any game card!
