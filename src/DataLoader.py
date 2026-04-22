"""Carga del dataset y construcción del grafo de aeropuertos."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from .Airport import Airport
from .Graph import Graph
from .Route import Route
from .GeoUtils import GeoUtils


def _build_airport(
    code: str,
    name: str,
    city: str,
    country: str,
    latitude: str,
    longitude: str,
) -> Airport:
    """Construye una instancia Airport a partir de los datos crudos del CSV."""
    return Airport(
        code=code.strip().upper(),
        name=name.strip(),
        city=city.strip(),
        country=country.strip(),
        lat=float(latitude),
        lon=float(longitude),
    )


def load_graph_from_csv(file_path: str | Path) -> Graph:
    """Lee el CSV y devuelve el grafo completo del laboratorio."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)

    graph = Graph()

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            source = _build_airport(
                row["Source Airport Code"],
                row["Source Airport Name"],
                row["Source Airport City"],
                row["Source Airport Country"],
                row["Source Airport Latitude"],
                row["Source Airport Longitude"],
            )
            destination = _build_airport(
                row["Destination Airport Code"],
                row["Destination Airport Name"],
                row["Destination Airport City"],
                row["Destination Airport Country"],
                row["Destination Airport Latitude"],
                row["Destination Airport Longitude"],
            )

            graph.add_vertex(source)
            graph.add_vertex(destination)

            weight = GeoUtils.haversine(
                source.lat,
                source.lon,
                destination.lat,
                destination.lon,
            )
            graph.add_route(graph.create_edge(source, destination, weight))

    return graph
