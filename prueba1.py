import pandas as pd
import numpy as np

# Códigos válidos de estados de México (3 letras)
ESTADOS_MEXICO = {
    "AGU", "BCN", "BCS", "CAM", "CHP", "CHH", "COA", "COL",
    "DUR", "GUA", "GRO", "HID", "JAL", "MEX", "MIC", "MOR",
    "NAY", "NLE", "OAX", "PUE", "QUE", "ROO", "SLP", "SIN",
    "SON", "TAB", "TAM", "TLA", "VER", "YUC", "ZAC", "CMX"
}

def detectar_tipo_geo(serie):
    """
    Detecta el tipo de unidad geográfica en id_geo:
      'estado'   -> códigos de 3 letras de estados mexicanos
      'simpmx'   -> cuadros numéricos de SIMPMX
      'arbitrario' -> unidades definidas por el usuario
    """
    muestra = serie.dropna().astype(str).unique()

    # ¿Son todos numéricos?
    son_numericos = np.all([v.strip().lstrip("-").isdigit() for v in muestra])
    if son_numericos:
        return "simpmx"

    # ¿Son códigos de estado (3 letras mayúsculas)?
    son_estados = np.all([v.strip().upper() in ESTADOS_MEXICO for v in muestra])
    if son_estados:
        return "estado"

    return "arbitrario"


# ── Leer archivo ────────────────────────────────────────────────
df = pd.read_excel("basePrueba.xlsx")

print(f"Filas: {len(df)}  |  Columnas: {list(df.columns)}")
print(df.head(10))

# ── Detectar tipo de id_geo ─────────────────────────────────────
tipo = detectar_tipo_geo(df["id_geo"])
print(f"\nTipo de unidad geográfica detectada: '{tipo}'")

if tipo == "estado":
    print("-> Unidades: estados de México (código 3 letras).")
    print("   Se puede mapear directamente sobre el mapa estatal.")

elif tipo == "simpmx":
    print("-> Unidades: cuadros SIMPMX (ID numérico).")
    print("   Se puede mapear usando la cuadrícula de SIMPMX.")

elif tipo == "arbitrario":
    print("-> Unidades geográficas arbitrarias (definidas por el usuario).")
    print("   No tienen representación en el mapa de SIMPMX.")
