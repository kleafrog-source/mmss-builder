"""Real GEPA implementation using Mistral API for prompt optimization."""

import asyncio
import random
import httpx
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from .config import settings


@dataclass
class PromptIndividual:
    """Single prompt variant in population."""
    prompt: str
    fitness: float = 0.0
    generation: int = 0
    
    def copy(self) -> "PromptIndividual":
        return PromptIndividual(
            prompt=self.prompt,
            fitness=self.fitness,
            generation=self.generation
        )


class MistralEvaluator:
    """Evaluate prompt quality using Mistral API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.mistral_api_key
        self.model = settings.mistral_model
        self.url = "https://api.mistral.ai/v1/chat/completions"
    
    async def evaluate_prompt(self, prompt: str, objective: str = "quality") -> float:
        """Evaluate prompt fitness score (0-1)."""
        
        eval_prompts = {
            "quality": """Rate this prompt for clarity, effectiveness, and completeness on a scale of 0-100.
Consider:
- Clear instructions
- Specific context
- Expected output format
- Edge case handling

Prompt to evaluate:
---
{prompt}
---

Respond with ONLY a number 0-100.""",
            
            "conciseness": """Rate this prompt for conciseness vs information density on a scale of 0-100.
Consider:
- No unnecessary words
- Efficient information transfer
- Still maintains clarity

Prompt to evaluate:
---
{prompt}
---

Respond with ONLY a number 0-100.""",
            
            "structure": """Rate this prompt's structural organization on a scale of 0-100.
Consider:
- Logical flow
- Clear sections
- Easy to follow

Prompt to evaluate:
---
{prompt}
---

Respond with ONLY a number 0-100."""
        }
        
        eval_text = eval_prompts.get(objective, eval_prompts["quality"]).format(prompt=prompt)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": eval_text}],
                        "temperature": 0.1,
                        "max_tokens": 10
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                content = result["choices"][0]["message"]["content"].strip()
                # Extract number from response
                import re
                numbers = re.findall(r'\d+', content)
                if numbers:
                    score = int(numbers[0])
                    return min(100, max(0, score)) / 100.0
                return 0.5
        except Exception as e:
            print(f"Evaluation error: {e}")
            return 0.5  # Default on error


class GEPAEvolution:
    """Genetic Evolutionary Prompt Algorithm using Mistral."""
    
    def __init__(
        self,
        population_size: int = 10,
        iterations: int = 20,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elitism: int = 2
    ):
        self.population_size = population_size
        self.iterations = iterations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism
        self.evaluator = MistralEvaluator()
        self.improvements_log: List[str] = []
    
    def _create_population(self, seed_prompt: str) -> List[PromptIndividual]:
        """Create initial population with variations."""
        population = [PromptIndividual(prompt=seed_prompt, generation=0)]
        
        # Generate variations through mutations
        for i in range(self.population_size - 1):
            mutated = self._mutate(seed_prompt, intensity=0.3)
            population.append(PromptIndividual(prompt=mutated, generation=0))
        
        return population
    
    def _mutate(self, prompt: str, intensity: float = 0.1) -> str:
        """Apply mutation to prompt."""
        mutations = [
            self._mutate_add_instruction,
            self._mutate_add_example,
            self._mutate_restructure,
            self._mutate_clarify,
            self._mutate_add_constraint
        ]
        
        # Apply 1-3 random mutations based on intensity
        num_mutations = random.randint(1, max(1, int(3 * intensity)))
        result = prompt
        
        for _ in range(num_mutations):
            mutation = random.choice(mutations)
            result = mutation(result)
        
        return result
    
    def _mutate_add_instruction(self, prompt: str) -> str:
        """Add clarifying instruction."""
        instructions = [
            "\n\nBe specific and detailed in your response.",
            "\n\nProvide step-by-step reasoning.",
            "\n\nInclude relevant examples where applicable.",
            "\n\nConsider edge cases and mention them.",
            "\n\nStructure your response clearly with headers."
        ]
        return prompt + random.choice(instructions)
    
    def _mutate_add_example(self, prompt: str) -> str:
        """Add example to prompt."""
        if "Example:" not in prompt and "For example" not in prompt:
            return prompt + "\n\nExample: [Provide a concrete example of expected output]."
        return prompt
    
    def _mutate_restructure(self, prompt: str) -> str:
        """Restructure prompt with sections."""
        if "# " not in prompt:
            lines = prompt.split("\n")
            if len(lines) > 2:
                return f"# Task\n{lines[0]}\n\n# Context\n" + "\n".join(lines[1:])
        return prompt
    
    def _mutate_clarify(self, prompt: str) -> str:
        """Add clarification."""
        clarifications = [
            "\n\nMake sure to be precise and accurate.",
            "\n\nFocus on the most important aspects first.",
            "\n\nAvoid ambiguity in your response."
        ]
        return prompt + random.choice(clarifications)
    
    def _mutate_add_constraint(self, prompt: str) -> str:
        """Add constraint or requirement."""
        constraints = [
            "\n\nLimit your response to 3-5 key points.",
            "\n\nEnsure your answer is suitable for beginners.",
            "\n\nUse technical terminology appropriately."
        ]
        return prompt + random.choice(constraints)
    
    def _crossover(self, parent1: PromptIndividual, parent2: PromptIndividual) -> PromptIndividual:
        """Combine two prompts."""
        # Split prompts and mix sections
        p1_lines = parent1.prompt.split("\n")
        p2_lines = parent2.prompt.split("\n")
        
        if len(p1_lines) > 2 and len(p2_lines) > 2:
            # Take first part from p1, second from p2
            split = len(p1_lines) // 2
            child_lines = p1_lines[:split] + p2_lines[split:]
            child_prompt = "\n".join(child_lines)
        else:
            # Simple concatenation with separator
            child_prompt = parent1.prompt + "\n\nAdditional context:\n" + parent2.prompt
        
        return PromptIndividual(
            prompt=child_prompt,
            generation=max(parent1.generation, parent2.generation) + 1
        )
    
    def _select_parent(self, population: List[PromptIndividual]) -> PromptIndividual:
        """Tournament selection."""
        tournament_size = 3
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    async def evolve(
        self,
        seed_prompt: str,
        objective: str = "quality"
    ) -> Tuple[str, float, List[str]]:
        """Run evolutionary optimization."""
        
        # Initialize
        population = self._create_population(seed_prompt)
        best_fitness_history = []
        
        print(f"Starting GEPA evolution: pop={self.population_size}, iter={self.iterations}")
        
        for generation in range(self.iterations):
            # Evaluate population
            tasks = [self.evaluator.evaluate_prompt(ind.prompt, objective) for ind in population]
            fitness_scores = await asyncio.gather(*tasks)
            
            for ind, fitness in zip(population, fitness_scores):
                ind.fitness = fitness
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            best_fitness_history.append(population[0].fitness)
            
            print(f"  Gen {generation + 1}/{self.iterations}: best fitness = {population[0].fitness:.3f}")
            
            # Check convergence
            if generation > 5 and len(set(best_fitness_history[-5:])) == 1:
                print("  Converged!")
                break
            
            # Create next generation
            new_population = []
            
            # Elitism: keep best individuals
            new_population.extend([ind.copy() for ind in population[:self.elitism]])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    # Crossover
                    parent1 = self._select_parent(population)
                    parent2 = self._select_parent(population)
                    child = self._crossover(parent1, parent2)
                    child.generation = generation + 1
                    new_population.append(child)
                else:
                    # Mutation
                    parent = self._select_parent(population)
                    mutated_prompt = self._mutate(parent.prompt, self.mutation_rate)
                    new_population.append(PromptIndividual(
                        prompt=mutated_prompt,
                        generation=generation + 1
                    ))
            
            population = new_population
        
        # Final evaluation
        tasks = [self.evaluator.evaluate_prompt(ind.prompt, objective) for ind in population]
        fitness_scores = await asyncio.gather(*tasks)
        for ind, fitness in zip(population, fitness_scores):
            ind.fitness = fitness
        
        population.sort(key=lambda x: x.fitness, reverse=True)
        best = population[0]
        
        # Generate improvements summary
        improvements = self._generate_improvements(seed_prompt, best.prompt, best_fitness_history)
        
        return best.prompt, best.fitness, improvements
    
    def _generate_improvements(
        self,
        original: str,
        optimized: str,
        fitness_history: List[float]
    ) -> List[str]:
        """Generate list of improvements made."""
        improvements = []
        
        # Check what changed
        if len(optimized) > len(original) * 1.1:
            improvements.append("Added clarifying instructions and examples")
        
        if "# " in optimized and "# " not in original:
            improvements.append("Added structured sections with headers")
        
        if "Example:" in optimized and "Example:" not in original:
            improvements.append("Included concrete examples")
        
        if len(fitness_history) > 1 and fitness_history[-1] > fitness_history[0]:
            improvement = fitness_history[-1] - fitness_history[0]
            improvements.append(f"Fitness improved by {improvement:.1%} through {len(fitness_history)} generations")
        
        if not improvements:
            improvements.append("Prompt refined through evolutionary optimization")
        
        return improvements


async def optimize_with_gepa(
    prompt: str,
    population_size: int = 10,
    iterations: int = 20,
    objective: str = "quality"
) -> Dict[str, Any]:
    """Main entry point for GEPA optimization."""
    
    gepa = GEPAEvolution(
        population_size=population_size,
        iterations=iterations,
        mutation_rate=0.15,
        crossover_rate=0.7,
        elitism=2
    )
    
    optimized_prompt, fitness, improvements = await gepa.evolve(prompt, objective)
    
    return {
        "optimized_prompt": optimized_prompt,
        "fitness_score": fitness,
        "iterations": iterations,
        "improvements": improvements,
        "metadata": {
            "algorithm": "GEPA",
            "evaluator": "Mistral API",
            "population_size": population_size,
            "final_fitness": fitness
        }
    }
