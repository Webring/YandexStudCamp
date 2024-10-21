import networkx as nx
import heapq
from build_graph import graph
import numpy as np


def distance(point_a, point_b):
    x_a, y_a = point_a
    x_b, y_b = point_b
    return np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)

def get_closest_point(x_coord, y_coord, nodes):
    point = (x_coord, y_coord)
    min = 10000000
    closest_point = 0
    for i, node in enumerate(nodes):
        cur_point = (node[0], node[1])
        if distance(cur_point, point) < min:
            closest_point = i
            min = distance(cur_point, point)
    
    return closest_point


def dijkstra(G, start, end):
    queue = []
    heapq.heappush(queue, (0, start))
    distances = {node: float('infinity') for node in G.nodes}
    distances[start] = 0
    previous = {node: None for node in G.nodes}
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in G[current_node].items():
            distance = current_distance + weight['weight']
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()

    path_coords = []
    for node in path:
        path_coords.append([nodes[node][0], nodes[node][1]])
    return path_coords, distances[end]


nodes, edges, robot_center, base_center, cubes_number, cubes = graph()
#print(edges)

# Создание графа
G = nx.DiGraph()
for i in range(len(edges)):
    for j in range(len(edges)):
        if edges[i][j] == 1:
            G.add_edge(i, j, weight=2)


best_dist = 100000
best_path = []

for i in range(cubes_number):
    start = get_closest_point(robot_center[0], robot_center[1], nodes)
    end = get_closest_point(cubes[i][0], cubes[i][1], nodes)
    path_coords, dist = dijkstra(G, start, end)
    if dist < best_dist:
        best_path = path_coords

print(best_path)






route_start = 0
route_end = 15

path, distance = dijkstra(G, start, end)


#print(f"Кратчайший путь: {path}")
#print(f"Расстояние: {distance}")

# Визуализация графа
'''pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, edge_color='gray')
nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
path_edges = list(zip(path[:-1], path[1:]))
nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red')
plt.show()'''