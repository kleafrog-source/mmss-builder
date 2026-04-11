"""MMSS to Pezzo optimization pipeline example.

Demonstrates end-to-end workflow:
1. Load MMSS structure from file
2. Import to Pezzo
3. Run optimization via GEPA
4. Export optimized result back to MMSS format
"""

import asyncio
import httpx
import json
from pathlib import Path


# Example MMSS structure
EXAMPLE_MMSS = {
    "pkg": "EXAMPLE_OPTIMIZATION_PKG",
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
    ]
}


async def mmss_optimization_workflow(
    mmss_service_url: str = "http://localhost:8001",
    optimizer_url: str = "http://localhost:8000",
    pezzo_url: str = "http://localhost:3001"
):
    """Run MMSS optimization workflow.
    
    Args:
        mmss_service_url: URL of MMSS service
        optimizer_url: URL of optimizer service
        pezzo_url: URL of Pezzo API
    """
    print("=== MMSS to Pezzo Optimization Pipeline ===\n")
    
    # Step 1: Import MMSS to Pezzo
    print("1. Importing MMSS structure to Pezzo...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{mmss_service_url}/import",
            json={
                "mmss_structure": EXAMPLE_MMSS,
                "prompt_name": EXAMPLE_MMSS["pkg"],
                "description": "Example MMSS structure for code review optimization"
            },
            timeout=30.0
        )
        response.raise_for_status()
        prompt = response.json()
    
    prompt_id = prompt["id"]
    print(f"   ✓ Created prompt: {prompt['name']}")
    print(f"   ✓ Prompt ID: {prompt_id}")
    
    # Step 2: Optimize via MMSS service (calls optimizer internally)
    print("\n2. Running GEPA optimization...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{mmss_service_url}/optimize",
            json={
                "mmss_structure": EXAMPLE_MMSS,
                "prompt_name": f"{EXAMPLE_MMSS['pkg']}-optimized",
                "target_field": "content"
            },
            timeout=300.0
        )
        response.raise_for_status()
        opt_result = response.json()
    
    job_id = opt_result["job_id"]
    status = opt_result["status"]
    print(f"   ✓ Optimization job started: {job_id}")
    print(f"   Status: {status}")
    
    if status == "completed":
        print("\n3. Getting optimized result...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{optimizer_url}/jobs/{job_id}")
            job_data = response.json()
            job = job_data["job"]
        
        if job.get("result"):
            result = job["result"]
            print(f"   Fitness Score: {result.get('fitness_score', 'N/A')}")
            print(f"   Iterations: {result.get('iterations', 'N/A')}")
        
        # Step 4: Export back to MMSS format
        print("\n4. Exporting optimized result to MMSS format...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{mmss_service_url}/export/{job['prompt_id']}",
                timeout=30.0
            )
            response.raise_for_status()
            mmss_result = response.json()
        
        print(f"   ✓ Exported MMSS package: {mmss_result.get('pkg', 'N/A')}")
        print(f"   ✓ Version: {mmss_result.get('ver', 'N/A')}")
        print(f"   ✓ Operations: {len(mmss_result.get('ops', []))}")
        
        # Save to file
        output_file = Path("optimized_mmss_example.json")
        output_file.write_text(
            json.dumps(mmss_result, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"\n5. Saved to file: {output_file}")
        
        return True
    
    else:
        print(f"\n✗ Optimization failed: {opt_result.get('message', 'Unknown error')}")
        return False


async def main():
    """Run example."""
    success = await mmss_optimization_workflow()
    
    if success:
        print("\n=== Pipeline completed successfully ===")
        print("\nNext steps:")
        print("1. Check Pezzo console at http://localhost:4200")
        print("2. Review the optimized prompt versions")
        print("3. Load the optimized MMSS from optimized_mmss_example.json")
    else:
        print("\n=== Pipeline failed ===")


if __name__ == "__main__":
    asyncio.run(main())
