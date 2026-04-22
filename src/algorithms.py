from math import inf
import heapq

def shortest_path_between(graph, start, end):
    n = graph.vertex_count()
    start_i = graph.find_index(start)
    end_i = graph.find_index(end)
    if start_i == -1 or end_i == -1:
        return {"path": [], "distance": float("inf"), "reachable": False}
    distances = [inf] * n
    previous = [None] * n
    distances[start_i] = 0
    heap = [(0, start_i)]
    while heap:
        current_dist, current_i = heapq.heappop(heap)
        if current_dist > distances[current_i]:
            continue
        for neighbor_i, weight in graph.adyacencias[current_i]:
            new_dist = current_dist + weight
            if new_dist < distances[neighbor_i]:
                distances[neighbor_i] = new_dist
                previous[neighbor_i] = current_i
                heapq.heappush(heap, (new_dist, neighbor_i))
    path_indices = []
    curr = end_i
    while curr is not None:
        path_indices.append(curr)
        if curr == start_i:
            break
        curr = previous[curr]
    if not path_indices or path_indices[-1] != start_i:
        return {"path": [], "distance": float("inf"), "reachable": False}
    path_indices.reverse()
    path_codes = [graph.vertices[i].code for i in path_indices]
    return {
        "path": path_codes,
        "distance": distances[end_i],
        "reachable": True
    }

def connected_components(self, graph):
    n = graph.vertex_count()
    visited = [False] * n
    components = []
    for i in range(n):
        if not visited[i]:
            # nueva componente
            stack = [i]
            component = []
            while stack:
                v = stack.pop()
                if not visited[v]:
                    visited[v] = True
                    component.append(v)
                    for neighbor, _ in self.graph.adyacencias[v]:
                        if not visited[neighbor]:
                            stack.append(neighbor)
            components.append(component)
    return components