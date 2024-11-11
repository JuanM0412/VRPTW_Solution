import os
from copy import deepcopy
import random
import multiple_solutions as ms
from solution import euclidean_distance
import output
import time
from insert_nodes import insert_nodes


POPULATION_SIZE = 100
NUM_GENERATIONS = 50
NUM_CHILDREN = 50
MUTATION_RATE = 0.2
INSTANCES_DIR = "../instances"
OUTPUT_FILE = "/home/juan/University/Heurística/VRPTW/Evolutionary_Methods/output/VRPTW_JuanManuelGomez_GA+LS_100_50_50_02.xlsx"


CROSSOVER_RATE = 0.75
TIME_LIMIT = [50000, 50000, 50000, 50000, 50000, 50000, 200000, 200000, 200000, 200000, 200000, 200000, 750000, 750000, 750000, 750000, 750000, 750000]


def check_solution(graph, total_distance, new_route, max_vehicle_capacity, original_route, original_times):
    new_total_distance = 0
    total_time = 0
    current_vehicle_capacity = max_vehicle_capacity
    arrival_times = [0]

    i = 1
    while i < len(new_route) - 1:
        node_id = new_route[i]
        node_demand = graph[node_id][2]

        if current_vehicle_capacity - node_demand < 0:
            return False, total_distance, original_times, current_vehicle_capacity, new_total_distance

        previous_node = new_route[i - 1]
        distance = euclidean_distance(graph[previous_node], graph[node_id])
        arrival_time = total_time + distance

        if arrival_time > graph[node_id][4]:
            return False, total_distance, original_times, current_vehicle_capacity, new_total_distance

        if arrival_time < graph[node_id][3]:
            total_time += (graph[node_id][3] - arrival_time)
            arrival_time = graph[node_id][3]

        total_time += distance + graph[node_id][5]
        new_total_distance += distance
        current_vehicle_capacity -= node_demand
        arrival_times.append(arrival_time)
        i += 1

    depot_distance = euclidean_distance(graph[new_route[-2]], graph[0])
    total_time += depot_distance
    new_total_distance += depot_distance

    if total_time > graph[0][4]:
        return False, total_distance, original_times, current_vehicle_capacity, new_total_distance

    arrival_times.append(total_time)
    return True, new_total_distance, arrival_times, current_vehicle_capacity, new_total_distance


def fitness(solution):
    total_distance = solution[1]
    return total_distance


def initialize_population(graph, vehicle_capacity):
    population = []
    for _ in range(POPULATION_SIZE):
        alpha = random.uniform(0.1, 0.3)
        solution = ms.solve_instance(graph, vehicle_capacity, alpha)
        vehicles, total_distance, computation_time, routes = solution
        population.append((vehicles, total_distance, computation_time, routes, vehicle_capacity))

    return population


def selection(population):
    top_10_individuals = sorted(population, key=lambda sol: fitness(sol))[:10]
    
    parent1, parent2 = random.sample(top_10_individuals, 2)
    return parent1, parent2


def route_based_crossover(parent1, parent2, graph, vehicle_capacity, instance_number):
    solution1, solution2 = parent1, parent2
    #print(f"parent1 = {parent1}")
    #print(f"parent2 = {parent2}")
    _, _, _, routes1, _ = solution1
    _, _, _, routes2, _ = solution2

    selected_routes = random.sample(routes1, k=min(len(routes1), 2))
    selected_nodes = {node for route in selected_routes for node in route[0]}
    child_routes = []
    
    remaining_routes = [[node for node in route[0] if node not in selected_nodes] for route in routes2]
    remaining_routes = [route for route in remaining_routes if route]  # Eliminar rutas vacías
    
    for route in remaining_routes:
        if route:
            route = [0] + route + [0]
            is_valid, new_total_distance, arrival_times, remaining_capacity, route_distance = check_solution(
                graph, 0, route, vehicle_capacity, [], []
            )
            if is_valid:
                child_routes.append((route, new_total_distance, remaining_capacity, arrival_times, route_distance))

    assigned_nodes = {node for route in child_routes for node in route[0]}
    unassigned_nodes = set(range(1, len(graph))) - assigned_nodes
    for node in unassigned_nodes:
        new_route = [0, node, 0]
        is_valid, new_total_distance, arrival_times, remaining_capacity, route_distance = check_solution(
            graph, 0, new_route, vehicle_capacity, [], []
        )
        if is_valid:
            #print("arrival_times: ", arrival_times)
            child_routes.append((new_route, new_total_distance, remaining_capacity, arrival_times, route_distance))

    total_distance = sum(route[1] for route in child_routes)
    vehicles = len(child_routes)
    computation_time = 0

    child_routes = (vehicles, total_distance, computation_time, child_routes, vehicle_capacity)

    improved_child_solution = insert_nodes(graph, vehicles, total_distance, computation_time, child_routes[3], vehicle_capacity)
    #print(f"child_routes = {child_routes}")
    #print(f"improved_child_solution = {improved_child_solution}")
    #print("Parents: ", parent1)
    #print("Child: ", fitness(child_routes))
    #print("Minimum of parents: ", min(fitness(parent1), fitness(parent2)))
    return improved_child_solution if fitness(improved_child_solution) < min(fitness(parent1), fitness(parent2)) else min(parent1, parent2, key=lambda p: fitness(p))


def mutate(solution, graph, vehicle_capacity, instance_number):
    #print("Solution: ", solution)
    (vehicles, total_distance, computation_time, routes, vehicle_capacity) = deepcopy(solution)

    route_idx = random.randint(0, len(routes) - 1)
    route = routes[route_idx]
    
    if len(route[0]) <= 3:
        return solution
    
    node_idx = random.randint(1, len(route[0]) - 2)
    node_to_relocate = route[0][node_idx]
    
    new_route = deepcopy(route[0][:node_idx] + route[0][node_idx + 1:])
    
    is_valid, new_distance, remaining_capacity, arrival_times, route_distance = check_solution(
        graph, 0, new_route, vehicle_capacity, route, route[3]
    )

    #print("arrival_times: ", arrival_times)
    
    if not is_valid:
        return solution 
    
    target_route_idx = random.choice([i for i in range(len(routes)) if i != route_idx])
    target_route = routes[target_route_idx]
    
    insertion_pos = random.randint(1, len(target_route[0]) - 1)
    new_target_route = deepcopy(target_route[0][:insertion_pos] + [node_to_relocate] + target_route[0][insertion_pos:])
    
    is_valid_target, new_target_distance, remaining_target_capacity, target_times, target_route_distance = check_solution(
        graph, 0, new_target_route, vehicle_capacity, target_route, target_route[3]
    )

    #print("target_times: ", target_times)
    
    if is_valid and is_valid_target:
        #print("Mutation applied")
        #print("target_times: ", target_times)
        #print("arrival_times: ", arrival_times)
        new_routes = deepcopy(routes)
        new_routes[route_idx] = (new_route, new_distance, remaining_capacity, arrival_times, route_distance)
        new_routes[target_route_idx] = (new_target_route, new_target_distance, remaining_target_capacity, target_times, target_route_distance)
        
        new_total_distance = sum(route[1] for route in new_routes if len(route) > 1)
        mutated_solution = (vehicles, new_total_distance, computation_time, new_routes, vehicle_capacity)
        mutated_solution = insert_nodes(graph, vehicles, total_distance, computation_time, mutated_solution[3], vehicle_capacity)
        return mutated_solution

    return solution


def genetic_algorithm(graph, vehicle_capacity, instance_number):
    population = initialize_population(graph, vehicle_capacity)
    best_solution = min(population, key=lambda sol: fitness(sol))

    print(f"Distancia inicial = {fitness(best_solution)}")

    start_time = time.time()
    computation_time = 0
    #print("Initial solution: ", best_solution)

    for generation in range(NUM_GENERATIONS):
        new_population = []

        elapsed_time = (time.time() - start_time) * 1000

        if elapsed_time > TIME_LIMIT[instance_number - 1]:
            print('Límite de tiempo superado')
            computation_time += int(elapsed_time)
            current_best = min(population, key=lambda sol: fitness(sol))

            if fitness(current_best) < fitness(best_solution):
                best_solution = current_best

            return best_solution, TIME_LIMIT[instance_number - 1]
        
        for _ in range(NUM_CHILDREN):
            parent1, parent2 = selection(population)
            #print("Parents: ", parent1, parent2)

            """if random.random() < CROSSOVER_RATE:
                child = route_based_crossover(parent1, parent2, graph, vehicle_capacity, instance_number) # Cambia la estructura de la solución
            else:
                child = parent1"""

            child = route_based_crossover(parent1, parent2, graph, vehicle_capacity, instance_number)

            if random.random() < MUTATION_RATE:
                #print(child)
                child = mutate(child, graph, vehicle_capacity, instance_number)

            new_population.append(child)

        population = new_population
        current_best = min(population, key=lambda sol: fitness(sol))

        if fitness(current_best) < fitness(best_solution):
            best_solution = current_best

        #print(f"Generación {generation + 1}: Mejor distancia = {fitness(best_solution)}")
        end_time = time.time()
        computation_time += int((end_time - start_time) * 1000)

    return best_solution, computation_time


def load_instance(filename):
    with open(filename, 'r') as file:
        content = file.readlines()

    first_line = content[0].split()
    vehicle_capacity = int(first_line[1])
    graph = {int(line.split()[0]): list(map(int, line.split()[1:])) for line in content[1:]}
    return graph, vehicle_capacity


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            print(f'Solving instance {instance_path}')
            
            graph, vehicle_capacity = load_instance(instance_path)
            instance_name = instance_filename.replace('.txt', '')
            instance_number = int(instance_name[5::])
            best_solution, final_time = genetic_algorithm(graph, vehicle_capacity, instance_number)
            vehicles, total_distance, computation_time, routes, vehicle_capacity = best_solution
            print("Best solution: ", fitness(best_solution))
            output.save_results_to_excel(instance_filename, vehicles, total_distance, final_time, routes, vehicle_capacity, OUTPUT_FILE)
            print(f'Instance {instance_filename} solved.\n')


if __name__ == '__main__':
    main()