from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Base class for all models
Base = declarative_base()

class Player(Base):
    """
    Represents a player in the database.

    Attributes:
        id (int): The unique identifier of the player.
        name (str): The name of the player.
    """
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Game(Base):
    """
    Represents a game in the database.

    Attributes:
        id (int): The unique identifier of the game.
        player_id (int): The ID of the player who played the game.
        player (Player): The player who played the game.
        total_score (int): The total score of the game.
        rolls (list): The list of rolls in the game.
    """
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    player = relationship("Player")
    total_score = Column(Integer, default=0)
    rolls = relationship("Roll", back_populates="game")

class Roll(Base):
    """
    Represents a roll in a game in the database.

    Attributes:
        id (int): The unique identifier of the roll.
        game_id (int): The ID of the game to which the roll belongs.
        pins (int): The number of pins knocked down in the roll.
        game (Game): The game to which the roll belongs.
    """
    __tablename__ = "rolls"
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    pins = Column(Integer)
    game = relationship("Game", back_populates="rolls")