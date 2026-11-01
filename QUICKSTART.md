# 🎮 8Gen — Beginner's Quickstart Guide

Welcome! **8Gen** is an AI agent that creates playable games on your computer. You don't need any coding experience—just describe an idea, and your local AI will code and open a playable game in your web browser.

---

## ⚡ The Easiest Way to Start (One Command)

Just run:
```bash
./start.sh
```

That's it! It will automatically check your setup and open an interactive game creator where you can pick a game or type your own idea.

---

## 🕹️ 3 Fun Ways to Use 8Gen

### Option 1: The Interactive Wizard (Recommended for Beginners)
Run in your terminal:
```bash
8gen
```
You'll see a friendly menu:
```
What would you like to do?
1) 🎮 Create a new game
2) 🌐 Open the Web Studio
3) 🕹️ Play existing games
4) 🔧 Check Ollama setup
```
Pick **1**, select a starter game (like Space Invaders or Snake), and watch it create and launch the game in your browser!

---

### Option 2: The Visual Web Studio (In Your Browser)
If you prefer clicking buttons in your web browser:
```bash
8gen serve
```
Open **[http://localhost:8000](http://localhost:8000)**:
- Click on any starter game card (🚀 Space Invaders, 🐍 Snake, 🧱 Brick Breaker, etc.)
- Click **Generate Game**
- Play directly in your browser with full-screen support!

---

### Option 3: Instant One-Liner in Terminal
If you just want to generate a game immediately from the command line:
```bash
8gen generate "retro space shooter with laser cannons"
```
Your default web browser will automatically open with the playable game as soon as it's ready.

---

## 🪄 How to Improve / Change a Game ("Refining")

Did you make a game and want to add something? You can ask the AI to change it!

Just run:
```bash
8gen refine last "make the ball faster and add explosion sound effects"
```
Or in the Web Studio:
- Click the **⚡ Refine** button on any game card
- Type what you want to change (e.g. "add power-ups", "make enemies shoot back")
- The AI will update your game!

---

## 📋 Common Game Ideas You Can Try

Copy and paste any of these to see what happens:
- `8gen generate "cyberpunk flappy drone flying through electric neon gates with score counter"`
- `8gen generate "brick breaker breakout game with bouncy ball and multicolored destructible bricks"`
- `8gen generate "classic retro snake game with glowing tail and speed bonuses"`
- `8gen generate "match 3 jewel puzzle game with combos and sparkles"`
- `8gen generate "2-player pong game with bouncy physics and score counter to 5"`

---

## ❓ Frequently Asked Questions & Troubleshooting

### Q: What controls do the games use?
Most arcade games use:
- **Arrow keys** or **W / A / S / D** to move
- **Spacebar** to shoot or jump
- **Mouse / Touch** to aim, click, or drag

### Q: Do I need internet access?
No! Once Ollama and your model are downloaded, 8Gen runs **100% offline** on your computer.

### Q: "Cannot reach Ollama" error?
Make sure the free [Ollama app](https://ollama.com) is installed and running:
- Open the **Ollama** application on your Mac/PC, or
- Run `ollama serve` in a terminal window.

To check your connection anytime:
```bash
8gen config check
```
