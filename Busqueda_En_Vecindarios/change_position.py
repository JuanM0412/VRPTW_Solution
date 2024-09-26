from solution import solve_instance, euclidean_distance
import math, os, time
from copy import deepcopy


INSTANCES_DIR = 'instances'
OUTPUT_FILE = 'output/VRPTW_JuanManuelGomez_constructivo.xlsx'


def check_solution(graph, total_distance, computation_time, new_route, max_vehicle_capacity, i_iter, j_iter, travel_times):
    #print('New route:', new_route)
    new_total_distance = 0
    new_total_time = 0  # Variable para mantener el tiempo total actualizado
    current_vehicle_capacity = max_vehicle_capacity
    current_time = 0  # Tiempo en el que el vehículo sale del depósito (nodo 0)

    i = 1
    while i < len(new_route) - 1:
        node_id = new_route[i]
        node_demand = graph[node_id][2]

        # Verificar si la capacidad del vehículo es suficiente
        if current_vehicle_capacity - node_demand < 0:
            print('Capacity exceeded')
            return False, total_distance

        # Calcular la distancia desde el nodo anterior
        previous_node = new_route[i - 1]
        distance_to_current_node = euclidean_distance(graph[previous_node], graph[node_id])

        # Actualizar el tiempo de llegada
        current_time += distance_to_current_node

        # Verificar si el tiempo de llegada cae dentro de la ventana de tiempo del nodo
        earliest_time, latest_time = graph[node_id][3], graph[node_id][4]
        if current_time > latest_time:
            #print(f'Arrived too late to node {node_id}')
            return False, total_distance

        # Si el vehículo llega antes del tiempo de inicio de servicio, debe esperar
        if current_time < earliest_time:
            current_time = earliest_time

        # Actualizar el tiempo total y la distancia
        service_time = graph[node_id][5]
        current_time += service_time
        new_total_distance += distance_to_current_node
        current_vehicle_capacity -= node_demand
        i += 1

    # Verificar si el vehículo puede regresar al depósito a tiempo
    depot_distance = euclidean_distance(graph[new_route[-2]], graph[0])
    current_time += depot_distance
    new_total_distance += depot_distance

    if current_time > graph[0][4]:  # Tiempo límite para regresar al depósito
        #print('Exceeded time limit for returning to depot')
        return False, total_distance

    #print('Returning True')
    return True, new_total_distance


def change_position(graph, vehicles, total_distance, computation_time, routes, max_vehicle_capacity):
    for route in routes:
        nodes_traveled_copy = deepcopy(route[0])
        current_route_distance = route[4]
        travel_times = route[3]
        i = 1
        while i < len(nodes_traveled_copy) - 1:
            j = i + 1
            while j < len(nodes_traveled_copy) - 1:
                factibility, new_total_distance = check_solution(deepcopy(graph), deepcopy(total_distance), computation_time, nodes_traveled_copy, deepcopy(max_vehicle_capacity), i, j, travel_times)
                #print('Old distance', current_route_distance)
                if factibility and new_total_distance < current_route_distance:
                    print('Old distance', current_route_distance)
                    current_route_distance = new_total_distance
                    print('NEW DISTANCE', current_route_distance)
                    #print('Change position')
                    i = 1
                    break
                    
                nodes_traveled_copy[i], nodes_traveled_copy[j] = nodes_traveled_copy[j], nodes_traveled_copy[i]
                #print('Original route:', nodes_traveled)
                #print(f'New route: {nodes_traveled_copy}')
                j += 1
            i += 1


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            print(f'Solving instance {instance_path}')
            graph, vehicles, total_distance, computation_time, routes, vehicle_capacity = solve_instance(instance_path)
            #print('ROUTES:', routes)
            change_position(graph, vehicles, total_distance, computation_time, routes, vehicle_capacity)


if __name__ == '__main__':
    main()