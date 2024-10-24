from solution import euclidean_distance
import os, time
from copy import deepcopy

OUTPUT_FILE = 'Neighborhood_Search/output/VRPTW_JuanManuelGomez_Vecindario3.xlsx'
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


def perturb_solution(graph, vehicles, total_distance, computation_time, routes, max_vehicle_capacity):
    start_time = time.time()
    for idx1, route1 in enumerate(routes):
        route_list1 = list(route1)
        capacity_route1 = route_list1[2]
        nodes_traveled_copy1 = deepcopy(route_list1[0])
        travel_times1 = deepcopy(route_list1[3])
        current_route_distance1 = route_list1[4]
        
        for idx2 in range(idx1 + 1, len(routes)):
            route_list2 = list(routes[idx2])
            nodes_traveled_copy2 = deepcopy(route_list2[0])
            current_route_distance2 = route_list2[4]
            travel_times2 = deepcopy(route_list2[3])
            capacity_route2 = route_list2[2]
            flag = True

            for i in range(1, len(nodes_traveled_copy1) - 1):
                for j in range(1, len(nodes_traveled_copy2) - 1):
                    # Intercambiar nodos entre rutas
                    nodes_traveled_copy1[i], nodes_traveled_copy2[j] = nodes_traveled_copy2[j], nodes_traveled_copy1[i]

                    # Verificar factibilidad y distancia para ambas rutas
                    factibility1, new_total_distance1, new_vehicle_capacity1, possible_times1 = check_solution(deepcopy(graph), deepcopy(total_distance), nodes_traveled_copy1, deepcopy(max_vehicle_capacity), route1, capacity_route1, travel_times1)
                    factibility2, new_total_distance2, new_vehicle_capacity2, possible_times2 = check_solution(deepcopy(graph), deepcopy(total_distance), nodes_traveled_copy2, deepcopy(max_vehicle_capacity), route_list2, capacity_route2, travel_times2)

                    if factibility1 and factibility2:
                        new_total_distance = new_total_distance1 + new_total_distance2
                        flag = False
                        current_route_distance1 = deepcopy(new_total_distance1)
                        current_route_distance2 = deepcopy(new_total_distance2)
                        route_list1[4] = deepcopy(current_route_distance1)  # Modificar la distancia en la ruta 1
                        route_list2[4] = deepcopy(current_route_distance2)  # Modificar la distancia en la ruta 2
                        route_list1[0] = deepcopy(nodes_traveled_copy1)  # Actualizar la ruta 1
                        route_list2[0] = deepcopy(nodes_traveled_copy2)  # Actualizar la ruta 2
                        route_list1[2] = deepcopy(new_vehicle_capacity1) # Actualizar la capacidad ruta 1
                        route_list2[2] = deepcopy(new_vehicle_capacity2) # Actualizar la capacidad ruta 2
                        route_list1[3] = deepcopy(possible_times1)
                        route_list2[3] = deepcopy(possible_times2)
                        break

                    # Revertir si no es factible
                    nodes_traveled_copy1[i], nodes_traveled_copy2[j] = nodes_traveled_copy2[j], nodes_traveled_copy1[i]

                if not flag:
                    break

            # Actualizar las rutas después del intercambio
            routes[idx1] = tuple(route_list1)
            routes[idx2] = tuple(route_list2)

        # Recalcular la distancia total
        total_distance = sum(route[4] for route in routes)

    end_time = time.time()
    computation_time += int((end_time - start_time) * 1000)

    return len(routes), total_distance, computation_time, routes, max_vehicle_capacity