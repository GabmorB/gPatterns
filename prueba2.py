import pandas as pd
import numpy as np




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


    return "eleccion_usuario"


# Comienza el programa, se lee el archivo
df = pd.read_excel("Asteraceae_mex.xlsx")

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
if tipo == "cuadros_numericos":
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

# Asegurar que estén todas las columnas (Se rellena con 0 si falta)
for u in unidades:
    if u not in presencia_ausencia.columns:
        presencia_ausencia[u] = 0
presencia_ausencia = presencia_ausencia[unidades]


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
# Tabla normalizada: una fila por cada (id_pattern, id_geo) con presencia.
# Solo patrones G1, G2, … (G0 no tiene un patrón geográfico único definido).

registros = []
for _, fila in gn.iterrows():
    id_num = int(fila["g_pattern_id"][1:])
    for idx, id_geo in zip(indices, unidades):
        if fila[idx] == 1:
            registros.append({"id_pattern": id_num, "id_geo": int(id_geo)})

rel_gpattern_idgeo = pd.DataFrame(registros)

try:
    rel_gpattern_idgeo.to_excel("rel_gpattern_idgeo.xlsx", index=False)
    print("\nTabla guardada en 'rel_gpattern_idgeo.xlsx'")
except PermissionError:
    print("\n[Aviso] Cierra 'rel_gpattern_idgeo.xlsx' en Excel e intenta de nuevo.")



# Generación del rel_gpattern_taxon

lookup = {tuple(fila[indices]): int(fila["g_pattern_id"][1:])
          for _, fila in gn.iterrows()}

registros = []
for taxon, fila in presencia_ausencia.iterrows():
    id_num = lookup.get(tuple(fila[indices]), 0)
    registros.append({"taxon_name": taxon, "id_pattern": id_num})

rel_gpattern_taxon = pd.DataFrame(registros).reset_index(drop=True)
rel_gpattern_taxon.insert(0, "id_sp", range(1, len(rel_gpattern_taxon) + 1))
rel_gpattern_taxon = rel_gpattern_taxon[["id_sp", "id_pattern"]]

try:
    rel_gpattern_taxon.to_excel("rel_gpattern_taxon.xlsx", index=False)
    print("\nTabla guardada en 'rel_gpattern_taxon.xlsx'")
except PermissionError:
    print("\n[Aviso] Cierra 'rel_gpattern_taxon.xlsx' en Excel e intenta de nuevo.")



# Resumen de patrones con atributos: id_pattern, pattern, total_geo, total_sp

filas = []
for _, fila in gn.iterrows():
    estados_presentes = [unidades[i] for i, idx in enumerate(indices) if fila[idx] == 1]

    #if tipo == "estados":
        #es_disjoint = not es_conexo(estados_presentes, ADYACENCIA_ESTADOS)
     #   disjoint_str = "Disjoint" if es_disjoint else "Non-disjoint"
    ##   disjoint_str = None

    id_num = int(fila["g_pattern_id"][1:])  # extrae el número de "G1", "G2", …

    filas.append({
        "id_pattern": id_num,
        "pattern":    " ".join(estados_presentes),
        "total_geo":  int(fila["Gi"]),
        "total_sp":   int(fila["taxa_count"]),
    })

resumen_gpatterns = (pd.DataFrame(filas)
                 .sort_values("pattern")
                 .reset_index(drop=True))

try:
    resumen_gpatterns.to_excel("resumen_asteraceae_mex.xlsx", index=False)
    print("\nCatálogo guardado en 'resumen_asteraceae_mex.xlsx'")
except PermissionError:
    print("\n[Aviso] Cierra 'Asteraceae_mex.xlsx' en Excel e intenta de nuevo.")