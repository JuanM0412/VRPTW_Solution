from solution import constructive, euclidean_distance
import os, time
from copy import deepcopy
from output import save_results_to_excel


OUTPUT_FILE = 'Neighborhood_Search/output/VRPTW_JuanManuelGomez_Vecindario1_2.xlsx'
INSTANCES_DIR = 'instances'


def check_solution(graph, total_distance, new_route, max_vehicle_capacity, original_route, original_times):
    new_total_distance = 0
    total_time = 0  # Tiempo total actualizado
    current_vehicle_capacity = max_vehicle_capacity
    arrival_times = [0]  # Lista para llevar el tiempo de llegada a cada nodo

    i = 1
    while i < len(new_route) - 1:
        node_id = new_route[i]
        node_demand = graph[node_id][2]

        # Verificar si la capacidad del vehículo es suficiente
        if current_vehicle_capacity - node_demand < 0:
            #print('Capacity exceeded')
            return False, total_distance, original_times

        # Calcular la distancia desde el nodo anterior
        previous_node = new_route[i - 1]
        distance = euclidean_distance(graph[previous_node], graph[node_id])
        arrival_time = total_time + distance
    
        # Verificar si el tiempo de llegada cae dentro de la ventana de tiempo del nodo
        if arrival_time > graph[node_id][4]:
            return False, total_distance, original_times

        # Si llega antes del tiempo de inicio de servicio, debe esperar
        if arrival_time < graph[node_id][3]:
            total_time += (graph[node_id][3] - arrival_time)
            arrival_time = graph[node_id][3]

        # Actualizar el tiempo de servicio y el tiempo total acumulado
        total_time += distance + graph[node_id][5]
        new_total_distance += distance
        current_vehicle_capacity -= node_demand
        arrival_times.append(arrival_time)  # Registrar el tiempo de llegada actualizado

        i += 1

    # Verificar si el vehículo puede regresar al depósito a tiempo
    depot_distance = euclidean_distance(graph[new_route[-2]], graph[0])
    total_time += depot_distance
    new_total_distance += depot_distance

    if total_time > graph[0][4]:  # Tiempo límite para regresar al depósito
        return False, total_distance, original_times

    arrival_times.append(total_time)  # Tiempo de llegada al depósito
    return True, new_total_distance, arrival_times


def best_improvement(graph, vehicles, total_distance, computation_time, routes, max_vehicle_capacity):
    start_time = time.time()
    for idx, route in enumerate(routes):
        # Convertir la tupla en una lista para modificarla temporalmente
        route_list = list(route)
        nodes_traveled_copy = deepcopy(route_list[0])
        current_route_distance = route_list[4]
        travel_times = deepcopy(route_list[3])
        
        best_total_distance = current_route_distance
        best_route = deepcopy(nodes_traveled_copy)
        best_travel_times = deepcopy(travel_times)
        found_better_solution = False

        i = 1
        while i < len(nodes_traveled_copy) - 1:
            j = i + 1
            while j < len(nodes_traveled_copy) - 1:
                # Intercambiar las posiciones de los nodos
                nodes_traveled_copy[i], nodes_traveled_copy[j] = nodes_traveled_copy[j], nodes_traveled_copy[i]

                # Verificar factibilidad y distancia
                factibility, new_total_distance, possible_travel_times = check_solution(
                    deepcopy(graph), deepcopy(total_distance), nodes_traveled_copy, 
                    deepcopy(max_vehicle_capacity), route, travel_times
                )

                if factibility and new_total_distance < best_total_distance:
                    found_better_solution = True
                    best_total_distance = deepcopy(new_total_distance)
                    best_route = deepcopy(nodes_traveled_copy)
                    best_travel_times = deepcopy(possible_travel_times)

                # Revertir el intercambio para seguir evaluando otras posibilidades
                nodes_traveled_copy[i], nodes_traveled_copy[j] = nodes_traveled_copy[j], nodes_traveled_copy[i]
                j += 1
            i += 1

        # Si encontramos una mejor ruta, la aplicamos
        if found_better_solution:
            #print('Old distance', current_route_distance)
            route_list[0] = best_route
            route_list[3] = best_travel_times
            route_list[4] = best_total_distance
            #print('NEW DISTANCE', best_total_distance)
            routes[idx] = tuple(route_list)

        total_distance = sum(route[4] for route in routes)

    end_time = time.time()
    computation_time += int((end_time - start_time) * 1000)

    return len(routes), total_distance, computation_time, routes, max_vehicle_capacity


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            print(f'Solving instance {instance_path}')
            instance_name = instance_filename.replace('.txt', '')
            graph, vehicles, total_distance, computation_time, routes, vehicle_capacity = constructive(instance_path)
            print('ROUTES:', routes)
            vehicles, total_distance, computation_time, routes, vehicle_capacity = best_improvement(graph, vehicles, total_distance, computation_time, routes, vehicle_capacity)
            save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity, OUTPUT_FILE)


if __name__ == '__main__':
    main()