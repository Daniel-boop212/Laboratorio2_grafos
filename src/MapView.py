from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from statistics import mean


class MapView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.load_empty_map()

    # =========================
    # MAPA VACÍO
    # =========================
    def load_empty_map(self):
        self.setHtml(self.base_html(""), QUrl("http://localhost/"))

    # =========================
    # HTML BASE
    # =========================
    def base_html(self, extra_js):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>

            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                }}
                #map {{
                    width: 100%;
                    height: 100%;
                }}
            </style>

            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

            <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster/dist/MarkerCluster.css"/>
            <script src="https://unpkg.com/leaflet.markercluster/dist/leaflet.markercluster.js"></script>
        </head>

        <body>
            <div id="map"></div>

            <script>
                var map = L.map('map').setView([20, 0], 2);

                L.tileLayer(
                    'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
                    {{
                        attribution: '© OpenStreetMap'
                    }}
                ).addTo(map);

                var markers = L.markerClusterGroup();

                {extra_js}

                map.addLayer(markers);
            </script>
        </body>
        </html>
        """

    # =========================
    # MAPA GENERAL
    # =========================
    def draw_graph(self, graph, edge_limit=1000):
        airports = graph.get_vertices()

        if not airports:
            return

        # 🔥 LIMITAR aeropuertos (CLAVE)
        airports = airports[:1000]

        center_lat = mean(a.lat for a in airports)
        center_lon = mean(a.lon for a in airports)

        js = f"map.setView([{center_lat}, {center_lon}], 2);\n"

        # ICONO
        js += """
        var airportIcon = L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
        iconSize: [18, 18]
        });
        """

        # ✈️ AEROPUERTOS
        for airport in airports:
            if airport.lat is None or airport.lon is None:
                continue

            js += f"""
            L.marker([{airport.lat}, {airport.lon}], {{icon: airportIcon}})
            .addTo(map)
            .bindPopup("<b>{airport.code}</b><br>{airport.city}");
            """

        # ✈️ RUTAS (MUY LIMITADAS)
        count = 0
        for v1, v2, _ in graph.get_edges_for_map():
            if count >= edge_limit:
                break

            if not v1 or not v2:
                continue

            js += f"""
            L.polyline(
                [[{v1.lat}, {v1.lon}], [{v2.lat}, {v2.lon}]],
                {{
                color: '#ff5733',
                weight: 2,
                opacity: 0.6
                }}
            ).addTo(map);
            """
            count += 1

        self.setHtml(self.base_html(js), QUrl("http://localhost/"))

    # =========================
    # CAMINO MÍNIMO
    # =========================
    def draw_path(self, graph, path):
        if not path:
            return

        coords = []
        for code in path:
            airport = graph.find_airport(code)
            if airport:
                coords.append(airport)

        if not coords:
            return

        center_lat = mean(a.lat for a in coords)
        center_lon = mean(a.lon for a in coords)

        js = f"map.setView([{center_lat}, {center_lon}], 4);\n"

        poly_points = []

        for i, airport in enumerate(coords):
            if airport.lat is None or airport.lon is None:
                continue

            poly_points.append(f"[{airport.lat}, {airport.lon}]")

            color = "blue"
            label = "Escala"

            if i == 0:
                color = "green"
                label = "Origen"
            elif i == len(coords) - 1:
                color = "red"
                label = "Destino"

            popup = f"<b>{label}: {airport.code}</b><br>{airport.name}<br>{airport.city}, {airport.country}"

            js += f"""
            L.marker([{airport.lat}, {airport.lon}],
                {{icon: L.icon({{
                    iconUrl: 'https://maps.google.com/mapfiles/ms/icons/{color}-dot.png',
                    iconSize: [32, 32]
                }})}}
            ).addTo(map).bindPopup(`{popup}`);
            """

        # 🔥 Ruta destacada
        js += f"""
        var polyline = L.polyline(
            [{",".join(poly_points)}],
            {{
                color: '#ff0000',
                weight: 4
            }}
        ).addTo(map);

        polyline.bindPopup("Ruta: {' -> '.join(path)}");
        """

        self.setHtml(self.base_html(js), QUrl("http://localhost/"))