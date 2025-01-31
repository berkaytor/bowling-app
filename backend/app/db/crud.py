from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Player, Game, Roll

async def get_players(db: AsyncSession):
    """
    Retrieve all players from the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        list: A list of Player objects.
    """
    result = await db.execute(select(Player))
    return result.scalars().all()

async def create_player(db: AsyncSession, name: str):
    """
    Create a new player in the database.

    Args:
        db (AsyncSession): The database session.
        name (str): The name of the player.

    Returns:
        Player: The newly created Player object.
    """
    new_player = Player(name=name)
    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)
    return new_player

async def create_game(db: AsyncSession, player_id: int):
    """
    Create a new game for a player in the database.

    Args:
        db (AsyncSession): The database session.
        player_id (int): The ID of the player.

    Returns:
        Game: The newly created Game object.
    """
    game = Game(player_id=player_id)
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game

async def add_roll_to_game(db: AsyncSession, game_id: int, pins: int):
    """
    Add a roll to a game in the database.

    Args:
        db (AsyncSession): The database session.
        game_id (int): The ID of the game.
        pins (int): The number of pins knocked down in the roll.

    Returns:
        Game: The updated Game object.
    """
    result = await db.execute(select(Game).filter(Game.id == game_id))
    game = result.scalars().first()
    if not game:
        raise ValueError("Game not found")

    # Create a new roll and add it to the game
    new_roll = Roll(game_id=game_id, pins=pins)
    db.add(new_roll)
    await db.commit()
    await db.refresh(new_roll)

    return game

async def get_game_score(db: AsyncSession, game_id: int):
    """
    Calculate the score of a game.

    Args:
        db (AsyncSession): The database session.
        game_id (int): The ID of the game.

    Returns:
        int: The total score of the game.
    """
    result = await db.execute(select(Game).filter(Game.id == game_id))
    game = result.scalars().first()
    if not game:
        raise ValueError("Game not found")

    rolls = await db.execute(select(Roll).filter(Roll.game_id == game_id).order_by(Roll.id))
    rolls = rolls.scalars().all()

    score = 0
    roll_index = 0
    for frame in range(10):
        if roll_index >= len(rolls):
            break

        if rolls[roll_index].pins == 10:  # Strike
            if roll_index + 2 < len(rolls):
                score += 10 + rolls[roll_index + 1].pins + rolls[roll_index + 2].pins
            roll_index += 1
        elif roll_index + 1 < len(rolls) and rolls[roll_index].pins + rolls[roll_index + 1].pins == 10:  # Spare
            if roll_index + 2 < len(rolls):
                score += 10 + rolls[roll_index + 2].pins
            roll_index += 2
        else:  # Normal frame
            if roll_index + 1 < len(rolls):
                score += rolls[roll_index].pins + rolls[roll_index + 1].pins
            roll_index += 2

    return score

async def get_game_summary(db: AsyncSession, game_id: int):
    """
    Get a summary of a game, including the score and frame details.

    Args:
        db (AsyncSession): The database session.
        game_id (int): The ID of the game.

    Returns:
        dict: A dictionary containing the game summary.
    """
    result = await db.execute(select(Game).filter(Game.id == game_id))
    game = result.scalars().first()
    if not game:
        raise ValueError("Game not found")

    rolls = await db.execute(select(Roll).filter(Roll.game_id == game_id).order_by(Roll.id))
    rolls = rolls.scalars().all()

    score = await get_game_score(db, game_id)
    frames = []
    roll_index = 0
    for frame in range(10):
        if roll_index >= len(rolls):
            break

        if rolls[roll_index].pins == 10:  # Strike
            frames.append({"frame": frame + 1, "rolls": ["X"], "score": score})
            roll_index += 1
        elif roll_index + 1 < len(rolls) and rolls[roll_index].pins + rolls[roll_index + 1].pins == 10:  # Spare
            frames.append({"frame": frame + 1, "rolls": [rolls[roll_index].pins, "/"], "score": score})
            roll_index += 2
        else:  # Normal frame
            if roll_index + 1 < len(rolls):
                frames.append({"frame": frame + 1, "rolls": [rolls[roll_index].pins, rolls[roll_index + 1].pins], "score": score})
            roll_index += 2

    return {
        "game_id": game.id,
        "player_id": game.player_id,
        "total_score": score,
        "frames": frames,
        "rolls": [roll.pins for roll in rolls]
    }