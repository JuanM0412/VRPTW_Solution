from solution import solve_instance, euclidean_distance
import os, time
from copy import deepcopy
from output import save_results_to_excel

OUTPUT_FILE = 'Neighborhood_Search/output/VRPTW_JuanManuelGomez_Vecindario4.xlsx'
INSTANCES_DIR = 'instances'


def check_solution(graph, total_distance, new_route, max_vehicle_capacity, original_route, original_capacity, original_times):
    #print('New route:', new_route)
    new_total_distance = 0
    current_vehicle_capacity = max_vehicle_capacity
    total_time = 0  # Tiempo en el que el vehículo sale del depósito (nodo 0)
    arrival_times = [0] # Lista para llevar el tiempo de llegada a cada nodo

    i = 1
    while i < len(new_route) - 1:
        node_id = new_route[i]
        node_demand = graph[node_id][2]

        # Verificar si la capacidad del vehículo es suficiente
        if current_vehicle_capacity - node_demand < 0:
            #print('Capacity exceeded')
            return False, total_distance, original_capacity, original_times
        
        # Calcular la distancia desde el nodo anterior
        previous_node = new_route[i - 1]
        distance = euclidean_distance(graph[previous_node], graph[node_id])
        arrival_time = total_time + distance

       # Verificar si el tiempo de llegada cae dentro de la ventana de tiempo del nodo
        if arrival_time > graph[node_id][4]:
            return False, total_distance, original_capacity, original_times

        # Si llega antes del tiempo de inicio de servicio, debe esperar
        if arrival_time < graph[node_id][3]:
            total_time += (graph[node_id][3] - arrival_time)
            arrival_time = graph[node_id][3]

        # Actualizar el tiempo total y la distancia
        total_time += distance + graph[node_id][5]
        new_total_distance += distance
        current_vehicle_capacity -= node_demand
        arrival_times.append(arrival_time)
        i += 1

    # Verificar si el vehículo puede regresar al depósito a tiempo
    depot_distance = euclidean_distance(graph[new_route[-2]], graph[0])
    total_time += depot_distance
    new_total_distance += depot_distance

    if total_time > graph[0][4]:  # Tiempo límite para regresar al depósito
        #print('Exceeded time limit for returning to depot')
        return False, total_distance, original_capacity, original_times
    
    arrival_times.append(total_time)  # Tiempo de llegada al depósito

    #print('Returning True')
    return True, new_total_distance, current_vehicle_capacity, arrival_times


def insert_node_in_route(graph, route_from, route_to, max_vehicle_capacity, total_distance):
    best_total_distance = total_distance
    best_route_from = deepcopy(route_from)
    best_route_to = deepcopy(route_to)
    best_times_from = deepcopy(route_from[3])
    best_times_to = deepcopy(route_to[3])
    best_capacity_from = route_from[2]
    best_capacity_to = route_to[2]
    improved = False

    nodes_from = route_from[0]
    nodes_to = route_to[0]
    original_distance_from = route_from[4]
    original_distance_to = route_to[4]

    for i in range(1, len(nodes_from) - 1):  # Itera sobre los nodos de la primera ruta
        node = nodes_from[i]
        for j in range(1, len(nodes_to)):  # Prueba todas las posiciones en la segunda ruta
            # Inserta el nodo en la posición j de la segunda ruta
            new_route_from = deepcopy(nodes_from[:i] + nodes_from[i+1:])  # Quitar nodo de la primera ruta
            new_route_to = deepcopy(nodes_to[:j] + [node] + nodes_to[j:])  # Insertar nodo en la segunda ruta

            # Verificar factibilidad de ambas rutas
            factibility_from, new_distance_from, new_capacity_from, new_times_from = check_solution(graph, total_distance, new_route_from, max_vehicle_capacity, route_from, route_from[2], route_from[3])
            factibility_to, new_distance_to, new_capacity_to, new_times_to = check_solution(graph, total_distance, new_route_to, max_vehicle_capacity, route_to, route_to[2], route_to[3])

            if factibility_from and factibility_to:
                new_total_distance = new_distance_from + new_distance_to
                if new_total_distance < (original_distance_from + original_distance_to):
                    # Actualizamos si es una mejor solución
                    improved = True
                    best_total_distance = new_total_distance
                    best_route_from = (new_route_from, route_from[1], new_capacity_from, new_times_from, new_distance_from)
                    best_route_to = (new_route_to, route_to[1], new_capacity_to, new_times_to, new_distance_to)
                    
    return improved, best_route_from, best_route_to, best_total_distance


def insert_nodes(graph, vehicles, total_distance, computation_time, routes, max_vehicle_capacity):
    start_time = time.time()
    for idx1, route1 in enumerate(routes):
        for idx2 in range(idx1 + 1, len(routes)):
            route_list1 = list(routes[idx1])
            route_list2 = list(routes[idx2])

            # Intentar insertar nodos de route1 en route2 y viceversa
            improved1, new_route1, new_route2, new_total_distance1 = insert_node_in_route(graph, route_list1, route_list2, max_vehicle_capacity, total_distance)
            improved2, new_route2, new_route1, new_total_distance2 = insert_node_in_route(graph, route_list2, route_list1, max_vehicle_capacity, total_distance)

            # Si alguna inserción mejora, actualizar las rutas
            if improved1 or improved2:
                routes[idx1] = new_route1
                routes[idx2] = new_route2
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
            graph, vehicles, total_distance, computation_time, routes, vehicle_capacity = solve_instance(instance_path)
            #print('ROUTES:', routes)
            vehicles, total_distance, computation_time, routes, vehicle_capacity = change_position(graph, vehicles, total_distance, computation_time, routes, vehicle_capacity)
            save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity, OUTPUT_FILE)


if __name__ == '__main__':
    main()