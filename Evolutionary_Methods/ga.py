import os
from copy import deepcopy
import random
import multiple_solutions as ms
from solution import euclidean_distance
import output
import time
from change_position_same_route import change_position
from change_position_different_routes import different_routes

# Parámetros del Algoritmo Genético
POPULATION_SIZE = 500
NUM_GENERATIONS = 100
NUM_CHILDREN = 75
MUTATION_RATE = 0.4
INSTANCES_DIR = "../instances"
OUTPUT_FILE = "/home/juan/University/Heurística/VRPTW/Evolutionary_Methods/output/VRPTW_JuanManuelGomez_GA_500_100_75_04.xlsx"


CROSSOVER_RATE = 0.75
TIME_LIMIT = [50000, 50000, 50000, 50000, 50000, 50000, 200000, 200000, 200000, 200000, 200000, 200000, 750000, 750000, 750000, 750000, 750000, 750000]


def check_solution(graph, total_distance, new_route, max_vehicle_capacity, original_route, original_times):
    """Verifica la factibilidad de una ruta y actualiza la distancia, los tiempos y la capacidad."""
    new_total_distance = 0
    total_time = 0
    current_vehicle_capacity = max_vehicle_capacity
    arrival_times = [0]  # Inicializa con tiempo 0 en el depósito

    i = 1
    while i < len(new_route) - 1:
        node_id = new_route[i]
        node_demand = graph[node_id][2]

        # Verificar si la capacidad del vehículo es suficiente
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
    """
    Devuelve el fitness de la solución en función de la distancia total recorrida.
    La solución completa tiene cinco valores: vehículos, distancia total, tiempo de cálculo,
    rutas, y capacidad restante.
    """
    total_distance = solution[1]  # `total_distance` es el segundo elemento en `solution`
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
    """
    Selecciona dos padres de manera aleatoria entre los 10 mejores individuos de la población.
    """
    # Seleccionar los 10 mejores individuos basados en su fitness
    top_10_individuals = sorted(population, key=lambda sol: fitness(sol))[:10]
    
    # Seleccionar aleatoriamente dos padres entre los mejores 10
    parent1, parent2 = random.sample(top_10_individuals, 2)
    return parent1, parent2


def route_based_crossover(parent1, parent2, graph, vehicle_capacity, instance_number):
    solution1, solution2 = parent1, parent2
    #print(f"parent1 = {parent1}")
    #print(f"parent2 = {parent2}")
    _, _, _, routes1, _ = solution1
    _, _, _, routes2, _ = solution2

    # Selección de algunas rutas de los padres
    selected_routes = random.sample(routes1, k=min(len(routes1), 2))
    selected_nodes = {node for route in selected_routes for node in route[0]}
    child_routes = []
    
    # Generación de rutas restantes sin nodos duplicados
    remaining_routes = [[node for node in route[0] if node not in selected_nodes] for route in routes2]
    remaining_routes = [route for route in remaining_routes if route]  # Eliminar rutas vacías
    
    for route in remaining_routes:
        if route:  # Verificar que la ruta no esté vacía
            route = [0] + route + [0]
            is_valid, new_total_distance, arrival_times, remaining_capacity, route_distance = check_solution(
                graph, 0, route, vehicle_capacity, [], []
            )
            if is_valid:
                child_routes.append((route, new_total_distance, remaining_capacity, arrival_times, route_distance))

    # Asignar nodos que aún no tienen ruta
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

    # Recalcular la distancia total y el número de vehículos para la solución generada
    total_distance = sum(route[1] for route in child_routes)
    vehicles = len(child_routes)
    computation_time = 0

    child_routes = (vehicles, total_distance, computation_time, child_routes, vehicle_capacity)

    # Aplicar insert_nodes en el hijo generado
    # improved_child_solution = insert_nodes(graph, vehicles, total_distance, computation_time, child_routes[3], vehicle_capacity)
    #print(f"child_routes = {child_routes}")
    #print(f"improved_child_solution = {improved_child_solution}")
    #print("Parents: ", parent1)
    #print("Child: ", fitness(child_routes))
    #print("Minimum of parents: ", min(fitness(parent1), fitness(parent2)))
    # Devolver el mejor hijo
    return child_routes if fitness(child_routes) < min(fitness(parent1), fitness(parent2)) else min(parent1, parent2, key=lambda p: fitness(p))


def mutate(solution, graph, vehicle_capacity, instance_number):
    #print("Solution: ", solution)
    vehicles, total_distance, computation_time, routes, vehicle_capacity = different_routes(graph, solution[0], solution[1], solution[2], solution[3], vehicle_capacity)
    
    new_solution = (vehicles, total_distance, computation_time, routes, vehicle_capacity)
    
    return new_solution


def genetic_algorithm(graph, vehicle_capacity, instance_number):
    population = initialize_population(graph, vehicle_capacity)
    best_solution = min(population, key=lambda sol: fitness(sol))

    print(f"Distancia inicial = {fitness(best_solution)}")

    start_time = time.time()
    computation_time = 0
    #print("Initial solution: ", best_solution)

    for generation in range(NUM_GENERATIONS):
        new_population = []

        elapsed_time = (time.time() - start_time) * 1000  # Convertir a milisegundos

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
    """Carga la instancia desde un archivo."""
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