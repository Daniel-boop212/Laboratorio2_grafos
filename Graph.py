class Graph:
    def __init__(self):
        self.vertices = {}  
        self.adj_list = {} 

    def find_index(self, code):
        for i in range(len(self.vertices)):
            if self.vertices[i].code == code:
                return i
        return -1
    
    def add_vertex(self, airport):
        if self.find_index(airport.code) == -1:
            self.vertices.append(airport)
            self.adj_list.append([])  

    def add_edge(self, code1, code2, weight):
        if code1 == code2:
            return
        i = self.find_index(code1)
        j = self.find_index(code2)
        if i == -1 or j == -1:
            return
        self.adj_list[i].append((j, weight))
        self.adj_list[j].append((i, weight))