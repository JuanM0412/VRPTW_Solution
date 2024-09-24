from solution import solve_instance
import math, os, time, openpyxl


INSTANCES_DIR = 'instances'
OUTPUT_FILE = 'output/VRPTW_JuanManuelGomez_constructivo.xlsx'


def change_position(graph, vehicles, total_distance, computation_time, routes, vehicle_capacity):
    print(f'Graph: {graph}')
    print(f'Vehicles: {vehicles}')
    print(f'Total distance: {total_distance}')
    print(f'Computation time: {computation_time}')
    print(f'Routes: {routes}')
    print(f'Veicle capacity: {vehicle_capacity}')


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            print(f'Processing instance {instance_filename}')
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            graph, vehicles, total_distance, computation_time, routes, vehicle_capacity = solve_instance(instance_path)
            change_position(graph, vehicles, total_distance, computation_time, routes, vehicle_capacity)


if __name__ == '__main__':
    main()