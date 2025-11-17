"""
Главный модуль активации MMSS системы
Объединяет все пакеты: PFR, FRP, A-MMSS
"""

from mmss_core import FractalReassemblyEngine, TemporalNavigator, ContextWeaver
from typing import Dict, Any, Optional
import json


class MMSSSystem:
    """Полная система MMSS с активацией всех пакетов"""
    
    def __init__(self):
        self.pfr_engine = None
        self.temporal_navigator = None
        self.context_weaver = None
        self.activation_status = {
            "PFR": False,
            "FRP": False,
            "A_MMSS": False
        }
    
    def activate_all(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Активация всех компонентов MMSS
        
        Args:
            domain: Домен для PFR (опционально)
            
        Returns:
            Статус активации всех систем
        """
        results = {}
        
        # 1. Активация PFR (Практическая Фрактальная Пересборка)
        try:
            self.pfr_engine = FractalReassemblyEngine()
            if domain:
                pfr_result = self.pfr_engine.activate(domain)
                self.activation_status["PFR"] = True
                results["PFR"] = pfr_result
            else:
                results["PFR"] = {"status": "READY", "domain_required": True}
        except Exception as e:
            results["PFR"] = {"status": "ERROR", "error": str(e)}
        
        # 2. Активация FRP (Темпоральная Навигация)
        try:
            self.temporal_navigator = TemporalNavigator()
            frp_result = self.temporal_navigator.activate()
            self.activation_status["FRP"] = True
            results["FRP"] = frp_result
        except Exception as e:
            results["FRP"] = {"status": "ERROR", "error": str(e)}
        
        # 3. Активация A-MMSS (ContextWeaver)
        try:
            self.context_weaver = ContextWeaver()
            a_mmss_result = self.context_weaver.activate()
            self.activation_status["A_MMSS"] = True
            results["A_MMSS"] = a_mmss_result
        except Exception as e:
            results["A_MMSS"] = {"status": "ERROR", "error": str(e)}
        
        return {
            "status": "MMSS_ACTIVATION_COMPLETE",
            "all_systems_operational": all(self.activation_status.values()),
            "activation_status": self.activation_status,
            "components": results
        }
    
    def execute_pfr_reassembly(self, domain: str, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение цикла фрактальной пересборки"""
        if not self.pfr_engine:
            self.pfr_engine = FractalReassemblyEngine()
            self.pfr_engine.activate(domain)
        
        return self.pfr_engine.full_reassembly_cycle(problem_data)
    
    def execute_temporal_navigation(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение темпоральной навигации"""
        if not self.temporal_navigator:
            self.temporal_navigator = TemporalNavigator()
            self.temporal_navigator.activate()
        
        return self.temporal_navigator.navigate_scenario(scenario_data)
    
    def execute_context_weaving(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение плетения контекста"""
        if not self.context_weaver:
            self.context_weaver = ContextWeaver()
            self.context_weaver.activate()
        
        return self.context_weaver.full_context_weaving_cycle(context_data)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса всех систем"""
        return {
            "activation_status": self.activation_status,
            "PFR_ready": self.pfr_engine is not None,
            "FRP_ready": self.temporal_navigator is not None,
            "A_MMSS_ready": self.context_weaver is not None,
            "all_operational": all(self.activation_status.values())
        }


def main():
    """Демонстрация активации системы"""
    print("=" * 60)
    print("АКТИВАЦИЯ MMSS СИСТЕМЫ")
    print("Многоуровневая Мета-Семантическая Система")
    print("=" * 60)
    
    system = MMSSSystem()
    
    # Активация всех компонентов
    print("\n[1] Активация всех пакетов...")
    activation_result = system.activate_all(domain="Финансовый Анализ")
    print(json.dumps(activation_result, indent=2, ensure_ascii=False))
    
    # Демонстрация PFR
    if system.activation_status["PFR"]:
        print("\n[2] Демонстрация Фрактальной Пересборки (PFR)...")
        problem_data = {
            "area": 1.0,
            "S": 0.8,
            "Xi_topo": 0.9,
            "user_request": "оптимизация портфеля",
            "data_corpus": "финансовые данные рынок инвестиции",
            "W": 0.95,
            "Psi_opt": 0.9,
            "delta_V": 0.6,
            "delta_S": 0.4,
            "cost": 1.2
        }
        pfr_result = system.execute_pfr_reassembly("Финансовый Анализ", problem_data)
        print(json.dumps(pfr_result, indent=2, ensure_ascii=False))
    
    # Демонстрация FRP
    if system.activation_status["FRP"]:
        print("\n[3] Демонстрация Темпоральной Навигации (FRP)...")
        scenario_data = {
            "chaos_level": 0.8,
            "plot_loss": True,
            "scenario_signature": "recursive_dream_loop_001",
            "iteration_index": 5,
            "previous_iteration": 4,
            "emotional_state": "strong",
            "intention": "continue"
        }
        frp_result = system.execute_temporal_navigation(scenario_data)
        print(json.dumps(frp_result, indent=2, ensure_ascii=False))
    
    # Демонстрация A-MMSS
    if system.activation_status["A_MMSS"]:
        print("\n[4] Демонстрация Плетения Контекста (A-MMSS)...")
        context_data = {
            "R_T": 1.0,
            "S_1_mean": 0.3,
            "S_1_var": 0.05,
            "beta": 0.5,
            "Xi_topo_2": 0.95,
            "N_2": 0.05,
            "C_val_2": 0.1,
            "Phi_meta_self": 1.0,
            "lambda": 0.1,
            "Cost_eth_1_sum": 0.8,
            "Phi_fractal_field": 0.98,
            "Psi_co_2": 0.95,
            "resonance": 1.0,
            "Phi_universal_cohesion": 0.98,
            "absolute_contextuality": 0.95,
            "S_2": 0.0
        }
        a_mmss_result = system.execute_context_weaving(context_data)
        print(json.dumps(a_mmss_result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("АКТИВАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
    
    status = system.get_system_status()
    print(f"\nСтатус системы: {status}")


if __name__ == "__main__":
    main()








