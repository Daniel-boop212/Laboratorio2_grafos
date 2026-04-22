from PySide6.QtWidgets import QApplication
from src.App import App
from pathlib import Path
from src.ModernMessage import ModernMessage
from src.DataLoader import load_graph_from_csv
from PySide6.QtCore import QThread, Signal

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "flights_final.csv"

class LoadWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            graph = load_graph_from_csv(self.path)
            self.finished.emit(graph)
        except Exception as e:
            self.error.emit(str(e))

class Main:
    def __init__(self):
        self.qt_app = QApplication([])
        self.window = App()

    def run(self):
        self.window.show()
        self.qt_app.exec()
    
    def cargar_grafo(self):
        # 🔄 mostrar loader
        self.window.show_loading("Cargando dataset...")
        self.worker = LoadWorker(DATA_FILE)
        self.worker.finished.connect(self.on_graph_loaded)
        self.worker.error.connect(self.on_load_error)
        self.worker.start()
    
    def on_graph_loaded(self, graph):
        self.window.graph = graph
        self.window.update_map()
        self.window.hide_loading()

    def on_load_error(self, msg):
        self.window.hide_loading()
        ModernMessage.show_message(
        None,
        "Error al cargar",
        msg
        )

main = Main()
main.cargar_grafo()
main.run()