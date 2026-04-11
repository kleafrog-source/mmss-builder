"""
Типы игр и уровни сложности MMSS Game
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class EmotionalTrigger:
    trigger: str
    function: str
    access_type: str


class GameType(Enum):
    """Типы игр MMSS"""
    PFR_PUZZLE = "pfr_puzzle"  # Головоломка фрактальной пересборки
    TEMPORAL_NAVIGATOR = "temporal_navigator"  # Темпоральная навигация
    CONTEXT_WEAVER = "context_weaver"  # Плетение контекста
    MMSS_MASTER = "mmss_master"  # Комплексная игра


class GameDifficulty(Enum):
    """Уровни сложности"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class GameState:
    """Состояние игры"""
    def __init__(self):
        self.score: int = 0
        self.level: int = 1
        self.lives: int = 3
        self.eta_r: float = 0.0
        self.v_value: float = 0.0
        self.moves: int = 0
        self.completed_challenges: List[str] = []
        self.active_components: Dict[str, bool] = {
            'PFR': False,
            'FRP': False,
            'A_MMSS': False
        }















