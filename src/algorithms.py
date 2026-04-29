"""
Algoritmos sobre grafos: Dijkstra, componentes conexas, bipartito, MST (Kruskal/Prim).
"""

from math import inf
import heapq


# =============================================================================
# 1. CAMINO MÍNIMO — Dijkstra
# =============================================================================

def shortest_path_between(graph, start, end):
    """
    Calcula el camino mínimo entre dos aeropuertos usando Dijkstra.
    Retorna dict con 'path' (lista de códigos), 'distance' (km), 'reachable' (bool).
    """
    n = graph.vertex_count()
    start_i = graph.find_index(start)
    end_i   = graph.find_index(end)

    if start_i == -1 or end_i == -1:
        return {"path": [], "distance": inf, "reachable": False}

    distances = [inf] * n
    previous  = [None] * n
    distances[start_i] = 0
    heap = [(0.0, start_i)]

    while heap:
        current_dist, current_i = heapq.heappop(heap)
        if current_dist > distances[current_i]:
            continue
        for neighbor_i, weight in graph.adyacencias[current_i]:
            new_dist = current_dist + weight
            if new_dist < distances[neighbor_i]:
                distances[neighbor_i] = new_dist
                previous[neighbor_i]  = current_i
                heapq.heappush(heap, (new_dist, neighbor_i))

    # Reconstruir camino
    path_indices = []
    curr = end_i
    while curr is not None:
        path_indices.append(curr)
        if curr == start_i:
            break
        curr = previous[curr]

    if not path_indices or path_indices[-1] != start_i:
        return {"path": [], "distance": inf, "reachable": False}

    path_indices.reverse()
    path_codes = [graph.vertices[i].code for i in path_indices]
    return {
        "path": path_codes,
        "distance": distances[end_i],
        "reachable": True,
    }


# =============================================================================
# 2. DIJKSTRA DESDE UN ORIGEN — retorna todas las distancias
# =============================================================================

def dijkstra_from(graph, start):
    """
    Ejecuta Dijkstra desde 'start' y devuelve el array de distancias
    (índice = posición del vértice en graph.vertices).
    """
    n = graph.vertex_count()
    start_i = graph.find_index(start)
    if start_i == -1:
        return None

    distances = [inf] * n
    distances[start_i] = 0
    heap = [(0.0, start_i)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > distances[u]:
            continue
        for v, w in graph.adyacencias[u]:
            nd = d + w
            if nd < distances[v]:
                distances[v] = nd
                heapq.heappush(heap, (nd, v))

    return distances


# =============================================================================
# 3. COMPONENTES CONEXAS — DFS iterativo
# =============================================================================

def connected_components(graph):
    """
    Encuentra todas las componentes conexas del grafo usando DFS iterativo.
    Retorna lista de listas de índices de vértices.
    """
    n = graph.vertex_count()
    visited = [False] * n
    components = []

    for i in range(n):
        if not visited[i]:
            stack = [i]
            component = []
            while stack:
                v = stack.pop()
                if not visited[v]:
                    visited[v] = True
                    component.append(v)
                    for neighbor, _ in graph.adyacencias[v]:
                        if not visited[neighbor]:
                            stack.append(neighbor)
            components.append(component)

    return components


# =============================================================================
# 4. VERIFICACIÓN BIPARTITA — BFS con 2-coloración
# =============================================================================

def is_bipartite(graph, component_indices=None):
    """
    Verifica si el subgrafo definido por 'component_indices' es bipartito
    usando BFS con 2-coloración.
    Si component_indices es None, verifica el grafo completo.
    Retorna (True/False, coloring_dict o None si no es bipartito).
    """
    n = graph.vertex_count()
    nodes = component_indices if component_indices is not None else list(range(n))

    color = [-1] * n  # -1 = sin visitar
    node_set = set(nodes)  # Crear set para búsqueda rápida

    for start in nodes:
        if color[start] != -1:
            continue
        queue = [start]
        color[start] = 0
        while queue:
            next_queue = []
            for u in queue:
                for v, _ in graph.adyacencias[u]:
                    if v not in node_set:  # CORREGIDO: usar node_set en lugar de set(nodes)
                        continue          # ignorar nodos fuera del componente
                    if color[v] == -1:
                        color[v] = 1 - color[u]
                        next_queue.append(v)
                    elif color[v] == color[u]:
                        return False, None   # ciclo impar → no bipartito
            queue = next_queue

    coloring = {nodes[k]: color[nodes[k]] for k in range(len(nodes))}
    return True, coloring


# =============================================================================
# 5. ÁRBOL DE EXPANSIÓN MÍNIMA — Kruskal con Union-Find
# =============================================================================

class _UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def minimum_spanning_tree(graph, component_indices=None):
    """
    Calcula el MST del subgrafo dado usando Kruskal.
    Si component_indices es None, opera sobre todo el grafo.
    Retorna (peso_total, lista_de_aristas [(u_code, v_code, peso)]).
    """
    n = graph.vertex_count()
    nodes = component_indices if component_indices is not None else list(range(n))
    node_set = set(nodes)

    # Re-indexar para Union-Find local
    local_idx = {global_i: local_i for local_i, global_i in enumerate(nodes)}
    uf = _UnionFind(len(nodes))

    # Recopilar aristas del subgrafo (sin duplicar)
    edges = []
    seen = set()
    for u in nodes:
        for v, w in graph.adyacencias[u]:
            if v not in node_set:
                continue
            key = (min(u, v), max(u, v))
            if key not in seen:
                seen.add(key)
                edges.append((w, u, v))

    edges.sort()  # Kruskal: orden ascendente por peso

    total_weight = 0.0
    mst_edges = []

    for w, u, v in edges:
        lu, lv = local_idx[u], local_idx[v]
        if uf.union(lu, lv):
            total_weight += w
            mst_edges.append((
                graph.vertices[u].code,
                graph.vertices[v].code,
                w,
            ))

    return total_weight, mst_edges


# =============================================================================
# 6. TOP-10 CAMINOS MÁS LARGOS DESDE UN VÉRTICE
# =============================================================================

def top_farthest_airports(graph, start, top_n=10):
    """
    Devuelve los top_n aeropuertos alcanzables con el camino mínimo más largo
    desde 'start', ordenados de mayor a menor distancia.
    Retorna lista de (airport_obj, distancia_km).
    """
    distances = dijkstra_from(graph, start)
    if distances is None:
        return []

    results = []
    for i, d in enumerate(distances):
        code = graph.vertices[i].code
        if d != inf and code != start:
            results.append((graph.vertices[i], d))

    # Ordenar de mayor a menor distancia y tomar los primeros top_n
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]