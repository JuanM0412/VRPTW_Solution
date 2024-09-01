import math

ROUTE_FILE = 'instances/VRPTW1.txt'


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

    for node_id, attributes in graph.items():
        print(f'Node {node_id}: {attributes}')

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

    return distances


def main():
    graph, vehicle_capacity = parse_file(ROUTE_FILE)
    print(f'Grafo ordenado por el cuarto valor de cada nodo en {ROUTE_FILE}:')
    sorted_nodes = sorted(graph.keys(), key=lambda x: graph[x][3])
    del sorted_nodes[0]

    distances = calculate_distances(graph, 0)

    print(f'Distancias desde el nodo {0}:')
    for node_id, distance in distances:
        print(f'  Nodo {node_id}: {distance:.2f}')

    vehicles = 1
    time = 0
    route = [0]
    visited_nodes = set()
    current_capacity = vehicle_capacity
    total_time = 0
    
    while len(visited_nodes) < len(graph) - 1:
        for node in sorted_nodes:
            if node in visited_nodes:
                continue
            
            current_capacity = current_capacity - graph[node][2]
            if current_capacity < 0:
                route.append(0)
                print(f'Vehicle {vehicles} route {route}')
                vehicles += 1
                route.clear()
                route = [0]
                current_capacity = vehicle_capacity
                time = 0

            new_time = 0
            for distance in distances:
                if distance[0] == node:
                    new_time = distance[1]
                    time = time + distance[1]
                    break

            if time > graph[node][4]:
                time -= new_time
                continue

            while time < graph[node][3]:
                time += 1

            route.append(node)
            visited_nodes.add(node)
            time += graph[node][5]
            total_time += time
            distances = calculate_distances(graph, node)

            if len(visited_nodes) == 24:
                break
        
    print('Total time:', total_time)


if __name__ == '__main__':
    main()