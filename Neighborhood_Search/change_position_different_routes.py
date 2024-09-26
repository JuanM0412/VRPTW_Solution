from solution import solve_instance, euclidean_distance
import os
from copy import deepcopy
from output import save_results_to_excel

OUTPUT_FILE = 'Neighborhood_Search/output/VRPTW_JuanManuelGomez_Vecindario3.xlsx'
INSTANCES_DIR = 'instances'


def check_solution(graph, total_distance, new_route, max_vehicle_capacity, original_route):
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
    for idx1, route1 in enumerate(routes):
        route_list1 = list(route1)
        nodes_traveled_copy1 = deepcopy(route_list1[0])
        current_route_distance1 = route_list1[4]
        
        for idx2 in range(idx1 + 1, len(routes)):
            route_list2 = list(routes[idx2])
            nodes_traveled_copy2 = deepcopy(route_list2[0])
            current_route_distance2 = route_list2[4]
            flag = True

            for i in range(1, len(nodes_traveled_copy1) - 1):
                for j in range(1, len(nodes_traveled_copy2) - 1):
                    # Intercambiar nodos entre rutas
                    nodes_traveled_copy1[i], nodes_traveled_copy2[j] = nodes_traveled_copy2[j], nodes_traveled_copy1[i]

                    # Verificar factibilidad y distancia para ambas rutas
                    factibility1, new_total_distance1 = check_solution(deepcopy(graph), deepcopy(total_distance), nodes_traveled_copy1, deepcopy(max_vehicle_capacity), route1)
                    factibility2, new_total_distance2 = check_solution(deepcopy(graph), deepcopy(total_distance), nodes_traveled_copy2, deepcopy(max_vehicle_capacity), route_list2)

                    if factibility1 and factibility2:
                        new_total_distance = new_total_distance1 + new_total_distance2
                        if new_total_distance < (current_route_distance1 + current_route_distance2):
                            flag = False
                            print(f'Intercambio entre rutas {idx1} y {idx2}')
                            print(f'DISTANCIAS ANTERIORES: Ruta {idx1}: {current_route_distance1}, Ruta {idx2}: {current_route_distance2}')
                            current_route_distance1 = new_total_distance1
                            current_route_distance2 = new_total_distance2
                            route_list1[4] = current_route_distance1  # Modificar la distancia en la ruta 1
                            route_list2[4] = current_route_distance2  # Modificar la distancia en la ruta 2
                            route_list1[0] = nodes_traveled_copy1  # Actualizar la ruta 1
                            route_list2[0] = nodes_traveled_copy2  # Actualizar la ruta 2
                            print(f'NUEVAS DISTANCIAS: Ruta {idx1}: {current_route_distance1}, Ruta {idx2}: {current_route_distance2}')
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