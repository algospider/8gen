"""FastAPI application factory and routes."""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from eightgen.config.loader import get_settings
from eightgen.core.agent import Agent
from eightgen.server.routes.games import router as games_router
from eightgen.server.routes.generate import router as generate_router
from eightgen.server.routes.ws import router as ws_router

SERVER_DIR = Path(__file__).parent
STATIC_DIR = SERVER_DIR / "static"
TEMPLATES_DIR = SERVER_DIR / "templates"


def create_app() -> FastAPI:
    """Instantiate and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="8Gen Arcade Server",
        description="Local AI Game Generator Web Dashboard",
        version="0.1.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static assets
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Templates
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    # Include API Routers
    app.include_router(games_router)
    app.include_router(generate_router)
    app.include_router(ws_router)

    @app.get("/", response_class=HTMLResponse)
    async def dashboard_view(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "model_name": settings.model,
            },
        )

    @app.get("/games/{game_id}", response_class=HTMLResponse)
    async def game_view(request: Request, game_id: str):
        agent = Agent(settings)
        game = agent.get_game(game_id)
        if not game:
            return HTMLResponse("Game not found", status_code=404)
        return templates.TemplateResponse(
            request=request,
            name="game.html",
            context={
                "game": game,
                "model_name": settings.model,
            },
        )

    return app


app = create_app()
