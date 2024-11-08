import random
from solution import euclidean_distance  # Assuming 'euclidean_distance' function is available
import time
from copy import deepcopy

def check_solution(graph, total_distance, new_route, max_vehicle_capacity, original_route, original_capacity, original_times):
    new_total_distance = 0
    current_vehicle_capacity = max_vehicle_capacity
    total_time = 0  
    arrival_times = [0]  

    i = 1
    while i < len(new_route) - 1:
        node_id = new_route[i]
        node_demand = graph[node_id][2]

        if current_vehicle_capacity - node_demand < 0:
            return False, total_distance, original_capacity, original_times

        previous_node = new_route[i - 1]
        distance = euclidean_distance(graph[previous_node], graph[node_id])
        arrival_time = total_time + distance

        if arrival_time > graph[node_id][4]:
            return False, total_distance, original_capacity, original_times

        if arrival_time < graph[node_id][3]:
            total_time += (graph[node_id][3] - arrival_time)
            arrival_time = graph[node_id][3]

        total_time += distance + graph[node_id][5]
        new_total_distance += distance
        current_vehicle_capacity -= node_demand
        arrival_times.append(arrival_time)
        i += 1

    depot_distance = euclidean_distance(graph[new_route[-2]], graph[0])
    total_time += depot_distance
    new_total_distance += depot_distance

    if total_time > graph[0][4]: 
        return False, total_distance, original_capacity, original_times
    
    arrival_times.append(total_time)
    return True, new_total_distance, current_vehicle_capacity, arrival_times

def perturb_solution(graph, vehicles, total_distance, computation_time, routes, max_vehicle_capacity):
    start_time = time.time()
    
    if len(routes) < 3:
        return len(routes), total_distance, computation_time, routes, max_vehicle_capacity  # Not enough routes to proceed
    
    # Select three random distinct routes
    selected_routes = random.sample(routes, 3)
    
    # Pick one random node from each selected route, excluding depots at start and end
    selected_nodes = []
    for route in selected_routes:
        if len(route[0]) > 2:  # Ensure there are nodes to select (excluding depots)
            node_idx = random.choice(range(1, len(route[0]) - 1))
            selected_nodes.append(route[0][node_idx])
        else:
            return len(routes), total_distance, computation_time, routes, max_vehicle_capacity  # Not enough nodes

    # Create a new route starting and ending at depot (node 0)
    new_route = [0] + selected_nodes + [0]

    # Check feasibility of new route
    factible, new_route_distance, new_capacity, arrival_times = check_solution(
        deepcopy(graph), deepcopy(total_distance), new_route, max_vehicle_capacity, new_route, max_vehicle_capacity, []
    )

    if factible:
        # Update routes by removing nodes from original routes
        for idx, route in enumerate(selected_routes):
            new_route_nodes = [node for node in route[0] if node not in selected_nodes]
            updated_route = list(route)
            updated_route[0] = new_route_nodes
            selected_routes[idx] = tuple(updated_route)

        # Append the new feasible route
        new_route_info = (new_route, new_route_distance, max_vehicle_capacity - sum(graph[node][2] for node in selected_nodes), arrival_times, new_route_distance)
        selected_routes.append(new_route_info)

        # Update the list of routes and compute the new total distance
        routes = [route for route in routes if route not in selected_routes] + selected_routes
        total_distance = sum(route[4] for route in routes)
    
    end_time = time.time()
    computation_time += int((end_time - start_time) * 1000)

    return len(routes), total_distance, computation_time, routes, max_vehicle_capacity

# Updated function perturb_solution should now pick three nodes from different routes and create a new route with them.