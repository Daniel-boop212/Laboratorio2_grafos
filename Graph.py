from Airport import Airport
from Edge import Edge

class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = [] 

    def find_index(self, code):
        for i in range(len(self.vertices)):
            if self.vertices[i].code == code:
                return i
        return -1
    
    def find_airport(self, code):
        for i in range(len(self.vertices)):
            if self.vertices[i].code == code:
                return self.vertices[i]
        return None
    
    def find_edge(self, source, destination):
        for edge in self.edges:
            if (edge.source.code == source and edge.destination.code == destination) or (edge.source.code == destination and edge.destination.code == source):
                return edge
        return None
    
    def add_vertex(self, airport):
        if self.find_index(airport.code) == -1:
            self.vertices.append(airport)

    def add_edge(self, edge):
        source = self.find_index(edge.source.code)
        destination = self.find_index(edge.destination.code)
        if source == -1 or destination == -1:
            return
        self.edges.append(edge)

    def has_edge(self, source, destination):
        if self.find_index(source) == -1 or self.find_index(destination) == -1:
            return False
        for edge in self.edges:
            if (edge.source.code == source and edge.destination.code == destination) or (edge.source.code == destination and edge.destination.code == source):
                return True
        return False

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges
    
    def create_airport(self, code, name, city, country, lat, lon):
        return Airport(code, name, city, country, lat, lon)
    
    def create_edge(self, source, destination, weight):
        return Edge(source, destination, weight)
    
    def remove_airport(self, airport):
        self.vertices.remove(airport)
        for edge in self.edges:
            if edge.source.code == airport.code or edge.destination.code == airport.code:
                self.edges.remove(edge)

    def remove_edge(self, edge):
        self.edges.remove(edge)
    
    def get_edges_for_map(self):
        edge_list = []
        for edge in self.edges:
            edge_list.append((edge.source, edge.destination, edge.weight))
        return edge_list