import math, os, time, openpyxl, random


INSTANCES_DIR = 'instances'
OUTPUT_FILE = 'output/VRPTW_JuanManuelGomez_GRASP1.xlsx'


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


def calculate_distances(graph, current_node_id, remaining_nodes, k):
    distances = []
    current_node = graph[current_node_id]

    for node_id in remaining_nodes:
        if node_id != current_node_id:
            distance = euclidean_distance(current_node, graph[node_id])
            distances.append((node_id, distance))

    distances.sort(key=lambda x: x[1])
    return distances[:k]


def solve_instance(instance_filename):
    graph, vehicle_capacity = parse_file(instance_filename)
    remaining_nodes = set(graph.keys())
    vehicles = 1
    route = [0]
    k = 3
    visited_nodes = set()
    current_capacity = vehicle_capacity
    total_time = 0
    total_distance = 0
    current_node_id = 0
    start_time = time.time()

    routes = []

    while len(visited_nodes) < len(graph) - 1:
        remaining_nodes.discard(current_node_id)
        distances = calculate_distances(graph, current_node_id, remaining_nodes, k)
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
            routes.append((route[:], total_time, current_capacity))
            vehicles += 1
            route = [0]
            current_capacity = vehicle_capacity
            total_time = 0
            current_node_id = 0

    if route[-1] != 0:
        depot_distance = euclidean_distance(graph[current_node_id], graph[0])
        total_distance += depot_distance
        total_time += depot_distance
        route.append(0)
        routes.append((route[:], total_time, current_capacity))

    end_time = time.time()
    computation_time = int((end_time - start_time) * 1000)

    return vehicles, total_distance, computation_time, routes, vehicle_capacity


def save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity):
    if not os.path.exists(OUTPUT_FILE):
        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)
    else:
        workbook = openpyxl.load_workbook(OUTPUT_FILE)

    sheet = workbook.create_sheet(instance_name)

    sheet.append([vehicles, round(total_distance, 3), computation_time])

    for route, time, capacity in routes:
        sheet.append([len(route) - 2] + route + [round(time, 3), vehicle_capacity - capacity])

    workbook.save(OUTPUT_FILE)


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            instance_name = instance_filename.replace('.txt', '')
            vehicles, total_distance, computation_time, routes, vehicle_capacity = solve_instance(instance_path)
            save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity)


if __name__ == '__main__':
    main()