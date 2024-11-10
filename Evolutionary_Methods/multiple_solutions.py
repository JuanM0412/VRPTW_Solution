import math, os, time, openpyxl, random


def euclidean_distance(node1, node2):
    x1, y1 = node1[0], node1[1]
    x2, y2 = node2[0], node2[1]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calculate_distances(graph, current_node_id, remaining_nodes, alpha):
    distances = []
    current_node = graph[current_node_id]

    for node_id in remaining_nodes:
        if node_id != current_node_id:
            distance = euclidean_distance(current_node, graph[node_id])
            distances.append((node_id, distance))

    distances.sort(key=lambda x: x[1])
    resulting_nodes = int(len(distances) * alpha)

    if resulting_nodes == 0:
        resulting_nodes = 1
        
    return distances[:resulting_nodes]


def solve_instance(graph, vehicle_capacity, alpha):
    remaining_nodes = set(graph.keys())
    vehicles = 1
    route = [0]
    visited_nodes = set()
    current_capacity = vehicle_capacity
    total_time = 0
    total_distance = 0
    current_node_id = 0
    start_time = time.time()

    routes = []
    arrival_times = [0]

    while len(visited_nodes) < len(graph) - 1:
        remaining_nodes.discard(current_node_id)
        distances = calculate_distances(graph, current_node_id, remaining_nodes, alpha)
        random.shuffle(distances)
        found_valid_node = False

        for node_id, distance in distances:
            if node_id in visited_nodes:
                continue

            if current_capacity - graph[node_id][2] < 0:
                continue

            arrival_time = total_time + distance
            if arrival_time > graph[node_id][4]:
                continue

            if arrival_time < graph[node_id][3]:
                total_time += (graph[node_id][3] - arrival_time)
                arrival_time = graph[node_id][3]

            return_to_depot_time = total_time + distance + graph[node_id][5] + euclidean_distance(graph[node_id], graph[0])
            if return_to_depot_time > graph[0][4]:
                continue

            route.append(node_id)
            visited_nodes.add(node_id)
            remaining_nodes.discard(node_id)
            current_capacity -= graph[node_id][2]
            total_time += distance + graph[node_id][5]
            total_distance += distance
            current_node_id = node_id
            found_valid_node = True
            arrival_times.append(arrival_time)

            depot_distance = euclidean_distance(graph[current_node_id], graph[0])
            arrival_time_at_depot = total_time + depot_distance
            if arrival_time_at_depot > graph[0][4]:
                visited_nodes.remove(node_id)
                remaining_nodes.add(node_id)
                route.pop()
                current_capacity += graph[node_id][2]
                total_time -= (distance + graph[node_id][5])
                total_distance -= distance
                current_node_id = route[-1]
                found_valid_node = False
                continue

            break

        if not found_valid_node:
            depot_distance = euclidean_distance(graph[current_node_id], graph[0])
            total_distance += depot_distance
            total_time += depot_distance
            route.append(0)
            arrival_times.append(total_time)
            routes.append((route[:], total_time, current_capacity, arrival_times[:], total_distance))
            vehicles += 1
            route = [0]
            arrival_times = [0]
            current_capacity = vehicle_capacity
            total_time = 0
            current_node_id = 0

    if route[-1] != 0:
        depot_distance = euclidean_distance(graph[current_node_id], graph[0])
        total_distance += depot_distance
        total_time += depot_distance
        route.append(0)
        arrival_times.append(total_time)  # Registro del tiempo de llegada al depósito
        routes.append((route[:], total_time, current_capacity, arrival_times[:], total_distance))

    end_time = time.time()
    computation_time = int((end_time - start_time) * 1000)

    return vehicles, total_distance, computation_time, routes