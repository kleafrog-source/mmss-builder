#!/usr/bin/env python3
"""Batch optimization script for MMSS prompts in a folder.

Usage:
    python examples/batch_optimize.py extract/prompt-db-local/database --population 10 --iterations 20
    
Features:
    - Scans folder for JSON files
    - Imports each as prompt
    - Optimizes with GEPA
    - Exports results
    - Progress tracking
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import httpx
from datetime import datetime

# API URLs
PROMPT_MANAGER_URL = "http://localhost:8002"
OPTIMIZER_URL = "http://localhost:8000"


class BatchOptimizer:
    """Batch optimizer for MMSS prompts."""
    
    def __init__(self, base_url: str = PROMPT_MANAGER_URL):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
        
    async def import_prompt(self, file_path: Path, category: str = "imported") -> Dict[str, Any]:
        """Import single JSON file as prompt."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                mmss_data = json.load(f)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/prompts/import",
                    json={
                        "mmss_structure": mmss_data,
                        "category": category,
                        "tags": ["batch-imported"]
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"  ❌ Import failed for {file_path.name}: {e}")
            return None
    
    async def optimize_prompt(
        self,
        prompt_id: str,
        population_size: int = 10,
        iterations: int = 20
    ) -> Dict[str, Any]:
        """Optimize single prompt."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/prompts/{prompt_id}/optimize",
                    json={
                        "population_size": population_size,
                        "iterations": iterations
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"  ❌ Optimization failed: {e}")
            return None
    
    async def export_prompt(self, prompt_id: str, output_dir: Path) -> bool:
        """Export optimized prompt to file."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/prompts/{prompt_id}/export?format=mmss"
                )
                response.raise_for_status()
                mmss_data = response.json()
                
                # Save to output directory
                output_path = output_dir / f"{prompt_id}_optimized.json"
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(mmss_data, f, indent=2, ensure_ascii=False)
                return True
        except Exception as e:
            print(f"  ❌ Export failed: {e}")
            return False
    
    async def process_file(
        self,
        file_path: Path,
        population_size: int,
        iterations: int,
        output_dir: Path,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """Process single file: import → optimize → export."""
        result = {
            "file": file_path.name,
            "status": "pending",
            "prompt_id": None,
            "old_version": None,
            "new_version": None,
            "fitness_score": None,
            "error": None
        }
        
        print(f"\n📄 Processing: {file_path.name}")
        
        # Import
        print("  📥 Importing...")
        prompt = await self.import_prompt(file_path)
        if not prompt:
            result["status"] = "import_failed"
            result["error"] = "Import failed"
            return result
        
        result["prompt_id"] = prompt["metadata"]["id"]
        result["old_version"] = prompt["metadata"]["version"]
        
        # Skip if already optimized
        if skip_existing and len(prompt.get("optimization_history", [])) > 0:
            print("  ⏭️  Already optimized, skipping")
            result["status"] = "skipped"
            return result
        
        # Optimize
        print(f"  ⚡ Optimizing (pop={population_size}, iter={iterations})...")
        optimized = await self.optimize_prompt(
            prompt["metadata"]["id"],
            population_size,
            iterations
        )
        
        if not optimized:
            result["status"] = "optimization_failed"
            result["error"] = "Optimization failed"
            return result
        
        result["new_version"] = optimized["metadata"]["version"]
        result["status"] = "optimized"
        
        # Get fitness from history
        history = optimized.get("optimization_history", [])
        if history:
            result["fitness_score"] = history[-1].get("fitness_score")
            print(f"  ✅ Optimized! Fitness: {result['fitness_score']:.3f}, Version: {result['old_version']} → {result['new_version']}")
        else:
            print(f"  ✅ Optimized! Version: {result['old_version']} → {result['new_version']}")
        
        # Export
        if output_dir:
            print("  💾 Exporting...")
            await self.export_prompt(prompt["metadata"]["id"], output_dir)
        
        return result
    
    async def batch_optimize(
        self,
        input_dir: Path,
        population_size: int = 10,
        iterations: int = 20,
        output_dir: Path = None,
        pattern: str = "*.json",
        skip_existing: bool = True
    ):
        """Process all files in directory."""
        
        # Find all JSON files
        files = list(input_dir.glob(pattern))
        if not files:
            print(f"No {pattern} files found in {input_dir}")
            return
        
        print(f"\n{'='*60}")
        print(f"🚀 Batch Optimization Started")
        print(f"{'='*60}")
        print(f"📁 Input: {input_dir}")
        print(f"📊 Files: {len(files)}")
        print(f"⚙️  Population: {population_size}, Iterations: {iterations}")
        print(f"{'='*60}\n")
        
        # Create output directory
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each file
        start_time = datetime.now()
        
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}]", end="")
            result = await self.process_file(
                file_path,
                population_size,
                iterations,
                output_dir,
                skip_existing
            )
            self.results.append(result)
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        self.print_summary(duration)
    
    def print_summary(self, duration: float):
        """Print batch optimization summary."""
        total = len(self.results)
        optimized = sum(1 for r in self.results if r["status"] == "optimized")
        skipped = sum(1 for r in self.results if r["status"] == "skipped")
        failed = sum(1 for r in self.results if "failed" in r["status"])
        
        # Fitness statistics
        fitness_scores = [
            r["fitness_score"] for r in self.results 
            if r["fitness_score"] is not None
        ]
        
        print(f"\n{'='*60}")
        print(f"📊 BATCH OPTIMIZATION SUMMARY")
        print(f"{'='*60}")
        print(f"⏱️  Duration: {duration:.1f}s")
        print(f"📁 Total files: {total}")
        print(f"✅ Optimized: {optimized}")
        print(f"⏭️  Skipped (already optimized): {skipped}")
        print(f"❌ Failed: {failed}")
        
        if fitness_scores:
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            max_fitness = max(fitness_scores)
            min_fitness = min(fitness_scores)
            print(f"\n🎯 FITNESS SCORES:")
            print(f"   Average: {avg_fitness:.3f}")
            print(f"   Max: {max_fitness:.3f}")
            print(f"   Min: {min_fitness:.3f}")
        
        print(f"{'='*60}\n")
        
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "summary": {
                "total": total,
                "optimized": optimized,
                "skipped": skipped,
                "failed": failed
            },
            "fitness_stats": {
                "average": sum(fitness_scores) / len(fitness_scores) if fitness_scores else None,
                "max": max(fitness_scores) if fitness_scores else None,
                "min": min(fitness_scores) if fitness_scores else None
            } if fitness_scores else None,
            "results": self.results
        }
        
        report_path = Path("batch_optimization_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📝 Report saved: {report_path}")


async def main():
    parser = argparse.ArgumentParser(
        description="Batch optimize MMSS prompts from a folder"
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing MMSS JSON files"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("optimized_prompts"),
        help="Output directory for optimized prompts (default: optimized_prompts)"
    )
    parser.add_argument(
        "--population",
        "-p",
        type=int,
        default=10,
        help="Population size for GEPA (default: 10)"
    )
    parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=20,
        help="Iterations for GEPA (default: 20)"
    )
    parser.add_argument(
        "--pattern",
        default="*.json",
        help="File pattern to match (default: *.json)"
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Don't skip already optimized prompts"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"❌ Directory not found: {args.input_dir}")
        sys.exit(1)
    
    optimizer = BatchOptimizer()
    await optimizer.batch_optimize(
        input_dir=args.input_dir,
        population_size=args.population,
        iterations=args.iterations,
        output_dir=args.output_dir,
        pattern=args.pattern,
        skip_existing=not args.no_skip
    )


if __name__ == "__main__":
    asyncio.run(main())
