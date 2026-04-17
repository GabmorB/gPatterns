import pandas as pd
import numpy as np

# Lista ordenada de los 32 estados de México
ESTADOS_MEXICO = [
    "AGU", "BCN", "BCS", "CAM", "CHH", "CHP", "CMX", "COA",
    "COL", "DUR", "GRO", "GUA", "HID", "JAL", "MEX", "MIC",
    "MOR", "NAY", "NLE", "OAX", "PUE", "QUE", "ROO", "SLP",
    "SIN", "SON", "TAB", "TAM", "TLA", "VER", "YUC", "ZAC"
]

# Matriz de adyacencia de estados de México
ADYACENCIA_ESTADOS = {
    "AGU": ["GUA", "JAL", "ZAC"],
    "BCN": ["BCS"],
    "BCS": ["BCN"],
    "CAM": ["ROO", "TAB", "YUC"],
    "CHH": ["COA", "DUR", "SIN", "SON"],
    "CHP": ["OAX", "TAB", "VER"],
    "CMX": ["MEX", "MOR"],
    "COA": ["CHH", "DUR", "NLE", "TAM", "ZAC"],
    "COL": ["JAL", "MIC"],
    "DUR": ["CHH", "COA", "NAY", "SIN", "ZAC"],
    "GRO": ["MEX", "MIC", "MOR", "OAX", "PUE"],
    "GUA": ["AGU", "HID", "JAL", "MIC", "QUE", "SLP", "ZAC"],
    "HID": ["GUA", "MEX", "PUE", "QUE", "SLP", "TLA", "VER"],
    "JAL": ["AGU", "COL", "DUR", "GUA", "MIC", "NAY", "ZAC"],
    "MEX": ["CMX", "GRO", "HID", "MIC", "MOR", "PUE", "QUE", "TLA"],
    "MIC": ["COL", "GRO", "GUA", "JAL", "MEX", "QUE"],
    "MOR": ["CMX", "GRO", "MEX", "PUE"],
    "NAY": ["DUR", "JAL", "SIN", "ZAC"],
    "NLE": ["COA", "SLP", "TAM", "ZAC"],
    "OAX": ["CHP", "GRO", "PUE", "VER"],
    "PUE": ["GRO", "HID", "MEX", "MOR", "OAX", "TLA", "VER"],
    "QUE": ["GUA", "HID", "MEX", "MIC", "SLP"],
    "ROO": ["CAM", "YUC"],
    "SLP": ["COA", "GUA", "HID", "NLE", "QUE", "TAM", "VER", "ZAC"],
    "SIN": ["CHH", "DUR", "NAY", "SON"],
    "SON": ["CHH", "SIN"],
    "TAB": ["CAM", "CHP", "VER"],
    "TAM": ["COA", "NLE", "SLP", "VER"],
    "TLA": ["HID", "MEX", "PUE"],
    "VER": ["CHP", "HID", "OAX", "PUE", "SLP", "TAB", "TAM"],
    "YUC": ["CAM", "ROO"],
    "ZAC": ["AGU", "COA", "DUR", "GUA", "JAL", "NAY", "NLE", "SLP"],
}


def es_conexo(estados_presentes, adyacencia):
    """
    Verifica si un conjunto de estados forma territorio contiguo.
    Retorna True si es conexo, False si tiene componentes separados (disjoint).
    """
    from collections import deque
    estados = set(estados_presentes)
    if len(estados) <= 1:
        return True
    visitados = {next(iter(estados))}
    cola = deque(visitados)
    while cola:
        actual = cola.popleft()
        for vecino in adyacencia.get(actual, []):
            if vecino in estados and vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)
    return visitados == estados


def detectar_tipo_geo(serie):
    """
    Función que detecta el tipo de unidad geográfica en id_geo:
    tanto si es 'clave_estado' = códigos de 3 letras de estados mexicanos
      'cuadros' = cuadros numéricos
      'eleccion_usuario' = unidades definidas por el usuario
    """
    muestra = serie.dropna().astype(str).unique()

    # Si se reciben datos por cuadros
    cuadros = np.all([v.strip().lstrip("-").isdigit() for v in muestra])
    if cuadros:
        return "cuadros_numericos"

    # Se reciben claves de estados
    estados = np.all([v.strip().upper() in ESTADOS_MEXICO for v in muestra])
    if estados:
        return "estados"

    return "eleccion_usuario"


# Comienza el programa, se lee el archivo
df = pd.read_excel("Nayarit.xlsx")

# Se imprimen 10 resultados ordenados en filas y columnas
print(f"Filas: {len(df)}  |  Columnas: {list(df.columns)}")
print(df.head(10))

# Se detecta el tipo de información que contiene la columna ''id_geo''
tipo = detectar_tipo_geo(df["id_geo"])
print(f"\nTipo de unidad geográfica detectada: '{tipo}'")

if tipo == "estados":
    print("-> Unidades: estados de México (código 3 letras).")

elif tipo == "cuadros_numericos":
    print("-> Unidades: cuadros (ID numérico).")

elif tipo == "eleccion_usuario":
    print("-> Unidades geográficas definidas por el usuario.")


# Matriz de presencia/ausencia (taxon_name × id_geo)

# Normalizar id_geo a string para que el tipo sea consistente en todo el programa
df["id_geo"] = df["id_geo"].astype(str).str.strip()

# Determinar las unidades geográficas canónicas y su orden
if tipo == "estados":
    unidades = ESTADOS_MEXICO          # orden fijo: AGU=1 … ZAC=32
elif tipo == "cuadros_numericos":
    unidades = sorted(df["id_geo"].dropna().astype(str).unique(),
                      key=lambda x: int(x))
else:
    unidades = sorted(df["id_geo"].dropna().astype(str).unique())

n_unidades = len(unidades)

# Construir matriz: una fila por taxón, una columna por unidad geográfica
presencia_ausencia = (
    df.groupby(["taxon_name", "id_geo"])
    .size()
    .unstack(fill_value=0)
    .clip(upper=1)
)

# Asegurar que estén todas las columnas canónicas (Se rellena con 0 si falta)
for u in unidades:
    if u not in presencia_ausencia.columns:
        presencia_ausencia[u] = 0
presencia_ausencia = presencia_ausencia[unidades]

# Para estados: renombrar columnas a índices numéricos 1-32
if tipo == "estados":
    presencia_ausencia.columns = list(range(1, n_unidades + 1))


# Guardar en Excel
try:
    presencia_ausencia.to_excel("matriz_presencia_ausencia.xlsx")
    print("\nMatriz guardada en 'matriz_presencia_ausencia.xlsx'")
except PermissionError:
    print("\n[Aviso] Cierra 'matriz_presencia_ausencia.xlsx' en Excel e intenta de nuevo.")


# Agrupar para identificar los Patrones-G
# Agrupa los taxones que tienen exactamente el mismo vector de presencia/ausencia.
# Cada grupo único es un Patrón-G.

indices = list(presencia_ausencia.columns)

patrones = (
    presencia_ausencia
    .groupby(indices, sort=False)
    .size()
    .reset_index(name="taxa_count")
)

patrones["Gi"] = patrones[indices].sum(axis=1)

# Ordenar: mayor taxa_count primero, luego mayor Gi
patrones = patrones.sort_values(
    ["taxa_count", "Gi"], ascending=[False, False]
).reset_index(drop=True)


# Numerar secuencialmente los patrones
# G1, G2, …  patrones compartidos (taxa_count >= 2), ya ordenados
# G0         patrones únicos (taxa_count == 1), no forman un patrón compartido

gn = patrones[patrones["taxa_count"] >= 2].copy().reset_index(drop=True)
g0 = patrones[patrones["taxa_count"] == 1].copy().reset_index(drop=True)

gn["g_pattern_id"] = ["G" + str(i + 1) for i in range(len(gn))]
g0["g_pattern_id"] = "G0"

tabla_patrones = pd.concat([gn, g0]).reset_index(drop=True)
tabla_patrones = tabla_patrones[["g_pattern_id", "taxa_count", "Gi"] + indices]



# Generación del rel_gpattern_idgeo 
# Tabla normalizada: una fila por cada (g_pattern_id, id_geo) con presencia.
# Solo patrones G1, G2, … (G0 no tiene un patrón geográfico único definido).

registros = []
for _, fila in gn.iterrows():
    for idx, id_geo in zip(indices, unidades):
        if fila[idx] == 1:
            registros.append({"g_pattern_id": fila["g_pattern_id"], "id_geo": id_geo})

rel_gpattern_idgeo = pd.DataFrame(registros)



# Generación del rel_gpattern_taxon

lookup = {tuple(fila[indices]): fila["g_pattern_id"]
          for _, fila in tabla_patrones.iterrows()}

registros = []
for taxon, fila in presencia_ausencia.iterrows():
    gid = lookup.get(tuple(fila[indices]), "G0")
    registros.append({"taxon_name": taxon, "g_pattern_id": gid})

rel_gpattern_taxon = (pd.DataFrame(registros)
                      .sort_values(["g_pattern_id", "taxon_name"])
                      .reset_index(drop=True))



# Catálogo de patrones con atributos: id_pattern, pattern, disjoint, total_geo, total_sp
#   disjoint = "Disjoint"     territorio NO contiguo (componentes separados)
#   disjoint = "Non-disjoint" territorio contiguo
#   disjoint = None           no aplica (cuadros: lo calcula SIPMX; eleccion_usuario: sin mapa)

filas = []
for _, fila in gn.iterrows():
    estados_presentes = [unidades[i] for i, idx in enumerate(indices) if fila[idx] == 1]

    if tipo == "estados":
        es_disjoint = not es_conexo(estados_presentes, ADYACENCIA_ESTADOS)
        disjoint_str = "Disjoint" if es_disjoint else "Non-disjoint"
    else:
        disjoint_str = None

    id_num = int(fila["g_pattern_id"][1:])  # extrae el número de "G1", "G2", …

    filas.append({
        "id_pattern": id_num,
        "pattern":    " ".join(estados_presentes),
        "disjoint":   disjoint_str,
        "total_geo":  int(fila["Gi"]),
        "total_sp":   int(fila["taxa_count"]),
    })

cat_gpatterns = (pd.DataFrame(filas)
                 .sort_values("pattern")
                 .reset_index(drop=True))

try:
    cat_gpatterns.to_excel("nayarit_gpattern.xlsx", index=False)
    print("\nCatálogo guardado en 'nayarit_gpattern.xlsx'")
except PermissionError:
    print("\n[Aviso] Cierra 'nayarit_gpattern.xlsx' en Excel e intenta de nuevo.")