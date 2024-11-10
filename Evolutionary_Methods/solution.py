import math, os, time, openpyxl


def parse_file(filename):
    with open(filename, 'r') as file:
        content = file.readlines()

    first_line = content[0].split()
    n_nodes = int(first_line[0])
    vehicle_capacity = int(first_line[1])

    graph = {}
    for line in content[1:]:
        parts = list(map(int, line.split()))
        node_id = parts[0]
        graph[node_id] = parts[1:]

    return graph, vehicle_capacity


def euclidean_distance(node1, node2):
    x1, y1 = node1[0], node1[1]
    x2, y2 = node2[0], node2[1]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def calculate_distances(graph, current_node_id):
    distances = []
    current_node = graph[current_node_id]

    for node_id in graph:
        if node_id != current_node_id:
            distance = euclidean_distance(current_node, graph[node_id])
            distances.append((node_id, distance))

    distances.sort(key=lambda x: x[1])
    return distances


def constructive(instance_filename):
    graph, vehicle_capacity = parse_file(instance_filename)
    vehicles = 1
    route = [0]
    visited_nodes = set()
    current_capacity = vehicle_capacity
    total_time = 0
    total_distance = 0
    current_node_id = 0
    start_time = time.time()

    routes = []
    arrival_times = [0]  # List to track arrival times at each node
    route_distance = 0  # Distance for the current route

    while len(visited_nodes) < len(graph) - 1:
        distances = calculate_distances(graph, current_node_id)
        found_valid_node = False

        for node_id, distance in distances:
            if node_id in visited_nodes or node_id == 0:
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
            current_capacity -= graph[node_id][2]
            total_time += distance + graph[node_id][5]
            total_distance += distance
            route_distance += distance  # Add to the current route's distance
            current_node_id = node_id
            arrival_times.append(arrival_time)  # Append the arrival time for this node
            found_valid_node = True

            depot_distance = euclidean_distance(graph[current_node_id], graph[0])
            arrival_time_at_depot = total_time + depot_distance
            if arrival_time_at_depot > graph[0][4]:
                visited_nodes.remove(node_id)
                route.pop()
                current_capacity += graph[node_id][2]
                total_time -= (distance + graph[node_id][5])
                total_distance -= distance
                route_distance -= distance  # Subtract from current route's distance
                current_node_id = route[-1]
                arrival_times.pop()  # Remove the last arrival time
                found_valid_node = False
                continue

            break

        if not found_valid_node:
            depot_distance = euclidean_distance(graph[current_node_id], graph[0])
            total_distance += depot_distance
            route_distance += depot_distance  # Add depot distance to current route's distance
            total_time += depot_distance
            route.append(0)
            arrival_times.append(total_time)  # Arrival time at the depot
            routes.append((route[:], total_time, current_capacity, arrival_times[:], route_distance))  # Store route distance
            vehicles += 1
            route = [0]
            arrival_times = [0]  # Reset arrival times for the new vehicle
            current_capacity = vehicle_capacity
            total_time = 0
            route_distance = 0  # Reset route distance for new vehicle
            current_node_id = 0

    if route[-1] != 0:
        depot_distance = euclidean_distance(graph[current_node_id], graph[0])
        total_distance += depot_distance
        route_distance += depot_distance  # Add depot distance to final route's distance
        total_time += depot_distance
        route.append(0)
        arrival_times.append(total_time)  # Final arrival time at depot
        routes.append((route[:], total_time, current_capacity, arrival_times[:], route_distance))

    end_time = time.time()
    computation_time = int((end_time - start_time) * 1000)

    return graph, vehicles, total_distance, computation_time, routes, vehicle_capacity