import pandas as pd
import numpy as np

# Conjunto con códigos prueba de estados de México
ESTADOS_MEXICO = {
    "AGU", "BCN", "BCS", "CAM", "CHP", "CHH", "COA", "COL",
    "DUR", "GUA", "GRO", "HID", "JAL", "MEX", "MIC", "MOR",
    "NAY", "NLE", "OAX", "PUE", "QUE", "ROO", "SLP", "SIN",
    "SON", "TAB", "TAM", "TLA", "VER", "YUC", "ZAC", "CMX"
}

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
