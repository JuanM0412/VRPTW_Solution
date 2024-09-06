# Métodos Constructivos y Aleatorizados

## Problemática

El problema de ruteo de vehículos con ventanas de tiempo (VRPTW) consiste en que una flota de vehículos homogéneos debe visitar un conjunto de nodos distribuidos geográficamente. Cada vehículo realiza una ruta visitando un subconjunto de estos nodos, de tal manera que cada nodo debe ser visitado exactamente una vez por un solo vehículo, y cada ruta debe comenzar y terminar en un depósito común. El objetivo es minimizar el número total de vehículos utilizados, y entre soluciones que usan el mismo número de vehículos, se prefiere la que minimice la distancia total recorrida.

Cada vehículo tiene una capacidad limitada, que restringe la carga total que puede transportar, y los nodos deben ser visitados dentro de una ventana de tiempo específica.

## Definición del problema

El VRPTW se define en un grafo *G* = (V, E), donde *V* = {0, 1, ..., n} es el conjunto de nodos y *E* es el conjunto de arcos que conectan los nodos. El nodo 0 representa el depósito, mientras que *V_c* = {1, ..., n} son los clientes. Cada nodo *i* tiene una demanda *q_i* que debe ser menor o igual a la capacidad *Q* del vehículo, un tiempo de servicio *s_i*, y una ventana de tiempo [*e_i*, *l_i*] en la que se debe iniciar el servicio. Si un vehículo llega antes de *e_j*, debe esperar hasta que la ventana de tiempo abra, y si llega después de *l_j*, no se permite el servicio.

### Restricciones

Cada solución del VRPTW debe cumplir las siguientes restricciones:

1. Cada cliente debe ser atendido solo una vez.
2. Los vehículos deben viajar de un cliente a otro en la ruta, comenzando y terminando en el depósito.
3. La demanda total de cada ruta no debe exceder la capacidad del vehículo *Q*.
4. El servicio en cada cliente debe comenzar dentro de su ventana de tiempo, y los vehículos deben regresar al depósito antes de *l_0*.

Este problema busca minimizar el número de vehículos y la distancia total recorrida, respetando las restricciones de capacidad y tiempo.

## Uso

Este repositorio contiene tres algoritmos que resuelven el problema de VRPTW:

- `minor_distance.py`. Este archivo contiene el método constructivo.
- `GRASP_1.py`. Este archivo contiene el primer método GRASP (cardinalidad).
- `GRASP_2.py`. Este archivo contiene el segundo método GRASP (alpha).

Además, también está:

- `lower_bound.py`. Este archivo contiene la cota inferior.

Dependiendo de la solución que se quiera obtener, se ejecuta el archivo correspondiente.

Cada uno de los algoritmos genera un archivo `.xlsx` como salida. Estos se guardan en la carpeta `output`, con el nombre especificado en el archivo de ejecución. Además, también están las instancias del problema, que se guardan en la carpeta `instances`.

Para ejecutar alguno de los algoritmos, simplemente se debe ir al directorio raíz del repositorio y ejecutar el archivo correspondiente usando el comando `python` seguido del nombre del archivo. Ejemplo:
```
python lower_bound.py
```

**NOTA:** es importante tener instalada la dependencia de `openpyxl` para poder crear los archivos `.xlsx`, que muestran los resultados de los algoritmos.