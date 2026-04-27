import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

# Agregar la ruta actual al path
sys.path.insert(0, os.path.dirname(__file__))

from src.App import App
from src.DataLoader import load_graph_from_csv

def main():
    try:
        
        app = QApplication(sys.argv)
        
        print("Creando ventana principal...")
        window = App()
        
        # Intentar cargar los datos
        csv_paths = [
            'data/flights_final.csv',
            '../data/flights_final.csv',
            os.path.join(os.path.dirname(__file__), 'data', 'flights_final.csv'),
            os.path.join(os.path.dirname(__file__), '..', 'data', 'flights_final.csv'),
        ]
        
        csv_loaded = False
        for csv_path in csv_paths:
            if os.path.exists(csv_path):
                try:
                    print(f"Cargando datos desde: {csv_path}")
                    window.graph = load_graph_from_csv(csv_path)
                    print(f"Éxito: {window.graph.vertex_count()} aeropuertos cargados")
                    print(f"{len(window.graph.get_routes())} rutas disponibles")
                    csv_loaded = True
                    break
                except Exception as e:
                    print(f"Error cargando {csv_path}: {e}")
        
        if not csv_loaded:
            print("ADVERTENCIA: No se encontró el archivo flights_final.csv")
            print("El grafo estará vacío. Las funcionalidades no funcionarán.")
            QMessageBox.warning(window, "Datos no encontrados",
                "No se encontró el archivo flights_final.csv\n\n"
                "Asegúrate de que el archivo esté en la carpeta 'data/'\n"
                "El programa funcionará pero el grafo estará vacío.")
        
        window.show()
        print("Ventana mostrada correctamente")
        print("=" * 50)
        
        sys.exit(app.exec())
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()