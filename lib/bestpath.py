import six
import sys

sys.modules["sklearn.externals.six"] = six
import mlrose
import numpy as np


# fitness description
destinations = [
    (3, 1),
    (31, 25),
    (44, 13),
    (20, 3),
    (9, 23),
    (20, 50),
    (35, 50),
    (1, 37),
]
fitness_destinations = mlrose.TravellingSales(coords=destinations)

# optimization definition
problem_fit = mlrose.TSPOpt(
    length=8, fitness_fn=fitness_destinations, maximize=False
)
# generic geneTic algorithm
best_state, best_fitness = mlrose.genetic_alg(problem_fit, random_state=2)

print(best_state)
print(best_fitness)

# potentially optimized genetic algorithm
best_state, best_fitness = mlrose.genetic_alg(
    problem_fit, mutation_prob=0.2, max_attempts=100, random_state=2
)

print(best_state)
