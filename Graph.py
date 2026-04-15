from Airport import Airport

class Graph:
    def __init__(self):
        self.vertices = []
        self.edges = [] 

    def find_index(self, code):
        for i in range(len(self.vertices)):
            if self.vertices[i].code == code:
                return i
        return -1
    
    def add_vertex(self, airport):
        if self.find_index(airport.code) == -1:
            self.vertices.append(airport)
            self.edges.append([])  

    def add_edge(self, code1, code2, weight):
        if code1 == code2:
            return
        i = self.find_index(code1)
        j = self.find_index(code2)
        if i == -1 or j == -1:
            return
        self.edges[i].append((j, weight))
        self.edges[j].append((i, weight))

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges
    
    def create_airport(self, code, name, city, country, lat, lon):
        return Airport(code, name, city, country, lat, lon)
    
    def get_edges_for_map(self):
        edge_list = []
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            for (j, weight) in self.edges[i]:
                v2 = self.vertices[j]
                if i < j:
                    edge_list.append((v1, v2, weight))
        return edge_list