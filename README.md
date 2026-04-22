# Laboratorio 2 - Grafo de rutas aéreas

Esta es una versión reorganizada y lista para entregar del proyecto del laboratorio. Conserva la idea central del código base, pero quedó adaptada a una estructura más limpia tipo proyecto académico, con `main.py`, carpeta `src/`, carpeta `data/`, interfaz con `customtkinter` y mapas HTML con `folium`.

El proyecto construye un grafo simple, no dirigido y ponderado a partir del archivo `flights_final.csv`, donde cada vértice representa un aeropuerto y cada arista representa una ruta aérea. El peso de cada arista se calcula con la distancia geográfica entre coordenadas usando la fórmula de Haversine.

## Qué hace el proyecto

La aplicación permite:

- construir el grafo desde el dataset `data/flights_final.csv`
- consultar nodos del grafo por código y ver su grado y vecinos
- determinar si el grafo es conexo
- mostrar el número de componentes y el tamaño de cada una cuando no es conexo
- verificar si el grafo es bipartito, o si hay varias componentes, verificar la componente más grande
- calcular el peso del árbol de expansión mínima por componente
- seleccionar un primer aeropuerto por código
- mostrar la información completa del aeropuerto seleccionado
- mostrar los 10 aeropuertos cuyos caminos mínimos desde el nodo 1 son los más largos
- seleccionar un segundo aeropuerto por código
- calcular el camino mínimo entre nodo 1 y nodo 2
- generar un mapa general con la geolocalización de los aeropuertos
- generar un mapa del camino mínimo resaltando origen, intermedios y destino

## Estructura del proyecto

```text
lab_grafos_aeropuertos_convertido/
│
├── main.py
├── README.md
├── requirements.txt
├── data/
│   └── flights_final.csv
├── maps/
│   └── (se generan aquí los HTML)
└── src/
    ├── __init__.py
    ├── airport.py
    ├── graph.py
    ├── loader.py
    ├── algorithms.py
    ├── map_view.py
    └── interface.py
```

## Instalación

Asegúrate de tener Python 3.11 o superior.

Instala dependencias:

```bash
pip install -r requirements.txt
```

Dependencias principales:

- `customtkinter`
- `folium`

## Cómo ejecutar

Desde la carpeta raíz del proyecto:

```bash
python main.py
```

## Qué hace cada botón

- `Resumen del Grafo`: muestra número de vértices, aristas y componentes.
- `Nodos del Grafo`: permite consultar un nodo por código, ver grado, vecinos y una muestra de códigos disponibles.
- `Conexidad`: revisa si el grafo es conexo y lista las componentes.
- `Bipartito`: verifica si la componente evaluada es bipartita.
- `MST`: calcula el árbol de expansión mínima por componente.
- `Seleccionar Nodo 1`: guarda el primer aeropuerto para los cálculos posteriores.
- `Top 10 caminos más largos desde Nodo 1`: calcula los caminos mínimos más largos desde el nodo 1.
- `Seleccionar Nodo 2`: guarda el segundo aeropuerto.
- `Camino mínimo Nodo 1 -> Nodo 2`: calcula y muestra la ruta mínima entre ambos nodos.
- `Ver mapa general`: abre un HTML con todos los nodos y una muestra de aristas para que el mapa no se vuelva pesado.
- `Ver mapa del camino`: abre el mapa del camino mínimo calculado.

## Errores comunes

### 1. No abre la interfaz
Verifica que `customtkinter` esté instalado.

### 2. No encuentra el CSV
El archivo debe estar exactamente en:

```text
data/flights_final.csv
```

### 3. No se abre el mapa
El proyecto genera archivos HTML en la carpeta `maps/` y luego intenta abrirlos en el navegador predeterminado.

### 4. Un código de aeropuerto no funciona
Debe existir en el dataset cargado y escribirse igual al código almacenado en el CSV.

## Comentario técnico

Los algoritmos del laboratorio fueron implementados sin usar librerías que resuelvan grafos automáticamente. La conectividad, la bipartición, el MST y los caminos mínimos se resuelven con lógica propia en `src/algorithms.py`.
