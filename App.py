from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QFrame, QStackedLayout, QMessageBox,
    QGridLayout
)
from ModernMessage import ModernMessage
from PySide6.QtCore import Qt
from GeoUtils import GeoUtils
from MapView import MapView
from Graph import Graph

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rutas Aereas")
        self.setMinimumSize(1300, 750)

        self.current_menu_index = 0
        self.menu_buttons = []

        # Tu StyleSheet que ya corregía los "parches" y colores
        self.setStyleSheet("""
            QWidget { background-color: #edf2f7; color: #1f2d3a; font-family: 'Segoe UI'; }
            QLabel { background-color: transparent; }
            QFrame#sidebar { background-color: #112433; border-radius: 24px; }
            QFrame#menuNav { background-color: #183447; border-radius: 20px; }
            QFrame#heroCard {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #163046, stop: 0.55 #1f5977, stop: 1 #5ea3c4);
                border-radius: 22px;
            }
            QFrame#contentCard { background-color: #ffffff; border: 1px solid #d8e2eb; border-radius: 22px; }
            QFrame#panelCard { background-color: #ffffff; border: 1px solid #dfe7ee; border-radius: 18px; }
            QFrame#resultCard { background-color: #f6fafc; border: 1px solid #d6e4ee; border-radius: 16px; }
            
            QLabel#brandTitle { color: white; font-size: 24px; font-weight: 700; }
            QLabel#brandSubtitle { color: #bdd5e4; font-size: 13px; }
            QLabel#sectionEyebrow { color: #c4d9e6; font-size: 11px; font-weight: 700; text-transform: uppercase; }
            QLabel#heroEyebrow { color: #d8ecf7; font-size: 12px; font-weight: 700; }
            QLabel#heroTitle { color: white; font-size: 32px; font-weight: 700; }
            QLabel#heroBody { color: #ebf7ff; font-size: 14px; }
            QLabel#panelTitle { color: #183447; font-size: 26px; font-weight: 700; }
            QLabel#fieldLabel { color: #274255; font-size: 13px; font-weight: 600; }

            QPushButton { padding: 12px 16px; border-radius: 12px; background-color: #1d6fa5; color: white; font-weight: 700; border: none; }
            QPushButton:hover { background-color: #175b87; }
            QPushButton#navButton { text-align: left; padding: 14px 16px; background-color: transparent; color: #d6e7f0; }
            QPushButton#navButton[active="true"] { background-color: #eef7fc; color: #143246; }
            QPushButton#secondaryButton { background-color: #eef4f7; color: #1d4358; border: 1px solid #cfdee8; }
            
            QLineEdit { padding: 10px 12px; border-radius: 12px; border: 1px solid #ccd7df; background-color: #fbfdfe; }
        """)

        # Inicialización del Grafo
        self.graph = Graph()
        self.init_ui()
        
        # Carga inicial de datos demo
        self.load_demo_data()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        sidebar = self.create_sidebar()

        self.main_stack = QStackedLayout()
        # Ahora el stack incluye el Mapa (Index 0) y el Menú (Index 1)
        self.main_stack.addWidget(self.create_map_view()) 
        self.main_stack.addWidget(self.create_menu_view())

        main_layout.addWidget(sidebar)
        main_layout.addLayout(self.main_stack, 1)
        self.switch_main_view(1) # Empezamos en el centro de operaciones

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(18)

        eyebrow = QLabel("Panel principal")
        eyebrow.setObjectName("sectionEyebrow")
        title = QLabel("Rutas Aereas")
        title.setObjectName("brandTitle")
        
        self.btn_map = QPushButton("Explorar mapa")
        self.btn_menu = QPushButton("Centro de operaciones")

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(self.btn_map)
        layout.addWidget(self.btn_menu)
        layout.addStretch()
        
        self.btn_map.clicked.connect(lambda: self.switch_main_view(0))
        self.btn_menu.clicked.connect(lambda: self.switch_main_view(1))
        return sidebar

    def switch_main_view(self, index):
        self.main_stack.setCurrentIndex(index)

    # --- NUEVO: Vista del Mapa integrada ---
    def create_map_view(self):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.map_view = MapView()
        layout.addWidget(self.map_view)
        return container

    def create_menu_view(self):
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        nav_panel = QFrame()
        nav_panel.setObjectName("menuNav")
        nav_panel.setFixedWidth(290)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(18, 18, 18, 18)

        self.menu_info = [
            ("Agregar Aeropuerto", "Registra un nuevo nodo con su identificador y nombre."),
            ("Eliminar Aeropuerto", "Retira un aeropuerto del grafo y limpia sus conexiones."),
            ("Agregar Vuelo", "Crea una conexion entre dos aeropuertos existentes."),
            ("Eliminar Vuelo", "Quita una ruta especifica del mapa de vuelos."),
            ("Conectividad", "Verifica el estado general de conexion del sistema."),
            ("Bipartito", "Analiza si la estructura del grafo cumple la condicion."),
            ("Arbol de Expansion Minima", "Genera una red base eficiente entre aeropuertos."),
            ("Info Aeropuerto", "Consulta los datos disponibles para un aeropuerto."),
            ("Camino Minimo", "Encuentra la mejor ruta entre origen y destino.")
        ]

        for index, (title, _) in enumerate(self.menu_info):
            button = QPushButton(title)
            button.setObjectName("navButton")
            button.clicked.connect(lambda _, i=index: self.set_menu_panel(i))
            nav_layout.addWidget(button)
            self.menu_buttons.append(button)
        nav_layout.addStretch()

        content_panel = QFrame()
        content_panel.setObjectName("contentCard")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(26, 26, 26, 26)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_card.setMaximumHeight(160) 
        hero_layout = QVBoxLayout(hero_card)

        self.menu_header_title = QLabel()
        self.menu_header_title.setObjectName("heroTitle")
        self.menu_header_description = QLabel()
        self.menu_header_description.setObjectName("heroBody")
        
        hero_layout.addWidget(self.menu_header_title)
        hero_layout.addWidget(self.menu_header_description)
        hero_layout.addStretch()

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

        content_layout.addWidget(hero_card)
        content_layout.addLayout(self.menu_stack, 1)

        layout.addWidget(nav_panel)
        layout.addWidget(content_panel, 1)
        self.set_menu_panel(0)
        return container

    def set_menu_panel(self, index):
        self.menu_stack.setCurrentIndex(index)
        title, description = self.menu_info[index]
        self.menu_header_title.setText(title)
        self.menu_header_description.setText(description)
        for i, btn in enumerate(self.menu_buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # --- HELPERS DE UI ---
    def create_title(self, text, description=None):
        header = QFrame()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel(text)
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        if description:
            body = QLabel(description)
            body.setObjectName("panelDescription")
            layout.addWidget(body)
        return header

    def create_form_row(self, label_text, field):
        wrapper = QFrame()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        field.setMaximumHeight(42)
        layout.addWidget(field)
        return wrapper

    def create_result_box(self, text="-"):
        box = QFrame()
        box.setObjectName("resultCard")
        layout = QVBoxLayout(box)
        label = QLabel("Resultado")
        label.setObjectName("resultLabel")
        value = QLabel(text)
        value.setWordWrap(True)
        layout.addWidget(label)
        layout.addWidget(value)
        return box, value

    def build_action_panel(self, title, description, fields, button_text, result_label=None):
        card = QFrame()
        card.setObjectName("panelCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        
        layout.addWidget(self.create_title(title, description))

        form_layout = QGridLayout()
        for index, (label_text, field) in enumerate(fields):
            row, col = index // 2, index % 2
            form_layout.addWidget(self.create_form_row(label_text, field), row, col)
        layout.addLayout(form_layout)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn = QPushButton(button_text)
        btn.setMinimumWidth(180)
        if title == "Agregar aeropuerto":
            btn.clicked.connect(lambda: self.panel_add_airport_helper(
                self.input_code.text(), 
                self.input_name.text(),
                self.input_city.text(),
                self.input_country.text(),
                self.input_lat.text(),
                self.input_lon.text()
            ))
        elif title == "Eliminar aeropuerto":
            btn.clicked.connect(lambda: self.panel_remove_airport_helper(
                self.input_remove.text()
            ))
        elif title == "Agregar vuelo":
            btn.clicked.connect(lambda: self.panel_add_edge_helper(
                self.edge_origin.text(), 
                self.edge_dest.text()
            ))
        elif title == "Eliminar vuelo":
            btn.clicked.connect(lambda: self.panel_remove_edge_helper(
                self.remove_edge_origin.text(), 
                self.remove_edge_dest.text()
            ))
        else:
            btn.clicked.connect(self.not_implemented)
        btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        res_widget = None
        if result_label is not None:
            result_box, res_widget = self.create_result_box(result_label)
            layout.addWidget(result_box)

        layout.addStretch() 
        return card

    # --- PANELES ---
    def panel_add_airport(self):
        self.input_code = QLineEdit()
        self.input_name = QLineEdit()
        self.input_city = QLineEdit()
        self.input_country = QLineEdit()
        self.input_lat = QLineEdit()
        self.input_lon = QLineEdit()
        return self.build_action_panel("Agregar aeropuerto", "Crea un nuevo nodo.",
                                      [("Codigo", self.input_code), ("Nombre", self.input_name), ("Ciudad", self.input_city), ("Pais", self.input_country), ("Latitud", self.input_lat), ("Longitud", self.input_lon)], "Agregar")
    
    def panel_add_airport_helper(self, code, name, city, country, lat, lon):
        if not (code and name and city and country and lat and lon):
            ModernMessage.show_message(self, "¡Error!", "Por favor, rellena todos los campos.")
            return
        if self.graph.find_index(code) != -1:
            ModernMessage.show_message(self, "¡Error!", f"El aeropuerto {code} ya existe.")
            return
        lat = float(lat)
        lon = float(lon)
        self.graph.add_vertex(self.graph.create_airport(code, name, city, country, lat, lon))
        self.update_map()
        ModernMessage.show_message(self, "¡Éxito!", f"El aeropuerto {code} ha sido integrado al sistema.")

    def panel_remove_airport(self):
        self.input_remove = QLineEdit()
        return self.build_action_panel("Eliminar aeropuerto", "Retira un nodo.", [("Codigo", self.input_remove)], "Eliminar")
    
    def panel_remove_airport_helper(self, code):
        if not code:
            ModernMessage.show_message(self, "¡Error!", "Por favor, rellena todos los campos.")
            return
        if self.graph.find_index(code) == -1:
            ModernMessage.show_message(self, "¡Error!", f"El aeropuerto {code} no existe.")
            return
        self.graph.remove_airport(self.graph.find_airport(code))
        self.update_map()
        ModernMessage.show_message(self, "¡Éxito!", f"El aeropuerto {code} ha sido eliminado.")

    def panel_add_edge(self):
        self.edge_origin = QLineEdit()
        self.edge_dest = QLineEdit()
        return self.build_action_panel("Agregar vuelo", "Conecta dos nodos.", 
                                      [("Origen", self.edge_origin), ("Destino", self.edge_dest)], "Conectar")
    
    def panel_add_edge_helper(self, origin, dest):
        if not (origin and dest):
            ModernMessage.show_message(self, "¡Error!", "Por favor, rellena todos los campos.")
            return
        if origin == dest:
            ModernMessage.show_message(self, "¡Error!", "El origen y el destino son iguales.")
            return
        if self.graph.find_index(origin) == -1 or self.graph.find_index(dest) == -1:
            ModernMessage.show_message(self, "¡Error!", "El origen o el destino no existe.")
            return
        airport1 = self.graph.find_airport(origin)
        airport2 = self.graph.find_airport(dest)
        dist = GeoUtils.haversine(airport1.lat, airport1.lon, airport2.lat, airport2.lon)
        if self.graph.has_edge(origin, dest):
            ModernMessage.show_message(self, "¡Error!", f"Ya existe un vuelo {origin} <-> {dest}.")
            return
        self.graph.add_edge(self.graph.create_edge(airport1, airport2, dist))
        self.update_map()
        ModernMessage.show_message(self, "¡Éxito!", f"El vuelo {origin} <-> {dest} ha sido integrado al sistema.")

    def panel_remove_edge(self):
        self.remove_edge_origin = QLineEdit()
        self.remove_edge_dest = QLineEdit()
        return self.build_action_panel("Eliminar vuelo", "Quita una conexion.", 
                                      [("Origen", self.remove_edge_origin), ("Destino", self.remove_edge_dest)], "Quitar")
    
    def panel_remove_edge_helper(self, origin, dest):
        if not (origin and dest):
            ModernMessage.show_message(self, "¡Error!", "Por favor, rellena todos los campos.")
            return
        if origin == dest:
            ModernMessage.show_message(self, "¡Error!", "El origen y el destino son iguales.")
            return
        if self.graph.find_index(origin) == -1 or self.graph.find_index(dest) == -1:
            ModernMessage.show_message(self, "¡Error!", "El origen o el destino no existe.")
            return
        edge = self.graph.find_edge(origin, dest)
        if edge is None:
            ModernMessage.show_message(self, "¡Error!", f"No existe un vuelo {origin} <-> {dest}.")
            return
        self.graph.remove_edge(edge)
        ModernMessage.show_message(self, "¡Éxito!", f"El vuelo {origin} <-> {dest} ha sido eliminado.")
        self.update_map()

    def panel_connected(self):
        card = self.build_action_panel("Conectividad", "Analiza el grafo.", [], "Analizar", "Sin datos.")
        self.connected_result = card 
        return card

    def panel_bipartite(self):
        return self.build_action_panel("Bipartito", "Comprueba biparticion.", [], "Comprobar", "Sin datos.")

    def panel_mst(self):
        return self.build_action_panel("Arbol de Expansion Minima", "Calcula el Arbol de Expansion.", [], "Calcular", "Sin datos.")

    def panel_info(self):
        self.info_code = QLineEdit()
        return self.build_action_panel("Informacion", "Consulta datos.", [("Codigo", self.info_code)], "Consultar", "Sin datos.")

    def panel_path(self):
        self.origin = QLineEdit()
        self.dest = QLineEdit()
        return self.build_action_panel("Camino Minimo", "Ruta optima.", [("Origen", self.origin), ("Destino", self.dest)], "Calcular", "Sin ruta.")

    def not_implemented(self):
            ModernMessage.show_message(self, "Pendiente", "Funcion no implementada.")

    # --- LÓGICA DE DATOS Y MAPA ---
    def load_demo_data(self):
        """Carga datos de ejemplo y actualiza el mapa."""
        # Ejemplo: CTG -> BOG
        a1 = self.graph.create_airport("CTG", "Rafael Nunez", "Cartagena", "Colombia", 10.39, -75.47)
        a2 = self.graph.create_airport("BOG", "El Dorado", "Bogota", "Colombia", 4.70, -74.14)
        
        self.graph.add_vertex(a1)
        self.graph.add_vertex(a2)
        
        dist = GeoUtils.haversine(a1.lat, a1.lon, a2.lat, a2.lon)
        self.graph.add_edge(self.graph.create_edge(a1, a2, dist))
        
        self.update_map()

    def update_map(self):
        """Refresca la visualización del mapa."""
        if hasattr(self, 'map_view'):
            self.map_view.draw_graph(
                self.graph.get_vertices(), 
                self.graph.get_edges_for_map()
            )