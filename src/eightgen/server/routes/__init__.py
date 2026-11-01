"""Server route blueprints."""

from eightgen.server.routes.games import router as games_router
from eightgen.server.routes.generate import router as generate_router
from eightgen.server.routes.ws import router as ws_router

__all__ = ["games_router", "generate_router", "ws_router"]
