#Encargado de leer el CSV y construir el grafo.
class DataLoader:
    def __init__(self, filename):
        self.filename = filename
        self.airports = {}
        self.edges = {}