from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QFrame, QStackedLayout, QMessageBox
)

from GeoUtils import GeoUtils
from MapView import MapView
from Graph import Graph


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rutas Aéreas")
        self.setMinimumSize(1300, 750)

        self.setStyleSheet("""
QWidget {
    background-color: #f5f6fa;
    color: #2c3e50;   /* 🔥 TEXTO OSCURO GLOBAL */
}

QPushButton {
    padding: 10px;
    border-radius: 8px;
    background-color: #3498db;
    color: white;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QLineEdit {
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #ccc;
    background-color: white;
    color: black;   /* 🔥 IMPORTANTE */
}

QLabel {
    color: #2c3e50; /* 🔥 CLAVE */
}
""")

        self.graph = Graph()

        self.init_ui()
        self.load_demo_data()

    # =========================
    # UI PRINCIPAL
    # =========================
    def init_ui(self):
        main_layout = QHBoxLayout()

        sidebar = QFrame()
        sidebar.setFixedWidth(200)

        sidebar_layout = QVBoxLayout()

        self.btn_map = QPushButton("Mapa")
        self.btn_menu = QPushButton("Menú")

        sidebar_layout.addWidget(self.btn_map)
        sidebar_layout.addWidget(self.btn_menu)
        sidebar_layout.addStretch()

        sidebar.setLayout(sidebar_layout)

        self.main_stack = QStackedLayout()
        self.main_stack.addWidget(self.create_map_view())
        self.main_stack.addWidget(self.create_menu_view())

        main_layout.addWidget(sidebar)
        main_layout.addLayout(self.main_stack)

        self.setLayout(main_layout)

        self.btn_map.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        self.btn_menu.clicked.connect(lambda: self.main_stack.setCurrentIndex(1))

    # =========================
    # MAPA
    # =========================
    def create_map_view(self):
        container = QFrame()
        layout = QVBoxLayout()

        self.map_view = MapView()
        layout.addWidget(self.map_view)

        container.setLayout(layout)
        return container

    # =========================
    # MENÚ
    # =========================
    def create_menu_view(self):
        container = QFrame()
        layout = QHBoxLayout()

        # BOTONES
        left_panel = QFrame()
        left_layout = QVBoxLayout()

        self.btn_add_airport = QPushButton("Agregar Aeropuerto")
        self.btn_remove_airport = QPushButton("Eliminar Aeropuerto")
        self.btn_add_edge = QPushButton("Agregar Vuelo")
        self.btn_remove_edge = QPushButton("Eliminar Vuelo")

        self.btn_connected = QPushButton("Conectividad")
        self.btn_bipartite = QPushButton("Bipartito")
        self.btn_mst = QPushButton("Árbol de Expansión Mínima")

        self.btn_info = QPushButton("Info Aeropuerto")
        self.btn_path = QPushButton("Camino Mínimo")

        buttons = [
            self.btn_add_airport, self.btn_remove_airport,
            self.btn_add_edge, self.btn_remove_edge,
            self.btn_connected, self.btn_bipartite,
            self.btn_mst, self.btn_info, self.btn_path
        ]

        for b in buttons:
            left_layout.addWidget(b)

        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(220)

        # PANEL DINÁMICO
        self.menu_stack = QStackedLayout()

        self.menu_stack.addWidget(self.panel_add_airport())
        self.menu_stack.addWidget(self.panel_remove_airport())
        self.menu_stack.addWidget(self.panel_add_edge())
        self.menu_stack.addWidget(self.panel_remove_edge())
        self.menu_stack.addWidget(self.panel_connected())
        self.menu_stack.addWidget(self.panel_bipartite())
        self.menu_stack.addWidget(self.panel_mst())
        self.menu_stack.addWidget(self.panel_info())
        self.menu_stack.addWidget(self.panel_path())

        layout.addWidget(left_panel)
        layout.addLayout(self.menu_stack)

        container.setLayout(layout)

        # CONEXIONES
        self.btn_add_airport.clicked.connect(lambda: self.menu_stack.setCurrentIndex(0))
        self.btn_remove_airport.clicked.connect(lambda: self.menu_stack.setCurrentIndex(1))
        self.btn_add_edge.clicked.connect(lambda: self.menu_stack.setCurrentIndex(2))
        self.btn_remove_edge.clicked.connect(lambda: self.menu_stack.setCurrentIndex(3))
        self.btn_connected.clicked.connect(lambda: self.menu_stack.setCurrentIndex(4))
        self.btn_bipartite.clicked.connect(lambda: self.menu_stack.setCurrentIndex(5))
        self.btn_mst.clicked.connect(lambda: self.menu_stack.setCurrentIndex(6))
        self.btn_info.clicked.connect(lambda: self.menu_stack.setCurrentIndex(7))
        self.btn_path.clicked.connect(lambda: self.menu_stack.setCurrentIndex(8))

        return container

    # =========================
    # UI HELPERS
    # =========================
    def create_card(self):
        card = QFrame()
        card.setStyleSheet("""
        QFrame {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        color: #2c3e50;  /* 🔥 IMPORTANTE */
        }
        """)
        return card

    def create_title(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
        font-size: 22px;
        font-weight: bold;
        color: #1a252f;
        margin-bottom: 10px;
        """)
        return label

    # =========================
    # PANELES
    # =========================
    def panel_add_airport(self):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title("Agregar Aeropuerto"))

        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Código")

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Nombre")

        btn = QPushButton("Agregar")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(QLabel("Código"))
        layout.addWidget(self.input_code)

        layout.addWidget(QLabel("Nombre"))
        layout.addWidget(self.input_name)

        layout.addWidget(btn)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def panel_remove_airport(self):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title("Eliminar Aeropuerto"))

        self.input_remove = QLineEdit()
        self.input_remove.setPlaceholderText("Código")

        btn = QPushButton("Eliminar")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(QLabel("Código"))
        layout.addWidget(self.input_remove)

        layout.addWidget(btn)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def panel_add_edge(self):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title("Agregar Vuelo"))

        self.edge_origin = QLineEdit()
        self.edge_origin.setPlaceholderText("Código origen")

        self.edge_dest = QLineEdit()
        self.edge_dest.setPlaceholderText("Código destino")

        btn = QPushButton("Agregar Vuelo")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(QLabel("Origen"))
        layout.addWidget(self.edge_origin)

        layout.addWidget(QLabel("Destino"))
        layout.addWidget(self.edge_dest)

        layout.addWidget(btn)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def panel_remove_edge(self):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title("Eliminar Vuelo"))

        self.remove_edge_origin = QLineEdit()
        self.remove_edge_origin.setPlaceholderText("Código origen")

        self.remove_edge_dest = QLineEdit()
        self.remove_edge_dest.setPlaceholderText("Código destino")

        btn = QPushButton("Eliminar Vuelo")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(QLabel("Origen"))
        layout.addWidget(self.remove_edge_origin)

        layout.addWidget(QLabel("Destino"))
        layout.addWidget(self.remove_edge_dest)

        layout.addWidget(btn)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def panel_connected(self):
        return self.simple_panel("Conectividad")

    def panel_bipartite(self):
        return self.simple_panel("Bipartito")

    def panel_mst(self):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title("Árbol de Expansión Mínima"))

        self.mst_result = QLabel("Resultado: -")

        btn = QPushButton("Calcular")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(btn)
        layout.addWidget(self.mst_result)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def panel_info(self):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title("Información de Aeropuerto"))

        self.info_code = QLineEdit()
        self.info_code.setPlaceholderText("Código del aeropuerto")

        self.info_result = QLabel("Resultado: -")

        btn = QPushButton("Buscar")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(QLabel("Código"))
        layout.addWidget(self.info_code)

        layout.addWidget(btn)
        layout.addWidget(self.info_result)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def panel_path(self):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title("Camino Mínimo"))

        self.origin = QLineEdit()
        self.origin.setPlaceholderText("Origen")

        self.dest = QLineEdit()
        self.dest.setPlaceholderText("Destino")

        self.result = QLabel("Resultado: -")

        btn = QPushButton("Calcular")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(QLabel("Origen"))
        layout.addWidget(self.origin)

        layout.addWidget(QLabel("Destino"))
        layout.addWidget(self.dest)

        layout.addWidget(btn)
        layout.addWidget(self.result)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def simple_panel(self, title):
        card = self.create_card()
        layout = QVBoxLayout()

        layout.addWidget(self.create_title(title))

        btn = QPushButton("Ejecutar")
        btn.clicked.connect(self.not_implemented)

        layout.addWidget(btn)
        layout.addStretch()

        card.setLayout(layout)
        return card

    # =========================
    # POPUP
    # =========================
    def not_implemented(self):
        msg = QMessageBox()
        msg.setText("Función no implementada aún")
        msg.exec()

    # =========================
    # DEMO
    # =========================
    def load_demo_data(self):
        a1 = self.graph.create_airport(
            "CTG", "Rafael Núñez", "Cartagena", "Colombia", 10.39, -75.47
        )
        a2 = self.graph.create_airport(
            "BOG", "El Dorado", "Bogotá", "Colombia", 4.70, -74.14
        )

        self.graph.add_vertex(a1)
        self.graph.add_vertex(a2)

        weight = GeoUtils.haversine(a1.lat, a1.lon, a2.lat, a2.lon)
        self.graph.add_edge("CTG", "BOG", weight)

        self.update_map()

    def update_map(self):
        self.map_view.draw_graph(
            self.graph.get_vertices(),
            self.graph.get_edges_for_map()
        )