import pandas as pd
import numpy as np

# Lista ordenada de los 32 estados de México (ISO 3166-2:MX)
ESTADOS_MEXICO = [
    "AGU", "BCN", "BCS", "CAM", "CHH", "CHP", "CMX", "COA",
    "COL", "DUR", "GRO", "GUA", "HID", "JAL", "MEX", "MIC",
    "MOR", "NAY", "NLE", "OAX", "PUE", "QUE", "ROO", "SLP",
    "SIN", "SON", "TAB", "TAM", "TLA", "VER", "YUC", "ZAC"
]

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
df = pd.read_excel("basePrueba.xlsx")

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


# ── PASO 1: Matriz de presencia/ausencia (taxon_name × id_geo) ──────────────

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

# Asegurar que estén todas las columnas canónicas (rellenar con 0 si falta)
for u in unidades:
    if u not in presencia_ausencia.columns:
        presencia_ausencia[u] = 0
presencia_ausencia = presencia_ausencia[unidades]

# Para estados: renombrar columnas a índices numéricos 1-32
if tipo == "estados":
    presencia_ausencia.columns = list(range(1, n_unidades + 1))

print("\nMatriz de presencia-ausencia (taxon_name × id_geo):")
print(presencia_ausencia)

# Guardar en Excel
try:
    presencia_ausencia.to_excel("matriz_presencia_ausencia.xlsx")
    print("\nMatriz guardada en 'matriz_presencia_ausencia.xlsx'")
except PermissionError:
    print("\n[Aviso] Cierra 'matriz_presencia_ausencia.xlsx' en Excel e intenta de nuevo.")


# ── PASO 2: Agrupar para identificar los Patrones-G ─────────────────────────
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

print(f"\nPatrones-G identificados: {len(patrones)}")
print(patrones[["taxa_count", "Gi"]].to_string(index=False))


# ── PASO 3: Numerar secuencialmente los patrones ─────────────────────────────
# G1, G2, … → patrones compartidos (taxa_count >= 2), ya ordenados
# G0         → patrones únicos (taxa_count == 1), no forman un patrón compartido

gn = patrones[patrones["taxa_count"] >= 2].copy().reset_index(drop=True)
g0 = patrones[patrones["taxa_count"] == 1].copy().reset_index(drop=True)

gn["g_pattern_id"] = ["G" + str(i + 1) for i in range(len(gn))]
g0["g_pattern_id"] = "G0"

tabla_patrones = pd.concat([gn, g0]).reset_index(drop=True)
tabla_patrones = tabla_patrones[["g_pattern_id", "taxa_count", "Gi"] + indices]

print(f"\nPatrones numerados: G1–G{len(gn)}  |  G0: {len(g0)} patrones únicos")
print(tabla_patrones[["g_pattern_id", "taxa_count", "Gi"]].to_string(index=False))


# ── PASO 4: rel_gpattern_idgeo ───────────────────────────────────────────────
# Tabla normalizada: una fila por cada (g_pattern_id, id_geo) con presencia.
# Solo patrones G1, G2, … (G0 no tiene un patrón geográfico único definido).

registros = []
for _, fila in gn.iterrows():
    for idx, id_geo in zip(indices, unidades):
        if fila[idx] == 1:
            registros.append({"g_pattern_id": fila["g_pattern_id"], "id_geo": id_geo})

rel_gpattern_idgeo = pd.DataFrame(registros)

print("\nTabla rel_gpattern_idgeo:")
print(rel_gpattern_idgeo.to_string(index=False))

try:
    rel_gpattern_idgeo.to_excel("rel_gpattern_idgeo.xlsx", index=False)
    print("\nTabla guardada en 'rel_gpattern_idgeo.xlsx'")
except PermissionError:
    print("\n[Aviso] Cierra 'rel_gpattern_idgeo.xlsx' en Excel e intenta de nuevo.")