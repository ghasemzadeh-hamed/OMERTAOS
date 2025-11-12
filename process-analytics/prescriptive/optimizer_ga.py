"""Genetic algorithm optimizer for prescriptive analytics."""

import random
from typing import Any, Dict, List, Tuple


class GeneticOptimizer:
    """Simple genetic algorithm for optimizing discrete decisions."""

    def __init__(self, population_size: int = 20, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate

    def optimize(self, decision_space: List[Dict[str, Any]], fitness_fn) -> Dict[str, Any]:
        """Perform a basic GA search over the decision space."""
        population = random.sample(decision_space, min(self.population_size, len(decision_space)))
        best = max(population, key=fitness_fn)
        for _ in range(10):
            parents = self._select_parents(population, fitness_fn)
            offspring = self._crossover(*parents)
            offspring = self._mutate(offspring, decision_space)
            if fitness_fn(offspring) > fitness_fn(best):
                best = offspring
        return best

    def _select_parents(self, population: List[Dict[str, Any]], fitness_fn) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        sorted_population = sorted(population, key=fitness_fn, reverse=True)
        return sorted_population[0], sorted_population[1]

    def _crossover(self, parent_a: Dict[str, Any], parent_b: Dict[str, Any]) -> Dict[str, Any]:
        child = parent_a.copy()
        for key, value in parent_b.items():
            if random.random() < 0.5:
                child[key] = value
        return child

    def _mutate(self, candidate: Dict[str, Any], decision_space: List[Dict[str, Any]]) -> Dict[str, Any]:
        if random.random() < self.mutation_rate:
            mutation = random.choice(decision_space)
            candidate.update(mutation)
        return candidate
