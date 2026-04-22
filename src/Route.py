#Representa una arista (vuelo entre aeropuertos).
class Route:
    def __init__(self, source, destination, weight):
        self.source = source
        self.destination = destination
        self.weight = weight