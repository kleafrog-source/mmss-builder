"""
MMSS Game Module - Интерактивная игра на основе принципов MMSS
"""

from .game_engine import MMSSGameEngine
from .game_types import GameType, GameDifficulty

__all__ = [
    'MMSSGameEngine',
    'GameType',
    'GameDifficulty'
]

__version__ = "1.0.0"





