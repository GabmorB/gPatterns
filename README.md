# gPatterns

Herramienta para leer y clasificar datos geográficos de México a partir de una base de datos con el método de G-pattern, como paso previo a su visualización en el sitio Sipmx.

---

## Requisitos

- Python 3.x
- pandas
- numpy
- openpyxl (necesario para leer archivos `.xlsx`)

Instalación de dependencias:

```bash
pip install pandas numpy openpyxl
```

---

## Archivo de entrada

El programa lee un archivo Excel (`.xlsx`) que debe contener al menos la columna **`id_geo`**.

El programa detecta automáticamente cuál de los tres tipos de unidad geográfica contiene esa columna:

| Tipo | Descripción | Ejemplo de `id_geo` |
|------|-------------|----------------------|
| `estados` | Códigos de 3 letras de estados mexicanos (ISO 3166-2:MX) | `PUE`, `MEX`, `BCS` |
| `cuadros_numericos` | IDs numéricos de cuadros de la interfaz SIMPMX | `6`, `11`, `23` |
| `eleccion_usuario` | Unidades arbitrarias definidas por el usuario | cualquier otro valor |

---

## Uso

1. Coloca tu archivo Excel en la misma carpeta que `prueba1.py`.
2. Cambia el nombre del archivo en la línea correspondiente si es necesario:

```python
df = pd.read_excel("basePrueba.xlsx")
```

3. Ejecuta el programa:

```bash
python prueba1.py
```

---

## Proceso implementado

### Paso 1 — Matriz de presencia/ausencia ✅

El programa construye una matriz `taxon_name × id_geo` con valores 0/1 (ausencia/presencia).

- Los valores de `id_geo` se normalizan a string para garantizar consistencia de tipos.
- Se aseguran todas las unidades canónicas en las columnas (las unidades sin registros se rellenan con 0).
- Para `estados`: las columnas se renombran a índices numéricos 1–32 según el orden canónico de `ESTADOS_MEXICO`.
- La matriz se exporta a `matriz_presencia_ausencia.xlsx`.

### Pasos 2–6 — En desarrollo

| Paso | Descripción |
|------|-------------|
| 2 | Agrupar para identificar los Patrones-G |
| 3 | Numerar secuencialmente los patrones |
| 4 | Crear tabla normalizada `rel_gpattern_idgeo` |
| 5 | Crear relación `rel_gpattern_taxon` + patrón G0 |
| 6 | Crear catálogo `cat_gpatterns` con atributo `disjoint` |

---

## Salida esperada

**Ejemplo con cuadros SIMPMX:**
```
Filas: 2999  |  Columnas: ['id_geo', 'taxon_name']
Tipo de unidad geográfica detectada: 'cuadros_numericos'
-> Unidades: cuadros (ID numérico).

Matriz de presencia-ausencia (taxon_name × id_geo):
id_geo           1  2  3  ...
taxon_name
Abies religiosa  0  0  1  ...
...
Matriz guardada en 'matriz_presencia_ausencia.xlsx'
```

---

## Notas

- Las unidades de tipo `eleccion_usuario` son determinadas por el usuario.
- El programa ignora valores vacíos (`NaN`) al analizar `id_geo`.
- Si los valores de `id_geo` son mixtos (algunos numéricos, otros texto), el programa los clasificará como `eleccion_usuario`.
