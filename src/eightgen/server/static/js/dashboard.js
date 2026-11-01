// 8Gen Dashboard UI logic

let activeGameId = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchGames();
  setupEventListeners();
});

function setupEventListeners() {
  const generateBtn = document.getElementById("generate-btn");
  const promptInput = document.getElementById("prompt-input");
  const modalClose = document.getElementById("modal-close");
  const fullscreenBtn = document.getElementById("fullscreen-btn");
  const refineSubmit = document.getElementById("refine-submit");

  generateBtn.addEventListener("click", handleGenerate);
  promptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  });

  if (modalClose) {
    modalClose.addEventListener("click", closeModal);
  }

  if (fullscreenBtn) {
    fullscreenBtn.addEventListener("click", () => {
      const iframe = document.getElementById("game-frame");
      if (iframe.requestFullscreen) {
        iframe.requestFullscreen();
      }
    });
  }

  if (refineSubmit) {
    refineSubmit.addEventListener("click", handleRefine);
  }

  // Chips click handler
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      const category = chip.getAttribute("data-category");
      if (prompt) promptInput.value = prompt;
      if (category) {
        const select = document.getElementById("category-select");
        if (select) select.value = category;
      }
      promptInput.focus();
    });
  });
}

async function fetchGames() {
  const grid = document.getElementById("games-grid");
  try {
    const res = await fetch("/api/games");
    const games = await res.json();
    renderGallery(games);
  } catch (err) {
    console.error("Failed to fetch games:", err);
    grid.innerHTML = `<div class="empty-state">Unable to load library. Is server running?</div>`;
  }
}

function renderGallery(games) {
  const grid = document.getElementById("games-grid");
  const countEl = document.getElementById("game-count");
  if (countEl) countEl.innerText = `${games.length} Games`;

  if (!games || games.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <h3>No games generated yet!</h3>
        <p>Pick an idea above or type your own prompt to create your first game.</p>
      </div>`;
    return;
  }

  grid.innerHTML = games.map((g) => {
    const icon = getCategoryIcon(g.category);
    return `
      <div class="game-card" data-id="${g.id}">
        <div class="game-card-preview">
          <span>${icon}</span>
        </div>
        <div class="game-card-body">
          <div class="game-card-title">${escapeHtml(g.title)}</div>
          <div class="game-card-prompt">${escapeHtml(g.description || g.title)}</div>
          <div class="game-card-meta">
            <span class="version-badge">v${g.current_version}</span>
            <span>${new Date(g.updated_at).toLocaleDateString()}</span>
          </div>
          <div class="card-actions">
            <button class="btn-card btn-play" onclick="openGame('${g.id}', '${escapeHtml(g.title)}')">
              ▶ Play
            </button>
            <button class="btn-card btn-refine" onclick="promptRefine('${g.id}', '${escapeHtml(g.title)}')">
              ⚡ Refine
            </button>
            <a href="/api/games/${g.id}/download" class="btn-icon" title="Export HTML" download>
              ⬇
            </a>
            <button class="btn-icon delete" onclick="deleteGame('${g.id}')" title="Delete">
              ✕
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function getCategoryIcon(cat) {
  const c = (cat || "").toLowerCase();
  if (c.includes("shooter") || c.includes("space")) return "🚀";
  if (c.includes("puzzle") || c.includes("logic")) return "🧩";
  if (c.includes("platform")) return "🏃";
  if (c.includes("racing")) return "🏎️";
  if (c.includes("card") || c.includes("board")) return "🎲";
  return "🎮";
}

async function handleGenerate() {
  const promptInput = document.getElementById("prompt-input");
  const categorySelect = document.getElementById("category-select");
  const generateBtn = document.getElementById("generate-btn");
  const streamPanel = document.getElementById("stream-panel");

  const prompt = promptInput.value.trim();
  if (!prompt) return;

  const category = categorySelect.value;

  generateBtn.disabled = true;
  generateBtn.innerHTML = `<span>Synthesizing...</span>`;
  streamPanel.style.display = "block";
  streamPanel.textContent = "Connecting to Ollama AI engine...\n";

  // Use WebSocket for live token streaming
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/generate`;

  let ws;
  try {
    ws = new WebSocket(wsUrl);
  } catch (e) {
    console.warn("WebSocket not supported, falling back to HTTP");
  }

  if (ws) {
    ws.onopen = () => {
      ws.send(JSON.stringify({ prompt, category }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "start") {
        streamPanel.textContent += `Generating game for: "${prompt}"...\n\n`;
      } else if (data.type === "delta") {
        streamPanel.textContent += data.chunk;
        streamPanel.scrollTop = streamPanel.scrollHeight;
      } else if (data.type === "completed") {
        streamPanel.textContent += "\n\n✔ Game successfully built and validated!";
        generateBtn.disabled = false;
        generateBtn.innerHTML = `<span>Generate Game</span>`;
        promptInput.value = "";
        fetchGames();
        if (data.game) {
          openGame(data.game.id, data.game.title);
        }
      } else if (data.type === "error") {
        streamPanel.textContent += `\n\n✖ Error: ${data.message}`;
        generateBtn.disabled = false;
        generateBtn.innerHTML = `<span>Generate Game</span>`;
      }
    };

    ws.onerror = async () => {
      // Fallback to REST
      fallbackHttpGenerate(prompt, category);
    };
  } else {
    fallbackHttpGenerate(prompt, category);
  }
}

async function fallbackHttpGenerate(prompt, category) {
  const generateBtn = document.getElementById("generate-btn");
  const streamPanel = document.getElementById("stream-panel");
  try {
    streamPanel.textContent = "Synthesizing game (please wait)...";
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, category }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Generation failed");
    }
    const game = await res.json();
    streamPanel.textContent = "✔ Game generated!";
    fetchGames();
    openGame(game.id, game.title);
  } catch (err) {
    streamPanel.textContent = `✖ Error: ${err.message}`;
  } finally {
    generateBtn.disabled = false;
    generateBtn.innerHTML = `<span>Generate Game</span>`;
  }
}

function openGame(gameId, title) {
  activeGameId = gameId;
  const modal = document.getElementById("game-modal");
  const modalTitle = document.getElementById("modal-game-title");
  const iframe = document.getElementById("game-frame");

  modalTitle.innerText = title || "Play Game";
  iframe.src = `/api/games/${gameId}/play?t=${Date.now()}`;
  modal.style.display = "flex";
}

function closeModal() {
  const modal = document.getElementById("game-modal");
  const iframe = document.getElementById("game-frame");
  modal.style.display = "none";
  iframe.src = "about:blank";
}

function promptRefine(gameId, title) {
  const instruction = prompt(`Refine game "${title}":\n(e.g., "add sound effects", "make enemies shoot lasers", "add power-ups")`);
  if (!instruction || !instruction.trim()) return;

  const streamPanel = document.getElementById("stream-panel");
  streamPanel.style.display = "block";
  streamPanel.textContent = `Refining "${title}" with instruction: "${instruction}"...\nPlease wait...`;

  fetch(`/api/games/${gameId}/refine`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ instruction }),
  })
    .then((res) => {
      if (!res.ok) throw new Error("Refinement failed");
      return res.json();
    })
    .then((updated) => {
      streamPanel.textContent = `✔ Refinement complete! Game updated to v${updated.current_version}.`;
      fetchGames();
      openGame(updated.id, updated.title);
    })
    .catch((err) => {
      streamPanel.textContent = `✖ Refinement error: ${err.message}`;
    });
}

async function deleteGame(gameId) {
  if (!confirm("Are you sure you want to delete this game?")) return;
  try {
    await fetch(`/api/games/${gameId}`, { method: "DELETE" });
    fetchGames();
  } catch (err) {
    alert("Could not delete game.");
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
