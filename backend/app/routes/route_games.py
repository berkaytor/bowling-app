from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from sqlalchemy.future import select
from app.db.crud import create_game, create_player, add_roll_to_game, get_game_score, get_game_summary
from app.db.models import Player  # Import the Player model
from pydantic import BaseModel
from typing import List
import openai
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

class Frame(BaseModel):
    rolls: List[int]  # Pins knocked down in each roll (max 3 for the 10th frame)

class Game(BaseModel):
    frames: List[Frame]  # List of 10 frames
    
async def get_player_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Player).filter(Player.name == name))
    return result.scalars().first()

class PlayerInput(BaseModel):
    name: str

class RollInput(BaseModel):
    pins: int

@router.post("")
async def add_player(player: PlayerInput, db: AsyncSession = Depends(get_db)):
    existing_player = await get_player_by_name(db, player.name)
    if existing_player:
        new_game = await create_game(db, existing_player.id)
        return {
            "player": existing_player,
            "game": new_game
        }
    else:
        print("Creating new player")
        new_player = await create_player(db, player.name)
        new_game = await create_game(db, new_player.id)
        return {
            "player": new_player,
            "game": new_game
        }

@router.post("/{game_id}/rolls")
async def add_roll(game_id: int, roll: RollInput, db: AsyncSession = Depends(get_db)):
    print(game_id, roll.pins)
    try:
        game = await add_roll_to_game(db, game_id, roll.pins)
        return game
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{game_id}/score")
async def get_game_score_route(game_id: int, db: AsyncSession = Depends(get_db)):
    try:
        score = await get_game_score(db, game_id)
        return {"score": score}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

SYSTEM_PROMPT = (
    "You are a bowling game assistant. Your task is to analyze a single-player bowling game's roll record and generate a concise, informative summary. Include the player's total score, key achievements (e.g., strikes, spares, turkeys), and notable moments (e.g., consecutive strikes or a perfect game). Maintain a clear and engaging tone suitable for a general audience. If applicable, mention any unusual patterns or significant turning points in the game. Anwer in 2 or 3 sentences."
)

@router.get("/{game_id}/summary")
async def get_game_summary_route(game_id: int, db: AsyncSession = Depends(get_db)):
    try:
        summary = await get_game_summary(db, game_id)
        # logger.info(f"{' '.join(map(str, summary['frames']))}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        # Generate response using OpenAI's API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{' '.join(map(str, summary['frames']))}"}
            ],
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.7
        )
        
        return {"response": response.choices[0].message['content'].strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))