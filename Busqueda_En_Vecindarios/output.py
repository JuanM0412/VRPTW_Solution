import os, openpyxl


def save_results_to_excel(instance_name, vehicles, total_distance, computation_time, routes, vehicle_capacity, output_file):
    if not os.path.exists(output_file):
        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)
    else:
        workbook = openpyxl.load_workbook(output_file)

    sheet = workbook.create_sheet(instance_name)

    # First row with overall results
    sheet.append([vehicles, round(total_distance, 3), computation_time])

    # Detailed results for each vehicle
    for route_info in routes:
        # Descomponer la tupla en los primeros cuatro elementos, e ignorar los adicionales
        route = route_info[0]
        time = route_info[1]
        capacity = route_info[2]
        arrival_times = route_info[3]
        # Si hay más elementos en la tupla, puedes ignorarlos o utilizarlos según sea necesario

        # Prepare the row with number of nodes, the route, and the arrival times
        route_without_depots = route[1:-1]  # Exclude the depots (first and last)
        arrival_times_without_depots = arrival_times[1:-1]  # Exclude depot times for arrival

        # Construct the row data
        row = [len(route_without_depots)] + route + [round(t, 3) for t in arrival_times] + [vehicle_capacity - capacity]
        sheet.append(row)

    workbook.save(output_file)