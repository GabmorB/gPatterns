# gPatterns — Clasificador de Unidades Geográficas

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
2. Cambia el nombre del archivo en la línea 35 si es necesario:

```python
df = pd.read_excel("basePrueba.xlsx")
```

3. Ejecuta el programa:

```bash
python prueba1.py
```

---

## Salida esperada

El programa imprime:

- Número de filas y columnas del archivo
- Las primeras 10 filas del contenido
- El tipo de unidad geográfica detectada

**Ejemplo con cuadros SIMPMX:**
```
Filas: 150  |  Columnas: ['id_geo', 'valor', ...]
...
Tipo de unidad geográfica detectada: 'cuadros_numericos'
-> Unidades: cuadros (ID numérico).
```

---

## Notas

- Las unidades de tipo `eleccion_usuario` son determinadas por el usuario.
- El programa ignora valores vacíos (`NaN`) al analizar `id_geo`.
- Si los valores de `id_geo` son mixtos (algunos numéricos, otros texto), el programa los clasificará como `eleccion_usuario`.
