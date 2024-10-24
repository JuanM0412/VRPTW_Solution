import random, time, os
from copy import deepcopy
from multiple_solutions import solve_instance
from output import save_results_to_excel
from change_position_different_routes import different_routes, check_solution
from solution import parse_file
from multiple_solutions import solve_instance
from insert_nodes import insert_nodes
from perturbation import perturb_solution

# Parámetros para el algoritmo
nsol = 3  # Número de soluciones iniciales a generar
nit = 10  # Número de iteraciones internas (perturbaciones)
nc = 5    # Número de veces que se perturba la solución por iteración

OUTPUT_FILE = 'Neighborhood_Search/output/VRPTW_JuanManuelGomez_ELS_MultiStart_nsol3_nit10_nc10.xlsx'
INSTANCES_DIR = 'instances'
TIME_LIMIT = [50000, 50000, 50000, 50000, 50000, 50000, 200000, 200000, 200000, 200000, 200000, 200000, 750000, 750000, 750000, 750000, 750000, 750000]


class TabuList:
    def __init__(self, tenure):
        self.tabu_list = []
        self.tenure = tenure

    def add_solution(self, solution):
        self.tabu_list.append(deepcopy(solution))
        if len(self.tabu_list) > self.tenure:
            self.tabu_list.pop(0)

    def is_tabu(self, solution):
        return solution in self.tabu_list


def MS_ELS(graph, vehicle_capacity, instance_number, nsol=3, nit=10, nc=5, tabu_tenure=10):
    best_solution = (None, float('inf')) 
    tabu_list = TabuList(tabu_tenure)
    start_time = time.time()

    # Generar múltiples soluciones iniciales
    for h in range(nsol):
        # Generar solución inicial
        s = initial_solution(graph, vehicle_capacity, h)

        # Aplicar búsqueda local a la solución inicial
        s = local_search(graph, vehicle_capacity, s)

        # Verificar si es la mejor solución hasta el momento
        if s[1] < best_solution[1]:
            best_solution = deepcopy(s)

    # Iteraciones para mejorar las soluciones
    for it in range(nit):
        current_best = (None, float('inf'))

        for c in range(nc):
            # Perturbar la solución actual
            perturbed_solution = perturb_solution(graph, best_solution, vehicle_capacity)
            #print('Perturbed solution:', perturbed_solution)

            # Aplicar búsqueda local
            improved_solution = local_search(graph, vehicle_capacity, perturbed_solution)
            #print('Improved solution:', improved_solution)

            # Comparar con la mejor solución de la iteración
            if not tabu_list.is_tabu(improved_solution[3]):
                tabu_list.add_solution(improved_solution[3])
            
                if improved_solution[1] < current_best[1]:
                    current_best = deepcopy(improved_solution)

        # Si la mejor solución en la iteración es mejor que la global
        if current_best[1] < best_solution[1]:
            best_solution = deepcopy(current_best)

        # Verificar el tiempo límite
        if (time.time() - start_time) * 1000 > TIME_LIMIT[instance_number - 1]:
            print('Time limit exceeded')
            break

    return best_solution, int((time.time() - start_time) * 1000)


def initial_solution(graph, vehicle_capacity, h):
    if h == 0:
        solution = solve_instance(graph, vehicle_capacity, 0)
    elif h == 1:
        solution = solve_instance(graph, vehicle_capacity, 0)
        local_search(graph, vehicle_capacity, solution)
    else:
        solution = solve_instance(graph, vehicle_capacity, random.uniform(0.1, 0.3))

    return solution


def local_search(graph, vehicle_capacity, solution):
    # Función que aplica búsqueda local a la solución
    improved_solution = insert_nodes(graph, solution[0], solution[1], solution[2], solution[3], vehicle_capacity)  # Método para mejorar la solución
    return improved_solution


def perturb_solution(graph, solution, vehicle_capacity):
    # Función para perturbar una solución (puedes adaptar esto a tus necesidades)
    perturbed_solution = deepcopy(solution)
    perturbed_solution = different_routes(graph, solution[0], solution[1], solution[2], solution[3], vehicle_capacity)
    return perturbed_solution


def main():
    for instance_filename in os.listdir(INSTANCES_DIR):
        if instance_filename.endswith('.txt'):
            instance_path = os.path.join(INSTANCES_DIR, instance_filename)
            instance_name = instance_filename.replace('.txt', '')
            instance_number = int(instance_name[5::])  # Obtener el número de instancia

            # Cargar el grafo y la capacidad del vehículo desde el archivo de instancia
            graph, vehicle_capacity = parse_file(instance_path)

            # Aplicar el algoritmo MS-ELS a la instancia
            best_solution, computation_time = MS_ELS(graph, vehicle_capacity, instance_number)

            # Guardar los resultados finales
            vehicles, total_distance, computation_time, routes, *other_values = best_solution
            save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity, OUTPUT_FILE)


if __name__ == '__main__':
    main()
