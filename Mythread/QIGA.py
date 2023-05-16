import numpy as np
from math import pi

def initialize_population(n_pop, n_bits):
    return np.random.randint(2, size=(n_pop, n_bits))

def fitness_function(x):
    return np.sum(x, axis=1)

def binary_to_decimal(x):
    return np.dot(x, 2 ** np.arange(x.shape[1])[::-1])

def decimal_to_theta(x, n_bits):
    return (x * pi) / (2 ** n_bits)

def quantum_rotation_gate(theta):
    return np.array([[np.cos(theta/2), -np.sin(theta/2)], [np.sin(theta/2), np.cos(theta/2)]])

def apply_rotation_gate(population, thetas):
    new_population = np.zeros_like(population)

    for i in range(len(population)):
        for j in range(population.shape[1]):
            new_population[i][j] = quantum_rotation_gate(thetas[j]).dot(np.array([population[i][j], 0]))[0]

    return new_population

def quantum_crossover(parent1, parent2):
    n_points = np.random.randint(1, parent1.shape[1] - 1)
    points = np.random.choice(parent1.shape[1] - 1, n_points, replace=False) + 1
    points.sort()

    child1 = np.zeros_like(parent1)
    child2 = np.zeros_like(parent2)

    start = 0
    for i in range(n_points):
        end = points[i]
        child1[:, start:end] = parent1[:, start:end]
        child2[:, start:end] = parent2[:, start:end]
        start = end

        parent1, parent2 = parent2, parent1

    child1[:, start:] = parent1[:, start:]
    child2[:, start:] = parent2[:, start:]

    return child1, child2

def quantum_mutation(population, mutation_prob):
    for i in range(population.shape[0]):
        for j in range(population.shape[1]):
            if np.random.random() < mutation_prob:
                population[i][j] = 1 - population[i][j]

    return population

def quantum_ga(n_pop, n_bits, n_gen, crossover_prob, mutation_prob, verbose=False):
    population = initialize_population(n_pop, n_bits)

    for gen in range(n_gen):
        fitness = fitness_function(population)

        max_fit_idx = np.argmax(fitness)
        max_fit = fitness[max_fit_idx]
        avg_fit = np.mean(fitness)
        min_fit = np.min(fitness)

        if verbose:
            print(f"Generation {gen}: Max Fitness = {max_fit}, Avg Fitness = {avg_fit}, Min Fitness = {min_fit}")

        if max_fit == n_bits:
            return 1

        selection_prob = fitness / np.sum(fitness)
        indices = np.random.choice(n_pop, n_pop, p=selection_prob)

        parents1 = population[indices]
        parents2 = population[np.random.choice(n_pop, n_pop, p=selection_prob)]

        thetas = decimal_to_theta(binary_to_decimal(population), n_bits)
        rotated_pop = apply_rotation_gate(population, thetas)

        offspring1, offspring2 = quantum_crossover(parents1, parents2)

        mutated_pop = quantum_mutation(np.concatenate((offspring1, offspring2)), mutation_prob)

        thetas = decimal_to_theta(binary_to_decimal(mutated_pop), n_bits)
        rotated_mutated_pop = apply_rotation_gate(mutated_pop, thetas)

        population = np.concatenate((rotated_pop, rotated_mutated_pop))

    return 0

if __name__ == '__main__':
    quantum_ga(5, 10, 2, 0.5, 0.5, verbose=True)
