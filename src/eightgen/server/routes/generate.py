"""Generation API routes."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from eightgen.config.loader import get_settings
from eightgen.core.agent import Agent

router = APIRouter(prefix="/api/generate", tags=["generate"])


def get_agent() -> Agent:
    return Agent(get_settings())


class GenerateRequest(BaseModel):
    prompt: str
    category: Optional[str] = None
    model: Optional[str] = None
    instant: bool = False


@router.post("")
async def generate_game(payload: GenerateRequest, agent: Agent = Depends(get_agent)):
    """Generate a new game via REST API."""
    try:
        if payload.model:
            agent.provider.model = payload.model
        game = await agent.create_game(
            prompt=payload.prompt,
            category=payload.category,
            auto_open=False,
            instant=payload.instant,
        )
        return game.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
