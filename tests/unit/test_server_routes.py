"""Unit tests for FastAPI dashboard and REST endpoints."""

from starlette.testclient import TestClient
from eightgen.server.app import create_app


def test_dashboard_and_archetype_routes():
    app = create_app()
    client = TestClient(app)

    # 1. Dashboard View
    res = client.get("/")
    assert res.status_code == 200
    assert "8Gen Studio" in res.text
    assert "Universal SaaS Design" in res.text
    assert "Studio Workbench" in res.text

    # 2. Archetype route
    res = client.get("/api/games/archetype/shooter")
    assert res.status_code == 200
    assert "Neon Space Defender" in res.text

    res = client.get("/api/games/archetype/snake")
    assert res.status_code == 200
    assert "Cyber Snake" in res.text

    res = client.get("/api/games/archetype/brick")
    assert res.status_code == 200
    assert "Quantum Breakout" in res.text

    res = client.get("/api/games/archetype/drone")
    assert res.status_code == 200
    assert "Aero Drone Odyssey" in res.text

    # 3. List games API
    res = client.get("/api/games")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 4. Instant Generate API
    res = client.post(
        "/api/generate",
        json={"prompt": "Retro Space Invaders", "category": "shooter", "instant": True},
    )
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert "title" in data
    game_id = data["id"]

    # 5. Play game endpoint
    play_res = client.get(f"/api/games/{game_id}/play")
    assert play_res.status_code == 200
    assert "<!DOCTYPE html>" in play_res.text
