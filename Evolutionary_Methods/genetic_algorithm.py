import os
from copy import deepcopy
import random
import multiple_solutions as ms
from solution import euclidean_distance
import output
import time
from insert_nodes import insert_nodes

# Parámetros del Algoritmo Genético
POPULATION_SIZE = 50
NUM_GENERATIONS = 100
CROSSOVER_RATE = 0.75
MUTATION_RATE = 0.1
INSTANCES_DIR = "instances"
OUTPUT_FILE = "Evolutionary_Methods/output/VRPTW_JuanManuelGomez_GA_100_50_095_045.xlsx"


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
        population.append(((vehicles, total_distance, computation_time, routes), alpha))

    return population


def selection(population):
    tournament_size = 10
    parents = random.sample(population, tournament_size)
    parents.sort(key=lambda sol: fitness(sol[0]))
    return parents[0], parents[1]


def route_based_crossover(parent1, parent2, graph, vehicle_capacity, instance_number):
    (solution1, alpha1), (solution2, alpha2) = parent1, parent2
    _, _, _, routes1 = solution1
    _, _, _, routes2 = solution2

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
            child_routes.append((new_route, new_total_distance, remaining_capacity, arrival_times, route_distance))

    # Recalcular la distancia total y el número de vehículos para la solución generada
    total_distance = sum(route[1] for route in child_routes)
    vehicles = len(child_routes)
    computation_time = 0

    # Aplicar insert_nodes en el hijo generado
    improved_child_solution = insert_nodes(graph, vehicles, total_distance, computation_time, child_routes, vehicle_capacity)
    print(f"improved_child_solution = {improved_child_solution[1]}")
    #print("Parents: ", parent1)
    print("Minimum of parents: ", min(fitness(parent1[0]), fitness(parent2[0])))
    # Devolver el mejor hijo
    return improved_child_solution if fitness(improved_child_solution) < min(fitness(parent1[0]), fitness(parent2[0])) else min(parent1[0], parent2[0], key=lambda p: fitness(p))


def mutate(solution, graph, vehicle_capacity, instance_number):
    print("Solution: ", solution)
    (vehicles, total_distance, computation_time, routes), alpha = solution

    # Elegir aleatoriamente una ruta y un nodo de esa ruta para reubicar
    route_idx = random.randint(0, len(routes) - 1)
    route = routes[route_idx]
    
    if len(route[0]) <= 3:  # Si la ruta tiene solo un nodo aparte del depósito, no se puede reubicar
        return solution
    
    # Seleccionar un nodo aleatorio en la ruta para reubicar (excluyendo el depósito)
    node_idx = random.randint(1, len(route[0]) - 2)
    node_to_relocate = route[0][node_idx]
    
    # Eliminar el nodo de la ruta original
    new_route = deepcopy(route[0][:node_idx] + route[0][node_idx + 1:])
    
    # Verificar factibilidad de la ruta sin el nodo reubicado
    is_valid, new_distance, remaining_capacity, arrival_times, route_distance = check_solution(
        graph, 0, new_route, vehicle_capacity, route, route[3]
    )
    
    if not is_valid:
        return solution  # Si la ruta sin el nodo no es válida, retornar la solución sin cambios
    
    # Elegir aleatoriamente una ruta de destino (puede ser la misma ruta u otra)
    target_route_idx = random.choice([i for i in range(len(routes)) if i != route_idx])
    target_route = routes[target_route_idx]
    
    # Probar a insertar el nodo en una posición aleatoria de la ruta destino
    insertion_pos = random.randint(1, len(target_route[0]) - 1)
    new_target_route = deepcopy(target_route[0][:insertion_pos] + [node_to_relocate] + target_route[0][insertion_pos:])
    
    # Verificar factibilidad de la ruta con el nodo insertado
    is_valid_target, new_target_distance, remaining_target_capacity, target_times, target_route_distance = check_solution(
        graph, 0, new_target_route, vehicle_capacity, target_route, target_route[3]
    )
    
    # Si ambas rutas son válidas con las modificaciones, aplicamos los cambios
    if is_valid and is_valid_target:
        new_routes = deepcopy(routes)
        new_routes[route_idx] = (new_route, new_distance, remaining_capacity, arrival_times, route_distance)
        new_routes[target_route_idx] = (new_target_route, new_target_distance, remaining_target_capacity, target_times, target_route_distance)
        
        # Recalcular la distancia total y retornar la solución mutada
        new_total_distance = sum(route[1] for route in new_routes if len(route) > 1)
        mutated_solution = (vehicles, new_total_distance, computation_time, new_routes), alpha
        return mutated_solution

    # Si no es factible, retornar la solución original
    return solution


def genetic_algorithm(graph, vehicle_capacity, instance_number):
    population = initialize_population(graph, vehicle_capacity)
    best_solution = min(population, key=lambda sol: fitness(sol[0]))
    print(f"Distancia inicial = {fitness(best_solution[0])}")

    for generation in range(NUM_GENERATIONS):
        new_population = []
        for _ in range(POPULATION_SIZE // 2):
            parent1, parent2 = selection(population)

            if random.random() < CROSSOVER_RATE:
                child = route_based_crossover(parent1, parent2, graph, vehicle_capacity, instance_number)
            else:
                child = parent1

            if random.random() < MUTATION_RATE:
                child = mutate(child, graph, vehicle_capacity, instance_number)

            new_population.append(child)

        population = new_population
        current_best = min(population, key=lambda sol: fitness(sol[0]))
        if fitness(current_best[0]) < fitness(best_solution[0]):
            best_solution = current_best

        print(f"Generación {generation + 1}: Mejor distancia = {fitness(best_solution[0])}")

    return best_solution


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
            best_solution = genetic_algorithm(graph, vehicle_capacity, instance_number)
            vehicles, total_distance, computation_time, routes = best_solution
            output.save_results_to_excel(instance_filename, vehicles, total_distance, computation_time, routes, vehicle_capacity, OUTPUT_FILE)
            print(f'Instance {instance_filename} solved.\n')


if __name__ == '__main__':
    main()