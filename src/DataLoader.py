from __future__ import annotations
import csv
import pickle
from pathlib import Path
from .Airport import Airport
from .Graph import Graph
from .GeoUtils import GeoUtils

def _build_airport(
    code: str, name: str, city: str, country: str,
    latitude: str, longitude: str
) -> Airport:
    return Airport(
        code=code.strip().upper(),
        name=name.strip(),
        city=city.strip(),
        country=country.strip(),
        lat=float(latitude),
        lon=float(longitude),
    )

def load_graph_from_csv(file_path: str | Path, use_cache=True) -> Graph:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)

    cache_path = path.parent / f"{path.stem}_graph.pkl"

    if use_cache and cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                graph = pickle.load(f)
            print(f"Caché cargado: {graph.vertex_count()} aeropuertos, {len(graph.get_routes())} rutas")
            return graph
        except Exception as e:
            print(f"Error al leer caché: {e}. Recargando desde CSV...")

    print("Cargando desde CSV (esto puede tomar varios segundos la primera vez)...")
    graph = Graph()

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        total = len(rows)
        for i, row in enumerate(rows):
            if i % 10000 == 0:
                print(f"  Procesando {i}/{total} rutas...")
            source = _build_airport(
                row["Source Airport Code"],
                row["Source Airport Name"],
                row["Source Airport City"],
                row["Source Airport Country"],
                row["Source Airport Latitude"],
                row["Source Airport Longitude"],
            )
            dest = _build_airport(
                row["Destination Airport Code"],
                row["Destination Airport Name"],
                row["Destination Airport City"],
                row["Destination Airport Country"],
                row["Destination Airport Latitude"],
                row["Destination Airport Longitude"],
            )
            graph.add_vertex(source)
            graph.add_vertex(dest)
            weight = GeoUtils.haversine(source.lat, source.lon, dest.lat, dest.lon)
            graph.add_route(graph.create_edge(source, dest, weight))

    print(f" Grafo construido: {graph.vertex_count()} aeropuertos, {len(graph.get_routes())} rutas")
    # Guardar caché
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(graph, f)
        print(f"Caché guardado en {cache_path}")
    except Exception as e:
        print(f"No se pudo guardar caché: {e}")

    return graph