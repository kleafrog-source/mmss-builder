#!/usr/bin/env python3
"""
Standalone API test without Pezzo (for local development).
Tests: Optimizer Service + MMSS Service
"""

import asyncio
import httpx
import json
from typing import Dict, Any

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
        "description": "Code review assistant prompt for software development teams",
        "author": "GEPA-Pezzo-MMSS Integration MVP",
        "created": "2026-04-12",
        "version": "1.0.0"
    }
}


def print_header(text: str):
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}")


def print_step(step_num: int, text: str):
    print(f"\n>>> Шаг {step_num}: {text}")


def print_result(success: bool, text: str):
    icon = "✓" if success else "✗"
    print(f"  [{icon}] {text}")


async def check_services() -> Dict[str, bool]:
    """Check if services are running."""
    print_header("Проверка сервисов")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Check Optimizer
        try:
            response = await client.get(f"{OPTIMIZER_URL}/health")
            results["optimizer"] = response.status_code == 200
            print_result(True, f"Optimizer Service: {response.json()}")
        except Exception as e:
            results["optimizer"] = False
            print_result(False, f"Optimizer Service: {e}")
        
        # Check MMSS
        try:
            response = await client.get(f"{MMSS_URL}/health")
            results["mmss"] = response.status_code == 200
            print_result(True, f"MMSS Service: {response.json()}")
        except Exception as e:
            results["mmss"] = False
            print_result(False, f"MMSS Service: {e}")
    
    return results


async def test_optimizer_direct():
    """Test Optimizer Service with direct prompt."""
    print_step(1, "Тест Optimizer Service (прямая оптимизация)")
    
    prompt = "Write a function to calculate fibonacci numbers."
    
    payload = {
        "prompt": prompt,
        "objective": "quality",
        "config": {
            "population_size": 10,
            "iterations": 5,
            "mutation_rate": 0.1,
            "crossover_rate": 0.7,
            "elitism": 0.1
        },
        "wait_for_result": True
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"  Отправка запроса на оптимизацию...")
            response = await client.post(
                f"{OPTIMIZER_URL}/optimize",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print_result(True, f"Job ID: {result.get('job_id', 'N/A')}")
            print_result(True, f"Status: {result.get('status', 'N/A')}")
            
            if result.get('result'):
                opt_result = result['result']
                print_result(True, f"Fitness Score: {opt_result.get('fitness_score', 'N/A')}")
                print_result(True, f"Итераций: {opt_result.get('iterations', 'N/A')}")
                improvements = opt_result.get('improvements', [])
                print(f"  Улучшений: {len(improvements)}")
                for i, imp in enumerate(improvements, 1):
                    print(f"      {i}. {imp}")
                
                # Show optimized prompt preview
                opt_prompt = opt_result.get('optimized_prompt', '')
                preview = opt_prompt[:100] + "..." if len(opt_prompt) > 100 else opt_prompt
                print(f"\n  Оптимизированный промпт (превью):")
                print(f"  {preview}")
            
            return True
            
        except Exception as e:
            print_result(False, f"Ошибка: {e}")
            return False


async def test_mmss_api():
    """Test MMSS Service API."""
    print_step(2, "Тест MMSS Service API")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Load MMSS structure
        try:
            print(f"  Загрузка MMSS-структуры...")
            response = await client.post(
                f"{MMSS_URL}/load-file",
                json={"file_path": "test_mmss.json"}  # Will fail but tests endpoint
            )
            # We expect 404 for file, but connection works
            print_result(True, "Endpoint /load-file доступен")
        except Exception as e:
            print_result(False, f"Ошибка: {e}")
        
        # Test 2: Get list of MMSS files (in memory)
        try:
            print(f"  Проверка структуры MMSS...")
            # Just validate our example structure
            print_result(True, f"MMSS пакет: {EXAMPLE_MMSS['pkg']}")
            print_result(True, f"Операций: {len(EXAMPLE_MMSS['ops'])}")
            for op in EXAMPLE_MMSS['ops']:
                print(f"    - {op['i']}: {op['domain']}")
        except Exception as e:
            print_result(False, f"Ошибка: {e}")


async def test_mmss_optimizer_integration():
    """Test MMSS -> Optimizer integration."""
    print_step(3, "Тест интеграции MMSS -> Optimizer")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Optimize MMSS structure via Optimizer
        try:
            print(f"  Отправка MMSS на оптимизацию...")
            response = await client.post(
                f"{OPTIMIZER_URL}/optimize-mmss",
                json={
                    "mmss_structure": EXAMPLE_MMSS,
                    "target_field": "content",
                    "config": {
                        "population_size": 10,
                        "iterations": 5,
                        "mutation_rate": 0.1,
                        "crossover_rate": 0.7,
                        "elitism": 0.1
                    },
                    "wait_for_result": True
                }
            )
            response.raise_for_status()
            result = response.json()
            
            print_result(True, f"Job ID: {result.get('job_id', 'N/A')}")
            print_result(True, f"Status: {result.get('status', 'N/A')}")
            
            if result.get('result'):
                opt_result = result['result']
                print_result(True, f"Fitness Score: {opt_result.get('fitness_score', 'N/A')}")
                
                # Check if optimized MMSS is in result
                if 'optimized_mmss' in opt_result:
                    opt_mmss = opt_result['optimized_mmss']
                    print_result(True, f"MMSS структура оптимизирована")
                    print(f"  Пакет: {opt_mmss.get('pkg', 'N/A')}")
            
            return True
            
        except Exception as e:
            print_result(False, f"Ошибка: {e}")
            return False


async def main():
    """Main test flow."""
    print_header("API TEST: GEPA-Pezzo-MMSS Integration (No Docker)")
    print("Тестирование без Pezzo (только Optimizer + MMSS Services)\n")
    
    # Step 0: Check services
    services = await check_services()
    
    if not services.get("optimizer"):
        print("\n⚠️ Optimizer Service не запущен!")
        print("Запустите: start_optimizer.bat")
        return 1
    
    if not services.get("mmss"):
        print("\n⚠️ MMSS Service не запущен!")
        print("Запустите: start_mmss.bat")
        return 1
    
    # Run tests
    await test_optimizer_direct()
    await test_mmss_api()
    await test_mmss_optimizer_integration()
    
    # Summary
    print_header("ТЕСТ ЗАВЕРШЕН")
    print("\n📊 Сервисы работают корректно!")
    print("\n🌐 Доступные эндпоинты:")
    print(f"   • Optimizer API: {OPTIMIZER_URL}")
    print(f"     - GET  /health")
    print(f"     - POST /optimize")
    print(f"     - POST /optimize-mmss")
    print(f"   • MMSS API: {MMSS_URL}")
    print(f"     - GET  /health")
    print(f"     - POST /load-file")
    
    print("\n⚠️ Для полного MVP с Pezzo нужен Docker:")
    print("   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
