from .Airport import Airport
from .Route import Route


class Graph:
    def __init__(self):
        self.vertices = []
        self.routes = []
        self.adyacencias = []

    def rebuild_adyacencias(self):
        self.adyacencias = [[] for _ in range(len(self.vertices))]
        for route in self.routes:
            i = self.find_index(route.source.code)
            j = self.find_index(route.destination.code)
            w = route.weight
            if i != -1 and j != -1:
                self.adyacencias[i].append((j, w))
                self.adyacencias[j].append((i, w))

    # =========================
    # BÚSQUEDA
    # =========================

    def find_index(self, code):
        for i in range(len(self.vertices)):
            if self.vertices[i].code == code:
                return i
        return -1

    def find_airport(self, code):
        for airport in self.vertices:
            if airport.code == code:
                return airport
        return None

    def find_route(self, source, destination):
        for route in self.routes:
            if (
                (route.source.code == source and route.destination.code == destination)
                or
                (route.source.code == destination and route.destination.code == source)
            ):
                return route
        return None

    # =========================
    # AGREGAR
    # =========================

    def add_vertex(self, airport):
        if self.find_index(airport.code) == -1:
            self.vertices.append(airport)
            self.adyacencias.append([])

    def add_route(self, route):
        if not route:
            return
        # verificar existencia de origen y destino
        source = self.find_index(route.source.code)
        dest = self.find_index(route.destination.code)
        if source == -1 or dest == -1:
            return
        # evitar duplicados
        if self.has_route(route.source.code, route.destination.code):
            return
        self.routes.append(route)
        self.adyacencias[source].append((dest, route.weight))
        self.adyacencias[dest].append((source, route.weight))

    def has_route(self, source, destination):
        for edge in self.routes:
            if (
                (edge.source.code == source and edge.destination.code == destination)
                or
                (edge.source.code == destination and edge.destination.code == source)
            ):
                return True
        return False

    # =========================
    # ELIMINAR
    # =========================

    def remove_airport(self, airport):
        if airport not in self.vertices:
            return

        self.vertices.remove(airport)

        # 🔥 eliminar rutas asociadas (FORMA SEGURA)
        self.routes = [
            r for r in self.routes
            if r.source.code != airport.code and r.destination.code != airport.code
        ]
        self.rebuild_adyacencias()

    def remove_edge(self, edge):
        if edge in self.routes:
            self.routes.remove(edge)
        source = self.find_index(edge.source.code)
        dest = self.find_index(edge.destination.code)
        self.adyacencias[source].remove((dest, edge.weight))
        self.adyacencias[dest].remove((source, edge.weight))

    # =========================
    # GETTERS
    # =========================

    def get_vertices(self):
        return self.vertices

    def get_routes(self):
        return self.routes

    def get_edges_for_map(self):
        edge_list = []
        for edge in self.routes:
            if edge.source and edge.destination:
                edge_list.append((edge.source, edge.destination, edge.weight))
        return edge_list

    # =========================
    # FACTORY
    # =========================

    def create_airport(self, code, name, city, country, lat, lon):
        return Airport(code, name, city, country, lat, lon)

    def create_edge(self, source, destination, weight):
        return Route(source, destination, weight)

    # =========================
    # PARA ALGORITMOS
    # =========================

    def codes(self):
        return [v.code for v in self.vertices]

    def vertex_count(self):
        return len(self.vertices)

    def neighbors(self, code):
        i = self.find_index(code)
        if i == -1:
            return []
        result = []
        for j, w in self.adyacencias[i]:
            neighbor_code = self.vertices[j].code
            result.append((neighbor_code, w))
        return result