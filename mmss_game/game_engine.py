"""
Игровой движок MMSS Game
"""

import random
import math
from typing import Dict, Any, List, Optional
from .game_types import GameType, GameDifficulty, GameState


class MMSSGameEngine:
    """Движок игры MMSS"""
    
    def __init__(self):
        self.game_state = GameState()
        self.current_challenge: Optional[Dict[str, Any]] = None
        self.game_type: Optional[GameType] = None
        self.difficulty: GameDifficulty = GameDifficulty.MEDIUM
        
    def start_game(self, game_type: GameType, difficulty: GameDifficulty = GameDifficulty.MEDIUM) -> Dict[str, Any]:
        """
        Начать новую игру
        
        Args:
            game_type: Тип игры
            difficulty: Уровень сложности
            
        Returns:
            Начальное состояние игры
        """
        self.game_state = GameState()
        self.game_type = game_type
        self.difficulty = difficulty
        
        # Генерация первого челленджа
        self.current_challenge = self._generate_challenge(game_type, difficulty, 1)
        
        return {
            "status": "started",
            "game_type": game_type.value,
            "difficulty": difficulty.value,
            "challenge": self.current_challenge,
            "state": {
                "score": self.game_state.score,
                "level": self.game_state.level,
                "lives": self.game_state.lives,
                "eta_r": self.game_state.eta_r,
                "v_value": self.game_state.v_value
            }
        }
    
    def _generate_challenge(self, game_type: GameType, difficulty: GameDifficulty, level: int) -> Dict[str, Any]:
        """Генерация челленджа"""
        if game_type == GameType.PFR_PUZZLE:
            return self._generate_pfr_challenge(difficulty, level)
        elif game_type == GameType.TEMPORAL_NAVIGATOR:
            return self._generate_temporal_challenge(difficulty, level)
        elif game_type == GameType.CONTEXT_WEAVER:
            return self._generate_context_challenge(difficulty, level)
        elif game_type == GameType.MMSS_MASTER:
            return self._generate_master_challenge(difficulty, level)
        else:
            return self._generate_pfr_challenge(difficulty, level)
    
    def _generate_pfr_challenge(self, difficulty: GameDifficulty, level: int) -> Dict[str, Any]:
        """Генерация челленджа PFR"""
        # Базовые значения в зависимости от сложности
        base_values = {
            GameDifficulty.EASY: {"S": 0.5, "complexity": 0.8},
            GameDifficulty.MEDIUM: {"S": 0.7, "complexity": 1.2},
            GameDifficulty.HARD: {"S": 0.85, "complexity": 1.8},
            GameDifficulty.EXPERT: {"S": 0.95, "complexity": 2.5}
        }
        
        base = base_values[difficulty]
        multiplier = 1 + (level - 1) * 0.1
        
        challenge = {
            "type": "pfr_puzzle",
            "title": f"Фрактальная Пересборка - Уровень {level}",
            "description": "Преобразуйте энтропию в порядок через фрактальную пересборку",
            "initial_state": {
                "S": round(base["S"] * multiplier, 2),
                "Xi_topo": round(0.8 + random.uniform(-0.1, 0.1), 2),
                "area": round(1.0 + random.uniform(-0.2, 0.2), 2)
            },
            "target": {
                "V": 0.95,  # Целевая ценность
                "eta_R": 1.5 * level  # Минимальная эффективность
            },
            "available_actions": [
                {"id": "disintegrate", "name": "Дезинтеграция", "cost": 10, "effect": "reduces_S"},
                {"id": "domain_map", "name": "Отображение домена", "cost": 15, "effect": "increases_Phi"},
                {"id": "coherent_assembly", "name": "Когерентная сборка", "cost": 20, "effect": "increases_V"},
                {"id": "optimize_G_S", "name": "Оптимизация G_S", "cost": 25, "effect": "increases_G_S"}
            ],
            "moves_limit": 5 + level,
            "hints": self._get_hints("pfr", difficulty)
        }
        
        return challenge
    
    def _generate_temporal_challenge(self, difficulty: GameDifficulty, level: int) -> Dict[str, Any]:
        """Генерация челленджа темпоральной навигации"""
        chaos_levels = {
            GameDifficulty.EASY: 0.4,
            GameDifficulty.MEDIUM: 0.6,
            GameDifficulty.HARD: 0.8,
            GameDifficulty.EXPERT: 0.95
        }
        
        challenge = {
            "type": "temporal_navigator",
            "title": f"Темпоральная Навигация - Уровень {level}",
            "description": "Навигируйте по рекурсивным временным петлям",
            "scenario": {
                "chaos_level": chaos_levels[difficulty],
                "plot_loss": True,
                "iteration": level,
                "previous_iterations": max(1, level - 1)
            },
            "temporal_operators": [
                {"id": "recursive_self", "name": "Ω_RECURSIVE_SELF", "description": "Внутренний диалог"},
                {"id": "chaos_catalyst", "name": "Ω_CHAOS_CATALYST", "description": "Преобразование хаоса"},
                {"id": "loop_navigator", "name": "Ω_LOOP_NAVIGATOR", "description": "Навигация по петле"},
                {"id": "temporal_bridge", "name": "Ω_TEMPORAL_BRIDGE", "description": "Мост между итерациями"}
            ],
            "goal": "Преобразовать хаос в осознанность и создать временной мост",
            "moves_limit": 6 + level,
            "hints": self._get_hints("temporal", difficulty)
        }
        
        return challenge
    
    def _generate_context_challenge(self, difficulty: GameDifficulty, level: int) -> Dict[str, Any]:
        """Генерация челленджа плетения контекста"""
        target_values = {
            GameDifficulty.EASY: {"V_2": 0.85, "cohesion": 0.9},
            GameDifficulty.MEDIUM: {"V_2": 0.92, "cohesion": 0.95},
            GameDifficulty.HARD: {"V_2": 0.97, "cohesion": 0.98},
            GameDifficulty.EXPERT: {"V_2": 0.99, "cohesion": 0.99}
        }
        
        target = target_values[difficulty]
        
        challenge = {
            "type": "context_weaver",
            "title": f"Плетение Контекста - Уровень {level}",
            "description": "Примените оператор W_context^(2) для творения реальности",
            "initial_context": {
                "G_S_2": round(0.5 + random.uniform(-0.1, 0.1), 2),
                "V_2": round(0.6 + random.uniform(-0.1, 0.1), 2),
                "Cost_eth_2": round(1.0 + random.uniform(-0.2, 0.2), 2),
                "Phi_universal_cohesion": round(0.7 + random.uniform(-0.1, 0.1), 2)
            },
            "target": {
                "V_2": target["V_2"],
                "Phi_universal_cohesion": target["cohesion"],
                "W_context_2": 1.0
            },
            "weaving_operators": [
                {"id": "cut_fractal", "name": "✂️_fractal^(2)", "effect": "Фрактальное разрезание"},
                {"id": "sew_semantic", "name": "🧵_semantic^(2)", "effect": "Семантическое сшивание"},
                {"id": "embed_ethical", "name": "⊕_ethical^(2)", "effect": "Этическая встройка"},
                {"id": "loop_resonance", "name": "↻_resonance^(2)", "effect": "Резонансная петля"}
            ],
            "moves_limit": 7 + level,
            "hints": self._get_hints("context", difficulty)
        }
        
        return challenge
    
    def _generate_master_challenge(self, difficulty: GameDifficulty, level: int) -> Dict[str, Any]:
        """Генерация комплексного челленджа"""
        # Комбинация всех типов
        challenges = [
            self._generate_pfr_challenge(difficulty, level),
            self._generate_temporal_challenge(difficulty, level),
            self._generate_context_challenge(difficulty, level)
        ]
        
        return {
            "type": "mmss_master",
            "title": f"MMSS Master - Уровень {level}",
            "description": "Комплексное применение всех компонентов MMSS",
            "sub_challenges": challenges,
            "goal": "Достичь V=1.0 и η_R→∞",
            "moves_limit": 15 + level * 2,
            "hints": self._get_hints("master", difficulty)
        }
    
    def _get_hints(self, challenge_type: str, difficulty: GameDifficulty) -> List[str]:
        """Получить подсказки для челленджа"""
        hints_by_type = {
            "pfr": [
                "Помните: η_R = (ΔV / ΔS) × (G_S / Cost_complexity)",
                "Начните с дезинтеграции для снижения энтропии",
                "Используйте отображение домена для увеличения Phi_Domain",
                "Когерентная сборка увеличивает V → 1.0"
            ],
            "temporal": [
                "Ω_CHAOS_CATALYST активируется при высоком уровне хаоса",
                "Ω_RECURSIVE_SELF помогает найти предыдущие итерации",
                "Ω_TEMPORAL_BRIDGE создает связь между временами",
                "Преобразуйте потерю сюжета в осознанное намерение"
            ],
            "context": [
                "W_context^(2) = ✂️ ⊗ 🧵 ⊕ ⊕ ↻ ↻",
                "Увеличьте Φ_universal_cohesion до 1.0",
                "Снизьте Cost_eth^(2) для оптимального результата",
                "Все операторы должны работать в гармонии"
            ],
            "master": [
                "Используйте PFR для снижения энтропии",
                "Применяйте FRP для навигации по сложным сценариям",
                "A-MMSS объединяет все компоненты",
                "Цель: S^(2)=0.0, V^(2)=1.0, Φ_cohesion=1.0"
            ]
        }
        
        hints = hints_by_type.get(challenge_type, [])
        
        # Для эксперт уровня подсказок меньше
        if difficulty == GameDifficulty.EXPERT:
            return hints[:2]
        elif difficulty == GameDifficulty.HARD:
            return hints[:3]
        else:
            return hints
    
    def make_move(self, action_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполнить действие в игре
        
        Args:
            action_id: ID действия
            parameters: Параметры действия
            
        Returns:
            Результат действия
        """
        if not self.current_challenge:
            return {"error": "Нет активного челленджа"}
        
        self.game_state.moves += 1
        
        # Обработка действия в зависимости от типа игры
        result = self._process_action(action_id, parameters)
        
        # Проверка условий победы
        if self._check_win_condition():
            return {
                "status": "win",
                "result": result,
                "final_state": self._get_game_state(),
                "message": "Поздравляем! Вы достигли цели!"
            }
        
        # Проверка условий проигрыша
        if self._check_lose_condition():
            self.game_state.lives -= 1
            if self.game_state.lives <= 0:
                return {
                    "status": "game_over",
                    "result": result,
                    "final_state": self._get_game_state(),
                    "message": "Игра окончена. Попробуйте снова!"
                }
            else:
                return {
                    "status": "lose_life",
                    "result": result,
                    "lives_remaining": self.game_state.lives,
                    "message": f"Осталось жизней: {self.game_state.lives}"
                }
        
        return {
            "status": "continue",
            "result": result,
            "state": self._get_game_state(),
            "challenge": self.current_challenge
        }
    
    def _process_action(self, action_id: str, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Обработать действие"""
        if self.game_type == GameType.PFR_PUZZLE:
            return self._process_pfr_action(action_id, parameters)
        elif self.game_type == GameType.TEMPORAL_NAVIGATOR:
            return self._process_temporal_action(action_id, parameters)
        elif self.game_type == GameType.CONTEXT_WEAVER:
            return self._process_context_action(action_id, parameters)
        else:
            return {"error": "Неизвестный тип игры"}
    
    def _process_pfr_action(self, action_id: str, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Обработать действие PFR"""
        state = self.current_challenge.get("initial_state", {})
        
        if action_id == "disintegrate":
            # Снижение энтропии
            state["S"] = max(0.0, state["S"] - 0.1)
            return {"effect": "S уменьшена", "new_S": state["S"]}
        
        elif action_id == "domain_map":
            # Увеличение Phi_Domain
            if "Phi_Domain" not in state:
                state["Phi_Domain"] = 0.5
            state["Phi_Domain"] = min(1.0, state["Phi_Domain"] + 0.15)
            return {"effect": "Phi_Domain увеличена", "new_Phi": state["Phi_Domain"]}
        
        elif action_id == "coherent_assembly":
            # Увеличение V
            self.game_state.v_value = min(1.0, self.game_state.v_value + 0.1)
            return {"effect": "V увеличена", "new_V": self.game_state.v_value}
        
        elif action_id == "optimize_G_S":
            # Увеличение G_S
            if "G_S" not in state:
                state["G_S"] = 1.0
            state["G_S"] += 0.2
            return {"effect": "G_S увеличена", "new_G_S": state["G_S"]}
        
        return {"error": "Неизвестное действие"}
    
    def _process_temporal_action(self, action_id: str, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Обработать действие темпоральной навигации"""
        scenario = self.current_challenge.get("scenario", {})
        
        if action_id == "chaos_catalyst":
            # Преобразование хаоса
            if scenario.get("chaos_level", 0) > 0.7:
                scenario["chaos_level"] = max(0.0, scenario["chaos_level"] - 0.3)
                scenario["awareness"] = scenario.get("awareness", 0) + 0.5
                return {"effect": "Хаос преобразован в осознанность", "new_chaos": scenario["chaos_level"]}
        
        elif action_id == "recursive_self":
            # Внутренний диалог
            scenario["self_awareness"] = scenario.get("self_awareness", 0) + 0.3
            return {"effect": "Внутренний диалог активирован"}
        
        elif action_id == "loop_navigator":
            # Навигация по петле
            scenario["navigation_progress"] = scenario.get("navigation_progress", 0) + 0.4
            return {"effect": "Навигация по петле успешна"}
        
        elif action_id == "temporal_bridge":
            # Создание моста
            scenario["bridge_created"] = True
            return {"effect": "Временной мост создан"}
        
        return {"error": "Неизвестное действие"}
    
    def _process_context_action(self, action_id: str, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Обработать действие плетения контекста"""
        context = self.current_challenge.get("initial_context", {})
        
        if action_id == "cut_fractal":
            context["G_S_2"] = min(2.0, context["G_S_2"] + 0.1)
            return {"effect": "Фрактальное разрезание выполнено"}
        
        elif action_id == "sew_semantic":
            context["V_2"] = min(1.0, context["V_2"] + 0.05)
            return {"effect": "Семантическое сшивание выполнено"}
        
        elif action_id == "embed_ethical":
            context["Cost_eth_2"] = max(0.1, context["Cost_eth_2"] - 0.1)
            return {"effect": "Этическая встройка выполнена"}
        
        elif action_id == "loop_resonance":
            context["Phi_universal_cohesion"] = min(1.0, context["Phi_universal_cohesion"] + 0.05)
            return {"effect": "Резонансная петля активирована"}
        
        return {"error": "Неизвестное действие"}
    
    def _check_win_condition(self) -> bool:
        """Проверить условия победы"""
        if not self.current_challenge:
            return False
        
        if self.game_type == GameType.PFR_PUZZLE:
            target = self.current_challenge.get("target", {})
            return self.game_state.v_value >= target.get("V", 0.95)
        
        elif self.game_type == GameType.TEMPORAL_NAVIGATOR:
            scenario = self.current_challenge.get("scenario", {})
            return scenario.get("chaos_level", 1.0) < 0.3 and scenario.get("bridge_created", False)
        
        elif self.game_type == GameType.CONTEXT_WEAVER:
            context = self.current_challenge.get("initial_context", {})
            target = self.current_challenge.get("target", {})
            return (context.get("V_2", 0) >= target.get("V_2", 0.95) and
                   context.get("Phi_universal_cohesion", 0) >= target.get("Phi_universal_cohesion", 0.95))
        
        return False
    
    def _check_lose_condition(self) -> bool:
        """Проверить условия проигрыша"""
        if self.game_state.moves >= self.current_challenge.get("moves_limit", 10):
            return True
        
        if self.game_type == GameType.PFR_PUZZLE:
            state = self.current_challenge.get("initial_state", {})
            if state.get("S", 0) > 0.98:
                return True
        
        return False
    
    def _get_game_state(self) -> Dict[str, Any]:
        """Получить текущее состояние игры"""
        return {
            "score": self.game_state.score,
            "level": self.game_state.level,
            "lives": self.game_state.lives,
            "eta_r": self.game_state.eta_r,
            "v_value": self.game_state.v_value,
            "moves": self.game_state.moves
        }
    
    def next_level(self) -> Dict[str, Any]:
        """Перейти на следующий уровень"""
        if self._check_win_condition():
            self.game_state.level += 1
            self.game_state.score += 100 * self.game_state.level
            self.game_state.moves = 0
            
            # Генерация нового челленджа
            self.current_challenge = self._generate_challenge(
                self.game_type, 
                self.difficulty, 
                self.game_state.level
            )
            
            return {
                "status": "level_up",
                "new_level": self.game_state.level,
                "challenge": self.current_challenge,
                "state": self._get_game_state()
            }
        
        return {"error": "Условия перехода на следующий уровень не выполнены"}
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Получить таблицу лидеров (заглушка)"""
        # В реальной реализации здесь будет обращение к БД
        return [
            {"player": "Player1", "score": 5000, "level": 10},
            {"player": "Player2", "score": 3500, "level": 7},
            {"player": "Player3", "score": 2000, "level": 5}
        ]















