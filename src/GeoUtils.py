import math

class GeoUtils:
    # calcula la distancia en km entre dos puntos
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # radio de la Tierra en km

        # convertir a radianes
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # diferencias
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # fórmula
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c