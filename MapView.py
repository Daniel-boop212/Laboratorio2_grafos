from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


class MapView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.load_empty_map()

    # =========================
    # MAPA VACÍO
    # =========================
    def load_empty_map(self):
        self.setHtml(self.base_html(""), QUrl("https://localhost/"))

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

                {extra_js}
            </script>
        </body>
        </html>
        """

    # =========================
    # DIBUJAR GRAFO
    # =========================
    def draw_graph(self, vertices, edges):
        js = ""

        # 🔵 VÉRTICES
        for v in vertices:
            js += f"""
            L.marker([{v.lat}, {v.lon}])
                .addTo(map)
                .bindPopup("<b>{v.name}</b><br>{v.city}, {v.country}");
            """

        # 🔵 ARISTAS 
        for e in edges:
            v1, v2, weight = e

            js += f"""
            L.polyline(
                [[{v1.lat}, {v1.lon}], [{v2.lat}, {v2.lon}]],
                {{
                    color: 'blue',
                    weight: 2
                }}
            ).addTo(map);
            """

        self.setHtml(self.base_html(js), QUrl("https://localhost/"))