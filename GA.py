import random
# 设置遗传算法参数
POPULATION_SIZE = 20
GENERATIONS = 50
MUTATION_RATE = 0.08  # 调整变异率


# def genetic_decimal_to_binary(decimal_genome):
#     binary_genome = ""
#     for i in range(len(decimal_genome)):
#         binary_genome += bin(decimal_genome[i])[2:].zfill(8)
#     return binary_genome
#
#
# def genetic_binary_to_decimal(binary_genome):
#     decimal_genome = []
#     for i in range(0, len(binary_genome), 8):
#         decimal_genome.append(int(binary_genome[i:i + 8], 2))
#     return decimal_genome


def fitness(genome):
    return genome[3]


# 创建种群，其中个体是一个长度为4的列表，前三个元素表示角度，最后一个元素表示适应度
def generate_population(population_size):
    return [([random.randint(0, 160) for _ in range(3)]+[0]) for _ in range(population_size)]


def elitism(population, elite_size=2):
    sorted_population = sorted(population, key=fitness, reverse=True)
    return sorted_population[:elite_size]


def select_parents(population):
    weights = [fitness(genome) for genome in population]
    return random.choices(population, weights=weights, k=2)


def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2


def mutate(genome):
    for i in range(len(genome)):
        if random.random() < MUTATION_RATE:
            genome[i] = random.randint(0, 160)  # Randomly change the gene value


def generate_new_population(population):
    # 精英保留策略
    new_population = elitism(population)
    # 用交叉变异补全种群
    while len(new_population) < POPULATION_SIZE:
        # 十进制处理（可考虑二进制处理）
        parent1, parent2 = select_parents(population)
        child1, child2 = crossover(parent1, parent2)
        mutate(child1)
        mutate(child2)
        new_population.extend([child1, child2])
    return new_population


