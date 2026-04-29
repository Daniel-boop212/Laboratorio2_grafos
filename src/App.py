from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QFrame, QStackedLayout, QMessageBox,
    QGridLayout, QApplication, QProgressBar, QScrollArea
)

from .ModernMessage import ModernMessage
from PySide6.QtCore import Qt, QThread, Signal
from .MapView import MapView
from .Graph import Graph
from .algorithms import (
    shortest_path_between,
    connected_components,
    is_bipartite,
    minimum_spanning_tree,
    top_farthest_airports,
)


# ─────────────────────────────────────────────
# Worker: camino mínimo en hilo separado
# ─────────────────────────────────────────────
class PathWorker(QThread):
    finished = Signal(dict)

    def __init__(self, graph, origin, dest):
        super().__init__()
        self.graph  = graph
        self.origin = origin
        self.dest   = dest

    def run(self):
        result = shortest_path_between(self.graph, self.origin, self.dest)
        self.finished.emit(result)


# ─────────────────────────────────────────────
# Worker: análisis de conectividad en hilo separado
# ─────────────────────────────────────────────
class ConnectivityWorker(QThread):
    finished = Signal(object)

    def __init__(self, graph):
        super().__init__()
        self.graph = graph

    def run(self):
        result = connected_components(self.graph)
        self.finished.emit(result)


# ─────────────────────────────────────────────
# Worker: MST en hilo separado
# ─────────────────────────────────────────────
class MSTWorker(QThread):
    finished = Signal(object)

    def __init__(self, graph, components):
        super().__init__()
        self.graph      = graph
        self.components = components

    def run(self):
        results = []
        for comp in self.components:
            weight, edges = minimum_spanning_tree(self.graph, comp)
            results.append((len(comp), weight, edges))
        self.finished.emit(results)


# ─────────────────────────────────────────────
# Ventana principal
# ─────────────────────────────────────────────
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rutas Aéreas — Lab 2")
        self.setMinimumSize(1300, 750)

        self.current_menu_index = 0
        self.menu_buttons       = []
        self._components_cache  = None   # cache de componentes ya calculadas

        self.setStyleSheet("""
            QWidget { background-color: #edf2f7; color: #1f2d3a; font-family: 'Segoe UI'; }
            QLabel  { background-color: transparent; }
            QFrame#sidebar   { background-color: #112433; border-radius: 24px; }
            QFrame#menuNav   { background-color: #183447; border-radius: 20px; }
            QFrame#heroCard  {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #163046, stop:0.55 #1f5977, stop:1 #5ea3c4);
                border-radius: 22px;
            }
            QFrame#contentCard { background-color: #ffffff; border: 1px solid #d8e2eb; border-radius: 22px; }
            QFrame#panelCard   { background-color: #ffffff; border: 1px solid #dfe7ee; border-radius: 18px; }
            QFrame#resultCard  { background-color: #f6fafc; border: 1px solid #d6e4ee; border-radius: 16px; }

            QLabel#brandTitle    { color: white; font-size: 24px; font-weight: 700; }
            QLabel#brandSubtitle { color: #bdd5e4; font-size: 13px; }
            QLabel#sectionEyebrow{ color: #c4d9e6; font-size: 11px; font-weight: 700; }
            QLabel#heroTitle     { color: white;  font-size: 32px; font-weight: 700; }
            QLabel#heroBody      { color: #ebf7ff; font-size: 14px; }
            QLabel#panelTitle    { color: #183447; font-size: 26px; font-weight: 700; }
            QLabel#fieldLabel    { color: #274255; font-size: 13px; font-weight: 600; }

            QPushButton { padding: 12px 16px; border-radius: 12px; background-color: #1d6fa5;
                          color: white; font-weight: 700; border: none; }
            QPushButton:hover { background-color: #175b87; }
            QPushButton#navButton { text-align: left; padding: 14px 16px;
                                    background-color: transparent; color: #d6e7f0; }
            QPushButton#navButton[active="true"] { background-color: #eef7fc; color: #143246; }

            QLineEdit { padding: 10px 12px; border-radius: 12px;
                        border: 1px solid #ccd7df; background-color: #fbfdfe; }

            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 10px; background: transparent; margin: 4px; }
            QScrollBar::handle:vertical { background: #b8c7d6; border-radius: 5px; min-height: 40px; }
            QScrollBar::handle:vertical:hover { background: #8fb1c9; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.graph = Graph()
        
        # Cargar datos del grafo
        from .DataLoader import load_graph_from_csv
        import os
        
        csv_path = 'data/flights_final.csv'
        if os.path.exists(csv_path):
            try:
                self.graph = load_graph_from_csv(csv_path)
                print(f"Datos cargados: {self.graph.vertex_count()} aeropuertos, {len(self.graph.get_routes())} rutas")
            except Exception as e:
                print(f"Error al cargar datos: {e}")
                ModernMessage.show_message(self, "Error", f"Error al cargar datos: {e}")
        else:
            print(f"No se encontró el archivo: {csv_path}")
            ModernMessage.show_message(self, "Advertencia", f"No se encontró el archivo {csv_path}\nEl grafo estará vacío.")
        
        self.init_ui()

    # ─────────────────────────────────────────
    # LAYOUT PRINCIPAL
    # ─────────────────────────────────────────
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        main_layout.addWidget(self.create_sidebar())

        self.main_stack = QStackedLayout()
        self.main_stack.addWidget(self.create_map_view())   # index 0
        self.main_stack.addWidget(self.create_menu_view())  # index 1
        main_layout.addLayout(self.main_stack, 1)

        self.switch_main_view(1)

    # ─────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(18)

        eyebrow = QLabel("Panel principal")
        eyebrow.setObjectName("sectionEyebrow")
        title = QLabel("Rutas Aéreas")
        title.setObjectName("brandTitle")

        btn_map   = QPushButton("Explorar mapa")
        btn_menu  = QPushButton("Centro de operaciones")
        btn_reset = QPushButton("Reiniciar mapa")

        btn_map.clicked.connect(lambda checked=False: self.switch_main_view(0))
        btn_menu.clicked.connect(lambda checked=False: self.switch_main_view(1))
        btn_reset.clicked.connect(self.reset_map)

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(btn_map)
        layout.addWidget(btn_menu)
        layout.addWidget(btn_reset)
        layout.addStretch()
        return sidebar

    # ─────────────────────────────────────────
    # VISTA MAPA
    # ─────────────────────────────────────────
    def create_map_view(self):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.map_view = MapView()
        layout.addWidget(self.map_view)
        return container

    # ─────────────────────────────────────────
    # VISTA MENÚ
    # ─────────────────────────────────────────
    def create_menu_view(self):
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        # ── Nav lateral ──────────────────────
        nav_panel = QFrame()
        nav_panel.setObjectName("menuNav")
        nav_panel.setFixedWidth(290)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(18, 18, 18, 18)

        self.menu_info = [
            ("Conectividad",              "Verifica si el grafo es conexo y lista sus componentes."),
            ("Bipartito",                 "Comprueba si el grafo (o su componente mayor) es bipartito."),
            ("Árbol de Expansión Mínima", "Calcula el MST de cada componente y su peso total."),
            ("Info Aeropuerto",           "Consulta datos del aeropuerto y los 10 destinos más lejanos."),
            ("Camino Mínimo",             "Encuentra y visualiza la ruta óptima entre dos aeropuertos."),
        ]

        for index, (title, _) in enumerate(self.menu_info):
            btn = QPushButton(title)
            btn.setObjectName("navButton")
            btn.clicked.connect(lambda checked=False, i=index: self.set_menu_panel(i))
            nav_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        nav_layout.addStretch()

        # ── Contenido central ────────────────
        content_panel = QFrame()
        content_panel.setObjectName("contentCard")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(26, 26, 26, 26)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_card.setMaximumHeight(140)
        hero_layout = QVBoxLayout(hero_card)
        self.menu_header_title       = QLabel()
        self.menu_header_title.setObjectName("heroTitle")
        self.menu_header_description = QLabel()
        self.menu_header_description.setObjectName("heroBody")
        hero_layout.addWidget(self.menu_header_title)
        hero_layout.addWidget(self.menu_header_description)
        hero_layout.addStretch()

        self.menu_stack = QStackedLayout()
        self.menu_stack.addWidget(self.wrap_scroll(self.panel_connected()))
        self.menu_stack.addWidget(self.wrap_scroll(self.panel_bipartite()))
        self.menu_stack.addWidget(self.wrap_scroll(self.panel_mst()))
        self.menu_stack.addWidget(self.wrap_scroll(self.panel_info()))
        self.menu_stack.addWidget(self.wrap_scroll(self.panel_path()))

        content_layout.addWidget(hero_card)
        content_layout.addLayout(self.menu_stack, 1)

        layout.addWidget(nav_panel)
        layout.addWidget(content_panel, 1)
        self.set_menu_panel(0)
        return container

    # ─────────────────────────────────────────
    # HELPERS UI
    # ─────────────────────────────────────────
    def switch_main_view(self, index, _=None):
        self.main_stack.setCurrentIndex(index)

    def set_menu_panel(self, index, _=None):
        self.menu_stack.setCurrentIndex(index)
        title, description = self.menu_info[index]
        self.menu_header_title.setText(title)
        self.menu_header_description.setText(description)
        for i, btn in enumerate(self.menu_buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def wrap_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(widget)
        return scroll

    def reset_map(self, _=None):
        if hasattr(self, "map_view") and self.graph.vertex_count() > 0:
            self.map_view.draw_graph(self.graph)

    def update_map(self):
        if hasattr(self, "map_view"):
            self.map_view.draw_graph(self.graph)

    def show_loading(self, text="Cargando..."):
        if not hasattr(self, "loading_overlay"):
            self.loading_overlay = QFrame(self)
            self.loading_overlay.setStyleSheet(
                "background-color: rgba(0,0,0,120); border-radius: 20px;"
            )
            self.loading_overlay.setGeometry(self.rect())
            lay = QVBoxLayout(self.loading_overlay)
            self.loading_label = QLabel(text)
            self.loading_label.setStyleSheet("color: white; font-size: 20px;")
            self.loading_label.setAlignment(Qt.AlignCenter)
            self.loading_bar = QProgressBar()
            self.loading_bar.setRange(0, 0)
            lay.addStretch()
            lay.addWidget(self.loading_label)
            lay.addWidget(self.loading_bar)
            lay.addStretch()
        self.loading_label.setText(text)
        self.loading_overlay.show()

    def hide_loading(self):
        if hasattr(self, "loading_overlay"):
            self.loading_overlay.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "loading_overlay"):
            self.loading_overlay.setGeometry(self.rect())

    # ── Constructores de cards ───────────────
    def _make_card(self):
        card = QFrame()
        card.setObjectName("panelCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(14)
        return card, lay

    def _title_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("panelTitle")
        return lbl

    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def _result_box(self, placeholder="Sin datos."):
        box = QFrame()
        box.setObjectName("resultCard")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(16, 14, 16, 14)
        lbl_title = QLabel("Resultado")
        lbl_title.setObjectName("fieldLabel")
        lbl_val = QLabel(placeholder)
        lbl_val.setWordWrap(True)
        lbl_val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(lbl_title)
        lay.addWidget(lbl_val)
        return box, lbl_val

    def _loading_widgets(self, text):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #1d6fa5; font-weight: bold;")
        lbl.hide()
        bar = QProgressBar()
        bar.setRange(0, 0)
        bar.setTextVisible(False)
        bar.hide()
        return lbl, bar

    # ─────────────────────────────────────────
    # PANEL 1 — CONECTIVIDAD
    # ─────────────────────────────────────────
    def panel_connected(self):
        card, lay = self._make_card()
        lay.addWidget(self._title_label("Conectividad"))

        btn = QPushButton("Analizar")
        btn.setMinimumWidth(180)
        btn.clicked.connect(self._run_connectivity)

        self._conn_loading, self._conn_bar = self._loading_widgets("Analizando conectividad...")
        result_box, self._conn_result = self._result_box()

        lay.addWidget(btn, 0, Qt.AlignLeft)
        lay.addWidget(self._conn_loading)
        lay.addWidget(self._conn_bar)
        lay.addWidget(result_box)
        lay.addStretch()
        return card

    def _run_connectivity(self, _=None):
        if not self.graph.vertex_count():
            ModernMessage.show_message(self, "Error", "El grafo está vacío.")
            return
        self._conn_loading.show()
        self._conn_bar.show()
        self._conn_result.setText("")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self._conn_worker = ConnectivityWorker(self.graph)
        self._conn_worker.finished.connect(self._on_connectivity_done)
        self._conn_worker.start()

    def _on_connectivity_done(self, components):
        self._conn_loading.hide()
        self._conn_bar.hide()
        QApplication.restoreOverrideCursor()

        # Guardar en cache para reutilizar en bipartito y MST
        self._components_cache = components

        n_comp = len(components)
        if n_comp == 1:
            text = (
                f"   El grafo ES CONEXO.\n"
                f"   Una sola componente con {len(components[0])} vértices."
            )
        else:
            text = f" El grafo NO es conexo.\n\nNúmero de componentes: {n_comp}\n\n"
            # Ordenar por tamaño descendente para mejor legibilidad
            sorted_comps = sorted(components, key=len, reverse=True)
            for i, comp in enumerate(sorted_comps, 1):
                text += f"Componente {i}: {len(comp)} vértice(s)\n"

        self._conn_result.setText(text)

    # ─────────────────────────────────────────
    # PANEL 2 — BIPARTITO
    # ─────────────────────────────────────────
    def panel_bipartite(self):
        card, lay = self._make_card()
        lay.addWidget(self._title_label("Verificación Bipartita"))

        btn = QPushButton("Comprobar")
        btn.setMinimumWidth(180)
        btn.clicked.connect(self._run_bipartite)

        self._bip_loading, self._bip_bar = self._loading_widgets("Comprobando bipartición...")
        result_box, self._bip_result = self._result_box()

        lay.addWidget(btn, 0, Qt.AlignLeft)
        lay.addWidget(self._bip_loading)
        lay.addWidget(self._bip_bar)
        lay.addWidget(result_box)
        lay.addStretch()
        return card

    def _run_bipartite(self, _=None):
        if not self.graph.vertex_count():
            ModernMessage.show_message(self, "Error", "El grafo está vacío.")
            return

        self._bip_loading.show()
        self._bip_bar.show()
        self._bip_result.setText("")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Si no hay componentes cacheadas, calcularlas primero
        if self._components_cache is None:
            self._components_cache = connected_components(self.graph)

        components = self._components_cache

        if len(components) == 1:
            # Grafo conexo: verificar todo
            result, _ = is_bipartite(self.graph, components[0])
            text = (
                "El grafo es BIPARTITO."
                if result
                else " El grafo NO es bipartito (contiene un ciclo de longitud impar)."
            )
        else:
            # Verificar la componente más grande
            largest = max(components, key=len)
            result, _ = is_bipartite(self.graph, largest)
            scope = f"componente más grande ({len(largest)} vértices)"
            text = (
                f"El grafo tiene {len(components)} componentes.\n\n"
                f"La {scope} "
                + (" ES BIPARTITA." if result else " NO es bipartita.")
            )

        self._bip_loading.hide()
        self._bip_bar.hide()
        QApplication.restoreOverrideCursor()
        self._bip_result.setText(text)

    # ─────────────────────────────────────────
    # PANEL 3 — ÁRBOL DE EXPANSIÓN MÍNIMA
    # ─────────────────────────────────────────
    def panel_mst(self):
        card, lay = self._make_card()
        lay.addWidget(self._title_label("Árbol de Expansión Mínima"))

        btn = QPushButton("Calcular MST")
        btn.setMinimumWidth(180)
        btn.clicked.connect(self._run_mst)

        self._mst_loading, self._mst_bar = self._loading_widgets("Calculando MST...")
        result_box, self._mst_result = self._result_box()

        lay.addWidget(btn, 0, Qt.AlignLeft)
        lay.addWidget(self._mst_loading)
        lay.addWidget(self._mst_bar)
        lay.addWidget(result_box)
        lay.addStretch()
        return card

    def _run_mst(self, _=None):
        if not self.graph.vertex_count():
            ModernMessage.show_message(self, "Error", "El grafo está vacío.")
            return

        self._mst_loading.show()
        self._mst_bar.show()
        self._mst_result.setText("")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        if self._components_cache is None:
            self._components_cache = connected_components(self.graph)

        self._mst_worker = MSTWorker(self.graph, self._components_cache)
        self._mst_worker.finished.connect(self._on_mst_done)
        self._mst_worker.start()

    def _on_mst_done(self, results):
        self._mst_loading.hide()
        self._mst_bar.hide()
        QApplication.restoreOverrideCursor()

        # results: list of (n_vertices, total_weight, edges)
        sorted_res = sorted(results, key=lambda x: x[0], reverse=True)

        if len(sorted_res) == 1:
            n, w, _ = sorted_res[0]
            text = (
                f"El grafo es conexo ({n} vértices).\n\n"
                f"Peso total del MST: {w:,.2f} km"
            )
        else:
            text = f"El grafo tiene {len(sorted_res)} componentes.\n\n"
            for i, (n, w, _) in enumerate(sorted_res, 1):
                text += f"Componente {i}: {n} vértice(s) — MST = {w:,.2f} km\n"

        self._mst_result.setText(text)

    # ─────────────────────────────────────────
    # PANEL 4 — INFO AEROPUERTO
    # ─────────────────────────────────────────
    def panel_info(self):
        card, lay = self._make_card()
        lay.addWidget(self._title_label("Info Aeropuerto"))

        self._info_code = QLineEdit()
        self._info_code.setPlaceholderText("Código IATA, ej: BOG")

        row = QVBoxLayout()
        row.addWidget(self._field_label("Código del aeropuerto"))
        row.addWidget(self._info_code)
        lay.addLayout(row)

        btn = QPushButton("Consultar")
        btn.setMinimumWidth(180)
        btn.clicked.connect(self._run_info)

        self._info_loading, self._info_bar = self._loading_widgets("Calculando caminos...")
        result_box, self._info_result = self._result_box()

        lay.addWidget(btn, 0, Qt.AlignLeft)
        lay.addWidget(self._info_loading)
        lay.addWidget(self._info_bar)
        lay.addWidget(result_box)
        lay.addStretch()
        return card

    def _run_info(self, _=None):
        code = self._info_code.text().strip().upper()
        if not code:
            ModernMessage.show_message(self, "Error", "Ingresa un código de aeropuerto.")
            return

        airport = self.graph.find_airport(code)
        if airport is None:
            ModernMessage.show_message(self, "Error", f"No se encontró el aeropuerto '{code}'.")
            return

        self._info_loading.show()
        self._info_bar.show()
        self._info_result.setText("")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Ejecutar en hilo para no bloquear la UI
        class InfoWorker(QThread):
            finished = Signal(object, object)
            def __init__(self, graph, code, airport):
                super().__init__()
                self.graph   = graph
                self.code    = code
                self.airport = airport
            def run(self):
                top10 = top_farthest_airports(self.graph, self.code, top_n=10)
                self.finished.emit(self.airport, top10)

        self._info_worker = InfoWorker(self.graph, code, airport)
        self._info_worker.finished.connect(self._on_info_done)
        self._info_worker.start()

    def _on_info_done(self, airport, top10):
        self._info_loading.hide()
        self._info_bar.hide()
        QApplication.restoreOverrideCursor()

        text  = "    INFORMACIÓN DEL AEROPUERTO\n"
        text += f"  Código   : {airport.code}\n"
        text += f"  Nombre   : {airport.name}\n"
        text += f"  Ciudad   : {airport.city}\n"
        text += f"  País     : {airport.country}\n"
        text += f"  Latitud  : {airport.lat}\n"
        text += f"  Longitud : {airport.lon}\n\n"

        text += " TOP-10 AEROPUERTOS MÁS LEJANOS (por camino mínimo)\n"
        text += "─" * 55 + "\n"

        if not top10:
            text += "  No hay aeropuertos alcanzables."
        else:
            for rank, (ap, dist) in enumerate(top10, 1):
                text += (
                    f"  {rank:2}. [{ap.code}] {ap.name}\n"
                    f"      {ap.city}, {ap.country}\n"
                    f"      Lat: {ap.lat}  Lon: {ap.lon}\n"
                    f"      Distancia: {dist:,.2f} km\n\n"
                )

        self._info_result.setText(text)

    # ─────────────────────────────────────────
    # PANEL 5 — CAMINO MÍNIMO
    # ─────────────────────────────────────────
    def panel_path(self):
        card, lay = self._make_card()
        lay.addWidget(self._title_label("Camino Mínimo"))

        self._path_origin = QLineEdit()
        self._path_origin.setPlaceholderText("Código IATA origen, ej: BOG")
        self._path_dest   = QLineEdit()
        self._path_dest.setPlaceholderText("Código IATA destino, ej: JFK")

        grid = QGridLayout()
        col1 = QVBoxLayout()
        col1.addWidget(self._field_label("Aeropuerto origen"))
        col1.addWidget(self._path_origin)
        col2 = QVBoxLayout()
        col2.addWidget(self._field_label("Aeropuerto destino"))
        col2.addWidget(self._path_dest)
        grid.addLayout(col1, 0, 0)
        grid.addLayout(col2, 0, 1)
        lay.addLayout(grid)

        btn = QPushButton("Calcular ruta")
        btn.setMinimumWidth(180)
        btn.clicked.connect(self._run_path)

        self._path_loading, self._path_bar = self._loading_widgets("Calculando ruta...")
        result_box, self._path_result = self._result_box()

        lay.addWidget(btn, 0, Qt.AlignLeft)
        lay.addWidget(self._path_loading)
        lay.addWidget(self._path_bar)
        lay.addWidget(result_box)
        lay.addStretch()
        return card

    def _run_path(self, _=None):
        origin = self._path_origin.text().strip().upper()
        dest   = self._path_dest.text().strip().upper()

        if not origin or not dest:
            ModernMessage.show_message(self, "Error", "Completa los dos campos.")
            return
        if origin == dest:
            ModernMessage.show_message(self, "Error", "Origen y destino son iguales.")
            return
        if self.graph.find_airport(origin) is None:
            ModernMessage.show_message(self, "Error", f"No se encontró el aeropuerto '{origin}'.")
            return
        if self.graph.find_airport(dest) is None:
            ModernMessage.show_message(self, "Error", f"No se encontró el aeropuerto '{dest}'.")
            return

        self._path_loading.show()
        self._path_bar.show()
        self._path_result.setText("")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self._path_worker = PathWorker(self.graph, origin, dest)
        self._path_worker.finished.connect(self._on_path_done)
        self._path_worker.start()

    def _on_path_done(self, result):
        self._path_loading.hide()
        self._path_bar.hide()
        QApplication.restoreOverrideCursor()

        if not result["reachable"]:
            self._path_result.setText("No existe ruta entre esos aeropuertos.")
            return

        path = result["path"]
        dist = result["distance"]

        # Mostrar en el mapa y cambiar a la vista del mapa
        self.map_view.draw_path(self.graph, path)
        self.switch_main_view(0)

        # Detalles de las escalas
        lines = [
            f"   Distancia total: {dist:,.2f} km",
            f"   Escalas: {len(path) - 2}",
            f"   Ruta: {' → '.join(path)}\n",
            "─" * 50,
        ]
        for code in path:
            ap = self.graph.find_airport(code)
            if ap:
                lines.append(
                    f"  [{ap.code}] {ap.name} — {ap.city}, {ap.country}\n"
                    f"         Lat: {ap.lat}  Lon: {ap.lon}"
                )
        self._path_result.setText("\n".join(lines))