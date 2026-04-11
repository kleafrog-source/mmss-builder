"""GEPA / GEPA-MCP Client."""

import httpx
import json
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel

from .config import settings


class OptimizationResult(BaseModel):
    """Result of prompt optimization."""
    optimized_prompt: str
    iterations: int
    fitness_score: float
    improvements: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class GEPAConfig(BaseModel):
    """GEPA optimization configuration."""
    population_size: int = 20
    iterations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    elitism: int = 2


class GEPAClient:
    """Client for GEPA optimization via MCP or direct API."""
    
    def __init__(self, mcp_url: str = None, api_key: str = None):
        self.mcp_url = mcp_url or settings.gepa_mcp_url
        self.api_key = api_key or settings.gepa_api_key
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def optimize_prompt(
        self,
        prompt: str,
        config: Optional[GEPAConfig] = None,
        objective: str = "quality"
    ) -> OptimizationResult:
        """Optimize a prompt using GEPA.
        
        Args:
            prompt: Original prompt to optimize
            config: GEPA configuration
            objective: Optimization objective (quality, conciseness, etc.)
        
        Returns:
            OptimizationResult with optimized prompt and metadata
        """
        config = config or GEPAConfig(
            population_size=settings.gepa_population,
            iterations=settings.gepa_iterations
        )
        
        payload = {
            "method": "optimize_prompt",
            "params": {
                "prompt": prompt,
                "population_size": config.population_size,
                "iterations": config.iterations,
                "mutation_rate": config.mutation_rate,
                "crossover_rate": config.crossover_rate,
                "elitism": config.elitism,
                "objective": objective
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.mcp_url}/mcp",
                json=payload,
                headers=self.headers,
                timeout=300.0  # 5 минут на оптимизацию
            )
            response.raise_for_status()
            result = response.json()
        
        return OptimizationResult(
            optimized_prompt=result.get("optimized_prompt", prompt),
            iterations=result.get("iterations", config.iterations),
            fitness_score=result.get("fitness_score", 0.0),
            improvements=result.get("improvements", []),
            metadata=result.get("metadata", {})
        )
    
    async def optimize_mmss_structure(
        self,
        mmss_structure: Dict[str, Any],
        target_field: str = "content",
        config: Optional[GEPAConfig] = None
    ) -> OptimizationResult:
        """Optimize a specific field within MMSS structure.
        
        Args:
            mmss_structure: MMSS JSON structure
            target_field: Field to optimize (e.g., "content", "description")
            config: GEPA configuration
        
        Returns:
            OptimizationResult with optimized structure
        """
        # Extract content to optimize
        content = mmss_structure.get(target_field, "")
        if not isinstance(content, str):
            content = json.dumps(content, indent=2)
        
        # Optimize the content
        result = await self.optimize_prompt(content, config, objective="mmss_optimization")
        
        # Create optimized structure
        optimized_structure = dict(mmss_structure)
        optimized_structure[target_field] = result.optimized_prompt
        optimized_structure["_optimization_meta"] = {
            "original_fitness": result.fitness_score,
            "iterations": result.iterations,
            "improvements": result.improvements
        }
        
        return OptimizationResult(
            optimized_prompt=json.dumps(optimized_structure, indent=2),
            iterations=result.iterations,
            fitness_score=result.fitness_score,
            improvements=result.improvements,
            metadata={"structure": optimized_structure}
        )
    
    async def health_check(self) -> bool:
        """Check if GEPA service is available."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.mcp_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception:
            return False


# Singleton instance
gepa_client = GEPAClient()
