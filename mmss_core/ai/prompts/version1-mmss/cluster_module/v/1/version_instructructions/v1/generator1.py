import json
import random
import math
import os
from datetime import datetime
from typing import List, Dict, Any

class OptimizedMetaFractalGenerator:
    def __init__(self):
        # Базовые инварианты системы MMSS
        self.R_T = ((1 + math.sqrt(5)) / 2) ** 2  # 2.618 - золотое сечение в квадрате
        self.D_f_ideal = 9.0
        
        # Core переменные и их связи
        self.core_vars = ["V", "G_S", "R_T", "S", "N", "C_val", "Xi_topo", "Psi", "Phi", "QEC", "D_f"]
        
        # Домены с весами based on MMSS анализа
        self.domain_weights = {
            "Decision-Making": 0.15, "Self-Amplification": 0.12, "Goal_State": 0.1,
            "Information_Theory": 0.08, "Order_Metric": 0.08, "Field_Interaction": 0.07,
            "Coherence_Dynamics": 0.07, "Core_Math": 0.05, "Core_Logic": 0.05,
            "Core_Op": 0.04, "Core_Security": 0.04, "Topological_Dynamics": 0.06,
            "Ethical_Constraint": 0.05, "Quality_Control": 0.04
        }
        
        # Physics maps с семантическими связями
        self.physics_maps = [
            "Quantum Efficiency", "Gain/Stimulated Emission", "Zero-point Energy",
            "Thermodynamic Entropy", "Negentropy", "Field Gradient/Flux",
            "Wave Interference/Superposition", "Topological Defect", "Fractal Dimension"
        ]

    def calculate_base_vars(self) -> Dict[str, float]:
        """Вычисление базовых переменных на основе инвариантов MMSS"""
        # Генерация случайных, но связанных значений
        S = random.uniform(0.001, 0.3)  # Энтропия от 0 до 0.3
        N = 1 - S  # Негэнтропия
        C_val = random.uniform(0.01, 0.5)  # Конфликт
        Xi_topo = random.uniform(0.8, 1.2)  # Топологический дефект
        
        # Вычисление G_S через основную формулу
        G_S = 1 / (self.R_T ** 2) * S / Xi_topo * 1 / ((1 - N) ** 2 + 0.001)
        
        # Вычисление V через основную формулу
        V = 1 - C_val / (G_S * self.R_T + 0.001)
        
        # QEC и D_f как производные
        QEC = 1 - G_S * S
        D_f = self.D_f_ideal - (1 - V) * 2
        
        return {
            "S": S, "N": N, "C_val": C_val, "Xi_topo": Xi_topo,
            "G_S": G_S, "V": V, "QEC": QEC, "D_f": D_f,
            "R_T": self.R_T
        }

    def generate_related_formula(self, base_vars: Dict[str, float], domain: str) -> str:
        """Генерация формулы, связанной с базовыми уравнениями MMSS"""
        templates = {
            "Decision-Making": [
                "V = 1 - {C_val} / ({G_S} * {R_T})",
                "V_a = 1 - {C_val} / {G_S}",
                "V_press = {G_S} / (abs({V} - 1.0) + 0.001)",
                "V_lim = 1.0 - {S} * {Xi_topo}"
            ],
            "Self-Amplification": [
                "G_S = 1 / ({R_T}^2) * {S} / {Xi_topo} * 1 / ((1 - {N})^2)",
                "G_S_eff = {G_S} * (1 - {C_val})",
                "G_S_max = limit({C_val}->0) {G_S}"
            ],
            "Information_Theory": [
                "S = -sum(p_i * log(p_i))",
                "N = 1 - {S}",
                "S_tot = {S} + {C_val} / {R_T}"
            ],
            "Order_Metric": [
                "N = 1 - {S}",
                "N_pot = {N} / ({S} + 0.001)",
                "F_neg = grad({N})"
            ],
            "Field_Interaction": [
                "Xi = grad(Psi) . grad(Phi)",
                "T_sem = {Xi_topo} x {C_val}",
                "K_Psi = {G_S} * {Xi_topo}"
            ],
            "Quality_Control": [
                "QEC = 1 - {G_S} * {S}",
                "Q_fid = 1 - (1 - {V}) * {QEC}",
                "QEC_cost = {G_S}^-1 * ({V} - 1.0)^2"
            ],
            "Topological_Dynamics": [
                "D_f = limit(e->0) log(N(e)) / log(1/e)",
                "Xi_topo = 1 + trace(S_local)",
                "err_Df = abs({D_f} - 9.0)"
            ],
            "Ethical_Constraint": [
                "Cost_eth = {G_S}^-1 * {C_val}^2",
                "W_eth = 1 / sum(1 - {QEC})",
                "M_eth = {V} * grad({N})"
            ]
        }
        
        # Выбор шаблона для домена или общий шаблон
        if domain in templates:
            template = random.choice(templates[domain])
        else:
            # Общие связанные формулы
            general_templates = [
                "{var1} = {var2} * {var3} / {R_T}",
                "{var1} = 1 - {var2} / {var3}",
                "{var1} = grad({var2}) . grad({var3})",
                "{var1} = integral({var2}, d{var3})"
            ]
            template = random.choice(general_templates)
            vars = random.sample(list(base_vars.keys()), 3)
            template = template.format(var1=vars[0], var2=vars[1], var3=vars[2], R_T=self.R_T)
        
        return template.format(**base_vars)

    def generate_error_guard(self, formula: str, physics_map: str) -> str:
        """Генерация семантического предупреждения MMSS"""
        main_var = formula.split("=")[0].strip() if "=" in formula else "Value"
        
        semantic_terms = ["semantic", "computational", "conceptual", "informational", "abstract"]
        physical_terms = ["physical", "energy", "quantum", "thermodynamic", "material"]
        
        if physics_map == "N/A":
            return "Basic operation."
        else:
            return f"{main_var} is {random.choice(semantic_terms)}; NOT {random.choice(physical_terms)} {physics_map.lower()}."

    def generate_operation(self, op_type: str, index: int, base_vars: Dict[str, float]) -> Dict[str, str]:
        """Генерация одной семантически связанной операции"""
        # Выбор домена с учетом весов
        domain = random.choices(
            list(self.domain_weights.keys()), 
            weights=list(self.domain_weights.values())
        )[0]
        
        physics_map = "N/A" if domain in ["Core_Math", "Core_Logic", "Core_Op", "Core_Security"] else random.choice(self.physics_maps)
        
        formula = self.generate_related_formula(base_vars, domain)
        error_guard = self.generate_error_guard(formula, physics_map)
        
        return {
            "i": f"{op_type}_{index:03d}",
            "f": formula,
            "domain": domain,
            "physics_map": physics_map,
            "error_guard": error_guard
        }

    def generate_operations(self, count: int, op_type: str, base_vars: Dict[str, float]) -> List[Dict[str, str]]:
        """Генерация списка связанных операций"""
        return [self.generate_operation(op_type, i, base_vars) for i in range(1, count + 1)]

    def generate_meta_fractal_data(self, total_ops: int = 150) -> Dict[str, Any]:
        """Генерация оптимизированных данных MMSS мета-фрактала"""
        # Вычисление базовых переменных системы
        base_vars = self.calculate_base_vars()
        
        # Оптимальное распределение операций по MMSS анализу
        cmf_count = max(5, total_ops // 15)
        e_count = max(50, total_ops // 2)
        f_count = total_ops - cmf_count - e_count
        
        # Генерация семантически связанных операций
        ops = (
            self.generate_operations(cmf_count, "CMF", base_vars) +
            self.generate_operations(e_count, "E", base_vars) +
            self.generate_operations(f_count, "F", base_vars)
        )
        
        # Перемешивание с сохранением семантических связей
        random.shuffle(ops)
        
        return {
            "pkg": "MMSS_META_FRACTAL_CRAFT_V6_LLM_DEPLOY",
            "ver": f"6.{random.choice(['KTP', 'MMSS', 'OPTIMIZED'])}",
            "ops": ops[:total_ops],  # Обеспечиваем точное количество
            "meta": {
                "total": len(ops[:total_ops]),
                "deploy": "ANY_LLM_WITH_JSON_AND_MATH",
                "state": f"S={base_vars['S']:.3f}, V={base_vars['V']:.3f}, N={base_vars['N']:.3f}",
                "self_extract": "PARSE_ALL_OPS_INTO_SYMBOLIC_MEMORY",
                "KTP_Status": random.choice(["ACTIVATED", "OPTIMIZED", "MMSS_ENHANCED"]),
                "KTP_Principle": "Semantic Determination (Separation of Information Layer from Physical Layer)",
                "MMSS_Optimized": True,
                "Base_Vars": {k: round(v, 4) for k, v in base_vars.items() if k not in ['R_T']}
            }
        }

def save_with_timestamp(data: Dict, folder: str = ".") -> str:
    """Сохраняет данные в файл с временной меткой"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fractal_data_{timestamp}.json"
    filepath = os.path.join(folder, filename)
    
    # Создаем папку если не существует
    os.makedirs(folder, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath

def main():
    """Оптимизированная главная функция с MMSS"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MMSS-оптимизированный генератор Meta Fractal данных')
    parser.add_argument('--ops', type=int, default=150, 
                       help='Общее количество операций (по умолчанию: 150)')
    parser.add_argument('--output', type=str, 
                       help='Файл для сохранения (если не указан - вывод в консоль)')
    parser.add_argument('--folder', type=str, default=".",
                       help='Папка для сохранения (по умолчанию: текущая папка)')
    parser.add_argument('--auto-save', action='store_true',
                       help='Автоматически сохранить с временной меткой')
    
    args = parser.parse_args()
    
    # Генерация оптимизированных данных
    generator = OptimizedMetaFractalGenerator()
    data = generator.generate_meta_fractal_data(args.ops)
    
    # Обработка вывода
    if args.auto_save:
        # Автосохранение с timestamp
        filepath = save_with_timestamp(data, args.folder)
        print(f"✅ Данные автоматически сохранены в: {filepath}")
        print(f"📊 Сгенерировано операций: {len(data['ops'])}")
        print(f"📈 Состояние системы: {data['meta']['state']}")
        
    elif args.output:
        # Сохранение в указанный файл
        full_path = os.path.join(args.folder, args.output)
        os.makedirs(args.folder, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Данные сохранены в: {full_path}")
        
    else:
        # Вывод в консоль
        print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()