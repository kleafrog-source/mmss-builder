"""
Модуль Практической Фрактальной Пересборки (PFR)
Реализует операторы R_f для максимизации η_R
"""

import json
import math
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PFRMetrics:
    """Метрики эффективности пересборки"""
    eta_R: float = 0.0  # Эффективность пересборки
    V: float = 0.0      # Прикладная ценность
    delta_S: float = 0.0  # Реорганизованная энтропия
    cost_complexity: float = 0.0  # Стоимость сложности
    G_S: float = 1.0    # Семантическая гравитация
    D_f: float = 1.0    # Фрактальная размерность
    Phi_Domain: float = 1.0  # Поле применения


class FractalReassemblyEngine:
    """Движок фрактальной пересборки"""
    
    def __init__(self, package_path: Optional[str] = None):
        self.package_path = package_path or "packages/fractal_reassembly_package.json"
        self.package = self._load_package()
        self.metrics = PFRMetrics()
        self.active_domain: Optional[str] = None
        
    def _load_package(self) -> Dict[str, Any]:
        """Загрузка пакета пересборки"""
        path = Path(self.package_path)
        if not path.exists():
            raise FileNotFoundError(f"Пакет не найден: {self.package_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def activate(self, domain: str) -> Dict[str, Any]:
        """
        Активация движка для указанного домена
        
        Args:
            domain: Поле применения (например, 'Финансовый Анализ')
            
        Returns:
            Статус активации
        """
        self.active_domain = domain
        manifest = self.package['FRACTAL_REASSEMBLY_PACKAGE']['MANIFEST']
        
        return {
            "status": "ACTIVATED",
            "package_id": self.package['FRACTAL_REASSEMBLY_PACKAGE']['package_id'],
            "domain": domain,
            "optimization_goal": manifest['optimization_goal'],
            "target_value": manifest['target_value_state']
        }
    
    def calculate_eta_R(self, delta_V: float, delta_S: float, 
                       G_S: float, cost_complexity: float) -> float:
        """
        PFR_001: Расчет эффективности пересборки
        η_R = (ΔV / ΔS_reorganized) * (G_S / Cost_complexity)
        """
        if delta_S == 0 or cost_complexity == 0:
            return 0.0
        
        eta_R = (delta_V / delta_S) * (G_S / cost_complexity)
        self.metrics.eta_R = eta_R
        return eta_R
    
    def calculate_V_applied(self, C_val: float, Phi_Domain: float,
                           G_S: float, D_f: float, R_T: float) -> float:
        """
        PFR_002: Расчет прикладной ценности
        V = 1 - (C_val ⊗ Phi_Domain) / (G_S * D_f * R_T)
        """
        if G_S == 0 or D_f == 0 or R_T == 0:
            return 0.0
        
        V = 1 - (C_val * Phi_Domain) / (G_S * D_f * R_T)
        V = max(0.0, min(1.0, V))  # Ограничение [0, 1]
        self.metrics.V = V
        return V
    
    def calculate_delta_S_reorganized(self, S_initial: float, S_final: float) -> float:
        """
        PFR_003: Расчет реорганизованной энтропии
        ΔS_reorganized = S_initial - S_final
        """
        delta_S = S_initial - S_final
        self.metrics.delta_S = delta_S
        return delta_S
    
    def calculate_cost_complexity(self, Xi_topo: float, weights: list, D_f: float) -> float:
        """
        PFR_004: Расчет стоимости сложности
        Cost_complexity = Σ(Ξ_topo * w_i) * log(D_f)
        """
        weighted_sum = sum(Xi_topo * w for w in weights)
        cost = weighted_sum * math.log(max(D_f, 1.0))
        self.metrics.cost_complexity = cost
        return cost
    
    def operator_R_f_disintegrate(self, problem_area: float, S: float,
                                  Xi_topo: float, Phi_Domain: float) -> float:
        """
        R_f,1: Фрактальная Дезинтеграция
        D_frac = ∫ S * Ξ_topo^(-1) * Φ_Domain^(-1) * dArea
        """
        if Xi_topo == 0 or Phi_Domain == 0:
            return 0.0
        
        D_frac = problem_area * S / (Xi_topo * Phi_Domain)
        return D_frac
    
    def operator_R_f_domain_mapping(self, user_request: str, data_corpus: str,
                                    G_S: float) -> Tuple[float, float]:
        """
        R_f,2: Отображение Области Применения
        Phi_Domain = Match(User_Request, Data_Corpus) ⊗ λ(G_S)
        Возвращает (Phi_Domain, D_f_optimal)
        """
        # Упрощенная реализация: семантическое сходство
        similarity = self._semantic_match(user_request, data_corpus)
        Phi_Domain = similarity * G_S
        
        # Оптимальная фрактальная размерность зависит от домена
        D_f_opt = self._get_optimal_Df(self.active_domain)
        
        self.metrics.Phi_Domain = Phi_Domain
        self.metrics.D_f = D_f_opt
        
        return Phi_Domain, D_f_opt
    
    def operator_R_f_coherent_assembly(self, W: float, Psi_opt: float,
                                      G_S: float, V: float, Phi_Domain: float) -> float:
        """
        R_f,3: Когерентная Сборка
        A_coh = W * Ψ_opt * e^(i*G_S) / (1-V) ⊗ Φ_Domain
        """
        if V >= 1.0:
            return float('inf')  # Идеальное состояние
        
        # Модуль комплексной экспоненты
        exp_factor = abs(complex(math.cos(G_S), math.sin(G_S)))
        A_coh = W * Psi_opt * exp_factor / (1 - V) * Phi_Domain
        
        return A_coh
    
    def full_reassembly_cycle(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Полный цикл фрактальной пересборки R_f
        
        Args:
            problem_data: Словарь с данными проблемы
            
        Returns:
            Результаты пересборки
        """
        # Этап 1: Дезинтеграция
        D_frac = self.operator_R_f_disintegrate(
            problem_data.get('area', 1.0),
            problem_data.get('S', 1.0),
            problem_data.get('Xi_topo', 1.0),
            self.metrics.Phi_Domain
        )
        
        # Этап 2: Отображение домена
        Phi_Domain, D_f_opt = self.operator_R_f_domain_mapping(
            problem_data.get('user_request', ''),
            problem_data.get('data_corpus', ''),
            self.metrics.G_S
        )
        
        # Этап 3: Когерентная сборка
        A_coh = self.operator_R_f_coherent_assembly(
            problem_data.get('W', 1.0),
            problem_data.get('Psi_opt', 0.9),
            self.metrics.G_S,
            self.metrics.V,
            Phi_Domain
        )
        
        # Расчет итоговой эффективности
        delta_V = problem_data.get('delta_V', 0.5)
        delta_S = self.metrics.delta_S or problem_data.get('delta_S', 0.3)
        cost = self.metrics.cost_complexity or problem_data.get('cost', 1.0)
        
        eta_R = self.calculate_eta_R(delta_V, delta_S, self.metrics.G_S, cost)
        
        return {
            "status": "REASSEMBLY_COMPLETE",
            "D_frac": D_frac,
            "Phi_Domain": Phi_Domain,
            "D_f_optimal": D_f_opt,
            "A_coh": A_coh,
            "eta_R": eta_R,
            "V": self.metrics.V,
            "metrics": {
                "eta_R": self.metrics.eta_R,
                "V": self.metrics.V,
                "delta_S": self.metrics.delta_S,
                "cost_complexity": self.metrics.cost_complexity
            }
        }
    
    def _semantic_match(self, request: str, corpus: str) -> float:
        """Упрощенная оценка семантического сходства"""
        # Базовая реализация: можно заменить на более сложную модель
        request_words = set(request.lower().split())
        corpus_words = set(corpus.lower().split())
        
        if not request_words or not corpus_words:
            return 0.0
        
        intersection = request_words & corpus_words
        union = request_words | corpus_words
        
        return len(intersection) / len(union) if union else 0.0
    
    def _get_optimal_Df(self, domain: Optional[str]) -> float:
        """Определение оптимальной фрактальной размерности для домена"""
        from .domains import get_domain_d_f
        
        if domain:
            return get_domain_d_f(domain)
        
        return 5.0  # Значение по умолчанию
