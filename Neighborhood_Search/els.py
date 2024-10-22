import random
import time
from copy import deepcopy
from multiple_solutions import solve_instance
from output import save_results_to_excel
from change_position_different_routes import different_routes, check_solution
from solution import constructive
from vnd import vnd
import os

# Parámetros para el algoritmo
TABU_TENURE = 10  # Tiempo de vida de la lista tabú
MAX_ITERATIONS = 5  # Número máximo de iteraciones del multi-start

OUTPUT_FILE = 'Neighborhood_Search/output/VRPTW_JuanManuelGomez_ELS_MultiStart_Test5.xlsx'
INSTANCES_DIR = 'instances'
TIME_LIMIT = [50000, 50000, 50000, 50000, 50000, 50000, 200000, 200000, 200000, 200000, 200000, 200000, 750000, 750000, 750000, 750000, 750000, 750000]

class TabuList:
    def __init__(self, tenure):
        self.tabu_list = []
        self.tenure = tenure

    def add_solution(self, solution):
        self.tabu_list.append(deepcopy(solution))
        if len(self.tabu_list) > self.tenure:
            self.tabu_list.pop(0)

    def is_tabu(self, solution):
        return solution in self.tabu_list


def perturb_solution(graph, solution, max_vehicle_capacity):
    """ Perturba la solución removiendo nodos de las rutas y creando nuevas rutas """
    perturbed_solution = deepcopy(solution)
    num_nodes_to_move = 3  # Número de nodos que se moverán a nuevas rutas
    nodes_to_move = []

    # Seleccionar nodos de manera aleatoria de las rutas
    for route in perturbed_solution[3]:
        route = list(route)  # Convertir toda la tupla 'route' a lista
        route[0] = list(route[0])  # Convertir los nodos de la ruta en lista si es necesario
        if len(route[0]) > 1:  # Solo si la ruta tiene nodos para mover
            nodes_to_move.extend(random.sample(route[0][1:-1], min(num_nodes_to_move, len(route[0]) - 2)))

    # Remover los nodos seleccionados de las rutas originales
    for route in perturbed_solution[3]:
        route = list(route)  # Convertir toda la tupla 'route' a lista
        route[0] = [node for node in route[0] if node not in nodes_to_move]

    # Crear nuevas rutas para los nodos seleccionados
    for node in nodes_to_move:
        new_route = [[0, node, 0], 0, max_vehicle_capacity - graph[node][2], [0], 0]  # Inicializar ruta con capacidad y tiempos
        # Calcular distancia y tiempos para la nueva ruta
        factibility, distance, remaining_capacity, times = check_solution(graph, 0, new_route[0], max_vehicle_capacity, new_route, new_route[2], new_route[3])
        
        if factibility:
            new_route[1] = distance  # Actualizar la distancia de la ruta
            new_route[2] = remaining_capacity  # Actualizar la capacidad restante
            new_route[3] = times  # Actualizar los tiempos
            new_route[4] = distance  # Guardar la distancia total
            perturbed_solution[3].append(new_route)

    return perturbed_solution


def els(graph, best_solution, vehicle_capacity, instance_number, tabu_tenure=TABU_TENURE, max_iterations=MAX_ITERATIONS):
    tabu_list = TabuList(tabu_tenure)
    start_time = time.time()

    for iteration in range(max_iterations):
        current_solution = deepcopy(best_solution)
        
        # Verificar el tiempo límite
        if (time.time() - start_time) * 1000 > TIME_LIMIT[instance_number - 1]:
            print('Time limit exceeded')
            break

        # Perturbar la solución actual
        perturbed_solution = vnd(graph, current_solution[0], current_solution[1], current_solution[2], current_solution[3], vehicle_capacity, instance_number)

        # Aplicar búsqueda local usando el método `different_routes`
        improved_solution = different_routes(graph, perturbed_solution[0], perturbed_solution[1], 
                                             perturbed_solution[2], perturbed_solution[3], vehicle_capacity)

        # Revisar si la nueva solución es tabú
        if not tabu_list.is_tabu(improved_solution[3]):
            tabu_list.add_solution(improved_solution[3])

            # Si la nueva solución es mejor, actualizar la mejor solución
            vehicles, total_distance, computation_time, routes, *other_values = improved_solution
            if total_distance < best_solution[1]:
                best_solution = improved_solution

    computation_time = int((time.time() - start_time) * 1000)
    return best_solution, computation_time


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            instance_name = instance_filename.replace('.txt', '')
            instance_number = int(instance_name[5::])  # Obtener el número de instancia

            # Generar soluciones iniciales usando diferentes métodos
            initial_solutions = []
            
            # Primera solución inicial con GRASP
            graph, vehicles, total_distance, computation_time, routes, vehicle_capacity = solve_instance(instance_path, 0.1)
            initial_solutions.append((vehicles, total_distance, computation_time, routes))
            
            # Segunda solución inicial con el método 'constructive'
            graph, vehicles, total_distance, computation_time, routes, vehicle_capacity = constructive(instance_path)
            initial_solutions.append((vehicles, total_distance, computation_time, routes))
            
            # Tercera solución inicial mejorada con 'different_routes'
            vehicles, total_distance, computation_time, routes, vehicle_capacity = different_routes(graph, vehicles, total_distance, computation_time, routes, vehicle_capacity)
            initial_solutions.append((vehicles, total_distance, computation_time, routes))

            # Aplicar ELS a cada solución inicial y guardar los resultados
            best_solutions = []
            for solution in initial_solutions:
                best_solution, computation_time = els(graph, solution, vehicle_capacity, instance_number)
                best_solutions.append(best_solution)
            
            # Seleccionar la mejor solución después de aplicar ELS
            final_best_solution = min(best_solutions, key=lambda x: x[1])  # Comparar por la distancia total

            # Guardar los resultados finales
            vehicles, total_distance, computation_time, routes, *other_values = final_best_solution
            save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity, OUTPUT_FILE)

if __name__ == '__main__':
    main()
