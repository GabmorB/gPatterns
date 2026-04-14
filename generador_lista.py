import pandas as pd
import random

# Semilla para reproducibilidad
random.seed(42)

# Lista ordenada de los 32 estados de México
ESTADOS_MEXICO = [
    "AGU", "BCN", "BCS", "CAM", "CHH", "CHP", "CMX", "COA",
    "COL", "DUR", "GRO", "GUA", "HID", "JAL", "MEX", "MIC",
    "MOR", "NAY", "NLE", "OAX", "PUE", "QUE", "ROO", "SLP",
    "SIN", "SON", "TAB", "TAM", "TLA", "VER", "YUC", "ZAC"
]

# Géneros y epítetos inventados para construir nombres de especies
GENEROS = [
    "Fictusia", "Inventara", "Pruebalis", "Testia", "Falsocactus",
    "Novoplanta", "Exemplaria", "Simulex", "Dataria", "Codexia",
    "Arbustela", "Floribunda", "Radicalis", "Foliacea", "Spinulosa"
]

EPITETOS = [
    "mexicana", "nortealis", "sureanis", "montanum", "deserticola",
    "tropicalis", "costensis", "altiplana", "rupestris", "sylvatica",
    "lacustris", "aridorum", "humilis", "grandifolia", "parvifolia",
    "longipes", "brevicaulis", "crassipes", "tenuis", "robusta",
    "gracilis", "latifolium", "angustifolia", "viridis", "pallida"
]

# Genera nombres de especies únicos (Género + epíteto)
nombres_especies = sorted({
    f"{g} {e}" for g in GENEROS for e in EPITETOS
})

# Selecciona 80 especies al azar
especies = random.sample(nombres_especies, 80)

# -----------------------------------------------------------------------
# Patrones de distribución predefinidos para que la tabla sea interesante
# -----------------------------------------------------------------------
# Cada patrón es un subconjunto de estados; varias especies lo comparten.
patrones = {
    "amplia":        ESTADOS_MEXICO,                          # todos los estados
    "norte":         ESTADOS_MEXICO[:10],                     # 10 estados del norte
    "sur":           ESTADOS_MEXICO[22:],                     # 10 estados del sur
    "centro":        ESTADOS_MEXICO[10:22],                   # 12 estados del centro
    "pacifico":      ["BCN", "BCS", "SIN", "NAY", "JAL", "COL", "GRO", "OAX", "CHP"],
    "golfo":         ["TAM", "VER", "TAB", "CAM", "YUC", "ROO"],
    "altiplano":     ["CMX", "MEX", "HID", "TLA", "PUE", "QUE", "AGU"],
    "noreste":       ["COA", "NLE", "TAM", "CHH"],
    "noroeste":      ["SON", "SIN", "CHH", "DUR"],
    "endemico_cmx":  ["CMX"],
    "endemico_yuc":  ["YUC"],
    "endemico_bcs":  ["BCS"],
    "dos_estados_1": ["JAL", "MEX"],
    "dos_estados_2": ["OAX", "VER"],
    "tres_estados":  ["CMX", "MEX", "MOR"],
}

# Asignar patrones a las 80 especies con diferente frecuencia
# (más especies con patrones frecuentes → taxa_count alto en la tabla)
frecuencias = {
    "amplia":        8,
    "norte":         7,
    "sur":           7,
    "centro":        7,
    "pacifico":      6,
    "golfo":         6,
    "altiplano":     6,
    "noreste":       5,
    "noroeste":      5,
    "endemico_cmx":  6,
    "endemico_yuc":  5,
    "endemico_bcs":  5,
    "dos_estados_1": 4,
    "dos_estados_2": 4,
    "tres_estados":  4,
}

asignacion = []
idx = 0
for patron, n in frecuencias.items():
    estados_patron = patrones[patron]
    for _ in range(n):
        if idx >= len(especies):
            break
        asignacion.append((especies[idx], estados_patron))
        idx += 1

# -----------------------------------------------------------------------
# Construir el DataFrame de registros (una fila por ocurrencia)
# -----------------------------------------------------------------------
registros = []
for taxon, estados in asignacion:
    for estado in estados:
        # Agrega entre 1 y 3 registros por combinación taxon+estado
        n_obs = random.randint(1, 3)
        for _ in range(n_obs):
            registros.append({"id_geo": estado, "taxon_name": taxon})

df = pd.DataFrame(registros).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Registros generados: {len(df)}")
print(f"Especies únicas    : {df['taxon_name'].nunique()}")
print(f"Estados únicos     : {df['id_geo'].nunique()}")
print(f"\nMuestra de 10 registros:")
print(df.head(10).to_string(index=False))

# Guardar como basePrueba_estados.xlsx para no sobreescribir la base original
df.to_excel("basePrueba_estados.xlsx", index=False)
print("\nArchivo guardado en 'basePrueba_estados.xlsx'")
print("-> Para probarlo en prueba1.py cambia la línea:")
print("   pd.read_excel('basePrueba.xlsx')  =>  pd.read_excel('basePrueba_estados.xlsx')")
