"""Genetic algorithm for prompt evolution."""
import random
from dataclasses import dataclass
from typing import List, Tuple, Callable

from local_bridge import ollama


@dataclass
class Chromosome:
    """A prompt chromosome."""
    genes: str  # The prompt text
    fitness: float = 0.0


class GeneticEvolver:
    """Evolve prompts using genetic algorithms."""
    
    def __init__(self, population_size: int = 10, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population: List[Chromosome] = []
    
    def initialize(self, seed_prompts: List[str]):
        """Initialize population from seed prompts."""
        self.population = [Chromosome(genes=p) for p in seed_prompts]
        while len(self.population) < self.population_size:
            parent = random.choice(seed_prompts)
            mutated = self._mutate(parent)
            self.population.append(Chromosome(genes=mutated))
    
    def evolve(self, task: str, generations: int = 5, fitness_fn: Callable = None) -> str:
        """Evolve prompts for a task."""
        if fitness_fn is None:
            fitness_fn = self._default_fitness
        
        for gen in range(generations):
            # Evaluate fitness
            for chrom in self.population:
                chrom.fitness = fitness_fn(chrom.genes, task)
            
            # Selection
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            survivors = self.population[:self.population_size // 2]
            
            # Crossover and mutation
            new_pop = survivors.copy()
            while len(new_pop) < self.population_size:
                p1, p2 = random.sample(survivors, 2)
                child_genes = self._crossover(p1.genes, p2.genes)
                if random.random() < self.mutation_rate:
                    child_genes = self._mutate(child_genes)
                new_pop.append(Chromosome(genes=child_genes))
            
            self.population = new_pop
        
        return max(self.population, key=lambda x: x.fitness).genes
    
    def _crossover(self, p1: str, p2: str) -> str:
        """Single-point crossover."""
        words1, words2 = p1.split(), p2.split()
        point = len(words1) // 2
        return ' '.join(words1[:point] + words2[point:])
    
    def _mutate(self, prompt: str) -> str:
        """Mutate prompt using LLM."""
        mutation_prompt = f"Rephrase this instruction slightly differently: {prompt}"
        return ollama.generate(mutation_prompt)[:500]
    
    def _default_fitness(self, prompt: str, task: str) -> float:
        """Default fitness: response quality score."""
        response = ollama.generate(f"{prompt}\n\nTask: {task}")
        # Simple length-based scoring (should be replaced)
        return min(len(response) / 100, 10.0)
