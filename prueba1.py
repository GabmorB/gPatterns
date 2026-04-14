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