"""Basic optimization pipeline example.

Demonstrates:
1. Loading a prompt from Pezzo
2. Running GEPA optimization
3. Saving the result as a new version
"""

import asyncio
import httpx
import json
from pathlib import Path


async def optimize_prompt_workflow(
    prompt_name: str,
    optimizer_url: str = "http://localhost:8000",
    pezzo_url: str = "http://localhost:3001"
):
    """Run basic optimization workflow.
    
    Args:
        prompt_name: Name of prompt in Pezzo to optimize
        optimizer_url: URL of optimizer service
        pezzo_url: URL of Pezzo API
    """
    print(f"=== Optimizing prompt: {prompt_name} ===\n")
    
    # Step 1: Start optimization
    print("1. Starting optimization job...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{optimizer_url}/optimize",
            json={
                "prompt_name": prompt_name,
                "config": {
                    "population_size": 20,
                    "iterations": 50,
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.8
                },
                "objective": "quality",
                "async_mode": False  # Wait for completion
            },
            timeout=300.0
        )
        response.raise_for_status()
        result = response.json()
    
    job_id = result["job_id"]
    status = result["status"]
    
    print(f"   Job ID: {job_id}")
    print(f"   Status: {status}")
    
    if status == "completed":
        print("\n2. Optimization completed!")
        
        # Get job details
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{optimizer_url}/jobs/{job_id}")
            job_data = response.json()
            job = job_data["job"]
        
        # Display results
        if job.get("result"):
            result_data = job["result"]
            print(f"   Fitness Score: {result_data.get('fitness_score', 'N/A')}")
            print(f"   Iterations: {result_data.get('iterations', 'N/A')}")
            
            improvements = result_data.get("improvements", [])
            if improvements:
                print(f"\n   Improvements:")
                for imp in improvements:
                    print(f"   - {imp}")
            
            # Show optimized content (truncated)
            optimized = result_data.get("optimized_prompt", "")
            preview = optimized[:200] + "..." if len(optimized) > 200 else optimized
            print(f"\n   Optimized Content (preview):")
            print(f"   {preview}")
        
        print("\n3. Result saved to Pezzo as new version")
        return True
    
    else:
        print(f"\n✗ Optimization failed: {result.get('message', 'Unknown error')}")
        return False


async def main():
    """Run example."""
    # Example prompt name
    prompt_name = "example-prompt-to-optimize"
    
    success = await optimize_prompt_workflow(prompt_name)
    
    if success:
        print("\n=== Workflow completed successfully ===")
    else:
        print("\n=== Workflow failed ===")


if __name__ == "__main__":
    asyncio.run(main())
