from .Airport import Airport
from .Route import Route


class Graph:
    def __init__(self):
        self.vertices    = []   # lista de Airport
        self.routes      = []   # lista de Route
        self.adyacencias = []   # lista de listas [(j, weight), ...]

    # ─────────────────────────────────────────
    # BÚSQUEDA
    # ─────────────────────────────────────────

    def find_index(self, code: str) -> int:
        """Retorna el índice del aeropuerto con ese código, o -1 si no existe."""
        for i, airport in enumerate(self.vertices):
            if airport.code == code:
                return i
        return -1

    def find_airport(self, code: str):
        """Retorna el objeto Airport con ese código, o None."""
        for airport in self.vertices:
            if airport.code == code:
                return airport
        return None

    def find_route(self, src_code: str, dst_code: str):
        """Retorna la Route entre dos aeropuertos (sin importar dirección), o None."""
        for route in self.routes:
            if (
                (route.source.code == src_code and route.destination.code == dst_code)
                or
                (route.source.code == dst_code and route.destination.code == src_code)
            ):
                return route
        return None

    def has_route(self, src_code: str, dst_code: str) -> bool:
        return self.find_route(src_code, dst_code) is not None

    # ─────────────────────────────────────────
    # CONSTRUCCIÓN (solo para DataLoader)
    # ─────────────────────────────────────────

    def add_vertex(self, airport: Airport) -> None:
        """Agrega un vértice si su código no existe ya en el grafo."""
        if self.find_index(airport.code) == -1:
            self.vertices.append(airport)
            self.adyacencias.append([])

    def add_route(self, route: Route) -> None:
        """
        Agrega una arista no dirigida si aún no existe.
        Requiere que ambos extremos estén ya en el grafo.
        """
        if route is None:
            return
        src_i = self.find_index(route.source.code)
        dst_i = self.find_index(route.destination.code)
        if src_i == -1 or dst_i == -1:
            return
        if self.has_route(route.source.code, route.destination.code):
            return
        self.routes.append(route)
        self.adyacencias[src_i].append((dst_i, route.weight))
        self.adyacencias[dst_i].append((src_i, route.weight))

    # ─────────────────────────────────────────
    # FACTORY (para DataLoader)
    # ─────────────────────────────────────────

    def create_edge(self, source: Airport, destination: Airport, weight: float) -> Route:
        return Route(source, destination, weight)

    # ─────────────────────────────────────────
    # GETTERS
    # ─────────────────────────────────────────

    def get_vertices(self):
        return self.vertices

    def get_routes(self):
        return self.routes

    def get_edges_for_map(self):
        """
        Retorna lista de tuplas (Airport, Airport, peso) para el mapa.
        """
        return [
            (r.source, r.destination, r.weight)
            for r in self.routes
            if r.source and r.destination
        ]

    # ─────────────────────────────────────────
    # PARA ALGORITMOS
    # ─────────────────────────────────────────

    def vertex_count(self) -> int:
        return len(self.vertices)

    def codes(self):
        return [v.code for v in self.vertices]

    def neighbors(self, code: str):
        """Retorna lista de (codigo_vecino, peso)."""
        i = self.find_index(code)
        if i == -1:
            return []
        return [(self.vertices[j].code, w) for j, w in self.adyacencias[i]]