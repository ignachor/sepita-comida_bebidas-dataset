# sepita-comida_bebidas-dataset

CSV de **precios de comidas y bebidas** en Argentina, actualizado a diario a partir del volcado oficial de
[SEPA / Precios Claros](https://datos.produccion.gob.ar/dataset/sepa-precios)
(Secretaría de Comercio, CC BY 4.0).

## Descarga

Siempre la última versión: release [`datos`](../../releases/tag/datos)
→ `productos.csv`, `precios.csv`, `comidas_y_bebidas.csv` y `metadata.json` (fecha de la fuente y cantidad de filas).

Tutoriales (el código ejecutable está en `examples/`): [API REST](docs/API-TUTORIAL.md) · [archivos CSV estáticos](docs/TUTORIAL.md) · [hoja de ruta: actualización sin intervención](docs/ROADMAP.md).

## Archivos (release `datos`)

| archivo | uso |
|---|---|
| `productos.csv` | **punto de partida.** Una fila por EAN, con la columna `busqueda` para buscar |
| `precios.csv` | precios por EAN y cadena (se une por `ean`) |
| `comidas_y_bebidas.csv` | ambas tablas aplanadas (una fila por cadena + EAN) |
| `metadata.json` | fecha de la fuente y cantidad de filas |

### Búsqueda

`busqueda` es texto en minúsculas y sin tildes, con **todas las formas en que cualquier cadena escribe el nombre**
más la marca, cada palabra una sola vez. Cada palabra de la consulta debe aparecer:

```sql
-- Postgres / SQLite: deben aparecer todas las palabras
SELECT * FROM productos
WHERE busqueda LIKE '%fernet%' AND busqueda LIKE '%branca%' AND busqueda LIKE '%750%';
```

Normaliza la consulta del usuario de la misma manera (minúsculas, sin tildes, puntuación convertida en espacios).

## Columnas (`comidas_y_bebidas.csv`)

Una fila por **cadena + EAN**; los precios se agregan entre las sucursales de esa cadena.

| columna | significado |
|---|---|
| `categoria`, `subcategoria` | Comidas / Bebidas y una subcategoría (ver más abajo) |
| `cadena` | nombre de la cadena (`comercio_bandera_nombre` de SEPA) |
| `codigo_producto`, `es_ean` | EAN-13/8 válido (UPC-A convertido a EAN-13) |
| `descripcion`, `marca`, `cantidad_presentacion`, `unidad_presentacion` | datos del producto |
| `n_sucursales` | sucursales de esa cadena que lo venden |
| `precio_min`, `precio_promedio`, `precio_max` | precio de lista entre sucursales |
| `precio_referencia`, `unidad_referencia` | precio por unidad de referencia (kg, l…) |

Subcategorías — Bebidas: aguas, aperitivos y destilados, cervezas, gaseosas y jugos, infusiones,
vinos y espumantes. Comidas: carnes, pescados y fiambres; dulces, golosinas y snacks; frutas y verduras;
lácteos y huevos; panificados y galletitas; pastas, arroz y cereales.

## Limitaciones conocidas

- SEPA **no tiene un campo de categoría**: las categorías se infieren a partir de palabras clave en la
  descripción abreviada (`classifier.py`). Pueden aparecer clasificaciones erróneas.
- Se descartan las filas sin EAN válido (por ejemplo, carne o verdura por peso con un código interno de la cadena).
- Los precios vienen tal cual de las cadenas; no se filtran valores atípicos.

## Actualización

El proceso corre en una PC local con `update.sh`, programado como tarea de Windows (`SepitaDatasetUpdate`, todos los días a las 20:00):
descarga el volcado más reciente desde CKAN, ejecuta `build_dataset.py`, reemplaza los archivos de la release `datos`
y, si existe `DATABASE_URL`, recarga las tablas `productos` y `precios` en Postgres/Supabase (`load.sql`).
Al terminar elimina la carpeta local `dist/`.

No corre en GitHub Actions porque `datos.produccion.gob.ar` responde 403 a los servidores de GitHub
(el workflow `.github/workflows/update.yml` quedó solo para ejecución manual y hoy no es funcional).
El plan para automatizarlo sin depender de la PC está en [`docs/ROADMAP.md`](docs/ROADMAP.md).

Ejecución local (solo biblioteca estándar, Python 3.11+):

```
python test_dataset.py
python build_dataset.py                      # descarga el último volcado en dist/
python build_dataset.py --source <zip|dir>   # usa un volcado local
cp .env.example .env                         # opcional: define DATABASE_URL para cargar en la base
./update.sh                                  # todo el flujo: build, release y carga en la base
```
