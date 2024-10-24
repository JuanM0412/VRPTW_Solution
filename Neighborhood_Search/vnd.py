from solution import constructive
import os, time
from copy import deepcopy
from output import save_results_to_excel
from change_position_different_routes import different_routes
from change_position_same_route import change_position
from two_opt import two_opt
from insert_nodes import insert_nodes
from best_improvement import best_improvement


OUTPUT_FILE = 'Neighborhood_Search/output/VRPTW_JuanManuelGomez_VND_3120.xlsx'
INSTANCES_DIR = 'instances'
TIME_LIMIT = [50000, 50000, 50000, 50000, 50000, 50000, 200000, 200000, 200000, 200000, 200000, 200000, 750000, 750000, 750000, 750000, 750000, 750000]


def vnd(graph, vehicles, total_distance, computation_time, routes, max_vehicle_capacity, instance_number):
    start_time = time.time()
    neighborhoods = {3: best_improvement, 1: two_opt, 2: different_routes, 0: insert_nodes}
    
    best_total_distance = total_distance
    i = 0
    while i < 4:
        new_vehicles, new_routes, new_total_distance = deepcopy(vehicles), deepcopy(routes), deepcopy(total_distance)
        result = neighborhoods[i](graph, new_vehicles, new_total_distance, max_vehicle_capacity, new_routes, max_vehicle_capacity)
        _, new_total_distance, computation_time, new_routes, max_vehicle_capacity = result

        if computation_time > TIME_LIMIT[instance_number - 1]:
            print('Time limit exceeded')
            break

        if new_total_distance < best_total_distance:
            best_total_distance = new_total_distance
            vehicles, routes, total_distance = new_vehicles, new_routes, new_total_distance
            i = 0 
        else:
            i += 1
        
    
    end_time = time.time()
    computation_time += int((end_time - start_time) * 1000)

    return len(routes), total_distance, computation_time, routes, max_vehicle_capacity


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            print(f'Solving instance {instance_path}')
            instance_name = instance_filename.replace('.txt', '')
            instance_number = int(instance_name[5::])
            print('Instance number:', instance_number)
            graph, vehicles, total_distance, computation_time, routes, vehicle_capacity = constructive(instance_path)
            vehicles, total_distance, computation_time, routes, vehicle_capacity = vnd(graph, vehicles, total_distance, computation_time, routes, vehicle_capacity, instance_number)
            save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity, OUTPUT_FILE)


if __name__ == '__main__':
    main()