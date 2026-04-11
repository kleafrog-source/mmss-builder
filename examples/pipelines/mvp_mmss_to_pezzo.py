"""MVP: MMSS → Pezzo → GEPA → Pezzo

End-to-end сценарий:
1. Создает MMSS-структуру (code review prompt)
2. Загружает в Pezzo через MMSS Service
3. Оптимизирует через Optimizer Service (GEPA)
4. Сохраняет результат как новую версию в Pezzo

Запуск:
    python examples/pipelines/mvp_mmss_to_pezzo.py

Требования:
    - Запущен Pezzo: docker-compose up -d pezzo-server pezzo-console postgres
    - Запущен Optimizer: cd services/optimizer && python -m uvicorn src.api:app
    - Запущен MMSS Service: cd services/mmss && python -m uvicorn src.api:app --port 8001
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Добавляем путь к сервисам для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "mmss" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "optimizer" / "src"))

# Конфигурация сервисов
PEZZO_URL = "http://localhost:3001"
OPTIMIZER_URL = "http://localhost:8000"
MMSS_URL = "http://localhost:8001"

# Пример MMSS-структуры для code review
EXAMPLE_MMSS: Dict[str, Any] = {
    "pkg": "MVP_CODE_REVIEW_PROMPT",
    "ver": "1.0.0",
    "ops": [
        {
            "i": "SYS_PROMPT",
            "f": "You are an expert code reviewer. Analyze the provided code for: security vulnerabilities, performance issues, code style violations, and maintainability concerns. Provide specific, actionable recommendations.",
            "domain": "CodeReview",
            "physics_map": "Expertise Field",
            "error_guard": "Focus on constructive feedback, not criticism"
        },
        {
            "i": "FORMAT_INSTRUCTIONS",
            "f": "Structure your response as: 1) Summary 2) Critical Issues 3) Warnings 4) Suggestions. Use code examples where applicable.",
            "domain": "OutputFormat",
            "physics_map": "Structural Template",
            "error_guard": "Maintain consistent formatting"
        },
        {
            "i": "CONTEXT_AWARENESS",
            "f": "Consider: programming language conventions, project context, team experience level, and business requirements when evaluating code.",
            "domain": "ContextualAnalysis",
            "physics_map": "Adaptive Field",
            "error_guard": "Context is key; generic advice may not apply"
        }
    ],
    "metadata": {
        "purpose": "Code review assistant",
        "target_audience": "Development teams",
        "language": "en"
    }
}


async def check_service_health(url: str, name: str) -> bool:
    """Проверка доступности сервиса."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/health", timeout=5.0)
            if response.status_code == 200:
                print(f"  ✓ {name} доступен")
                return True
    except Exception as e:
        pass
    print(f"  ✗ {name} недоступен ({url})")
    return False


async def wait_for_services():
    """Ожидание запуска всех сервисов."""
    print("\n=== Проверка сервисов ===")
    
    services = [
        (PEZZO_URL, "Pezzo API"),
        (OPTIMIZER_URL, "Optimizer Service"),
        (MMSS_URL, "MMSS Service"),
    ]
    
    all_ready = True
    for url, name in services:
        if not await check_service_health(url, name):
            all_ready = False
    
    if not all_ready:
        print("\n⚠️  Не все сервисы доступны. Убедитесь, что:")
        print("   1. Pezzo запущен: docker-compose up -d pezzo-server pezzo-console postgres")
        print("   2. Optimizer запущен: cd services/optimizer && python -m uvicorn src.api:app")
        print("   3. MMSS Service запущен: cd services/mmss && python -m uvicorn src.api:app --port 8001")
        return False
    
    return True


async def step1_create_mmss_in_pezzo() -> str:
    """Шаг 1: Создание промпта из MMSS в Pezzo.
    
    Returns:
        ID созданного промпта в Pezzo
    """
    print("\n=== Шаг 1: MMSS → Pezzo ===")
    print(f"Создаем промпт из пакета: {EXAMPLE_MMSS['pkg']}")
    
    async with httpx.AsyncClient() as client:
        # Используем MMSS Service для импорта
        response = await client.post(
            f"{MMSS_URL}/import",
            json={
                "mmss_structure": EXAMPLE_MMSS,
                "prompt_name": EXAMPLE_MMSS["pkg"],
                "description": f"MVP: {EXAMPLE_MMSS['metadata']['purpose']}"
            },
            timeout=30.0
        )
        response.raise_for_status()
        prompt = response.json()
    
    prompt_id = prompt["id"]
    print(f"  ✓ Создан промпт в Pezzo: {prompt['name']}")
    print(f"  ✓ ID: {prompt_id}")
    print(f"  ✓ Операций: {len(EXAMPLE_MMSS['ops'])}")
    
    return prompt_id


async def step2_optimize_prompt(prompt_name: str) -> Dict[str, Any]:
    """Шаг 2: Оптимизация промпта через GEPA.
    
    Returns:
        Результат оптимизации с job_id и статусом
    """
    print("\n=== Шаг 2: Оптимизация через GEPA ===")
    print(f"Запускаем оптимизацию: {prompt_name}")
    
    async with httpx.AsyncClient() as client:
        # Запускаем оптимизацию через Optimizer Service
        response = await client.post(
            f"{OPTIMIZER_URL}/optimize",
            json={
                "prompt_name": prompt_name,
                "config": {
                    "population_size": 10,  # Меньше для MVP
                    "iterations": 20,       # Меньше для MVP
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.8
                },
                "objective": "quality",
                "async_mode": False  # Ждем завершения
            },
            timeout=120.0
        )
        response.raise_for_status()
        result = response.json()
    
    job_id = result["job_id"]
    status = result["status"]
    
    print(f"  ✓ Job ID: {job_id}")
    print(f"  ✓ Статус: {status}")
    
    if status == "completed":
        # Получаем детали результата
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OPTIMIZER_URL}/jobs/{job_id}")
            job_data = response.json()
            job = job_data.get("job", {})
        
        if job.get("result"):
            opt_result = job["result"]
            print(f"  ✓ Fitness Score: {opt_result.get('fitness_score', 'N/A')}")
            print(f"  ✓ Итераций: {opt_result.get('iterations', 'N/A')}")
            
            improvements = opt_result.get("improvements", [])
            if improvements:
                print(f"  ✓ Улучшения ({len(improvements)}):")
                for i, imp in enumerate(improvements[:3], 1):
                    print(f"      {i}. {imp}")
    
    return result


async def step3_verify_in_pezzo(prompt_name: str):
    """Шаг 3: Проверка результата в Pezzo.
    
    Показывает список версий промпта.
    """
    print("\n=== Шаг 3: Проверка в Pezzo ===")
    print(f"Проверяем версии промпта: {prompt_name}")
    
    async with httpx.AsyncClient() as client:
        # Получаем промпт по имени
        response = await client.get(
            f"{PEZZO_URL}/api/prompts",
            params={"name": prompt_name},
            timeout=10.0
        )
        response.raise_for_status()
        prompts = response.json()
        
        if not prompts:
            print("  ✗ Промпт не найден")
            return
        
        prompt = prompts[0]
        versions = prompt.get("versions", [])
        
        print(f"  ✓ Найден промпт: {prompt['name']}")
        print(f"  ✓ Версий: {len(versions)}")
        
        for i, version in enumerate(versions[:3], 1):
            sha = version.get("sha", "N/A")[:8]
            message = version.get("message", "No message")
            print(f"      {i}. {sha} - {message}")


async def main():
    """Главный MVP workflow."""
    print("=" * 60)
    print("MVP: MMSS → Pezzo → GEPA → Pezzo")
    print("=" * 60)
    
    # Проверяем сервисы
    if not await wait_for_services():
        print("\n❌ MVP прерван: не все сервисы доступны")
        return 1
    
    try:
        # Шаг 1: Создаем MMSS в Pezzo
        prompt_id = await step1_create_mmss_in_pezzo()
        prompt_name = EXAMPLE_MMSS["pkg"]
        
        # Шаг 2: Оптимизируем
        opt_result = await step2_optimize_prompt(prompt_name)
        
        if opt_result["status"] != "completed":
            print(f"\n⚠️ Оптимизация завершилась с ошибкой: {opt_result.get('message')}")
            return 1
        
        # Шаг 3: Проверяем результат
        await step3_verify_in_pezzo(prompt_name)
        
        # Финальный вывод
        print("\n" + "=" * 60)
        print("✅ MVP УСПЕШНО ЗАВЕРШЕН")
        print("=" * 60)
        print(f"\n📊 Результаты:")
        print(f"   • Промпт в Pezzo: {prompt_name}")
        print(f"   • ID: {prompt_id}")
        print(f"   • Job ID: {opt_result['job_id']}")
        print(f"\n🌐 Интерфейсы:")
        print(f"   • Pezzo Console: http://localhost:4200")
        print(f"   • Pezzo API: http://localhost:3001")
        print(f"   • Optimizer API: http://localhost:8000")
        print(f"\n📖 Дальнейшие шаги:")
        print(f"   1. Откройте Pezzo Console: http://localhost:4200")
        print(f"   2. Найдите промпт '{prompt_name}'")
        print(f"   3. Посмотрите версии и сравните до/после")
        
        return 0
        
    except httpx.HTTPError as e:
        print(f"\n❌ HTTP ошибка: {e}")
        print("Убедитесь, что все сервисы запущены и доступны")
        return 1
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
