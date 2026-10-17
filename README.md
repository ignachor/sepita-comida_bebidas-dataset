# sepita-comida_bebidas-dataset

Daily-updated CSV of **food and drink prices** in Argentina, built from the official
[SEPA / Precios Claros](https://datos.produccion.gob.ar/dataset/sepa-precios) dump
(Secretaría de Comercio, CC BY 4.0).

## Download

Always the latest version: release [`datos`](../../releases/tag/datos)
→ `comidas_y_bebidas.csv` (+ `metadata.json` with source date and row counts).

TypeScript tutorial: [`docs/TUTORIAL.md`](docs/TUTORIAL.md) (runnable code in `examples/`).

## Files (release `datos`)

| file | use |
|---|---|
| `productos.csv` | **start here.** One row per EAN, with a `busqueda` column for searching |
| `precios.csv` | prices per EAN and chain (join on `ean`) |
| `comidas_y_bebidas.csv` | both tables flattened (one row per chain + EAN) |
| `metadata.json` | source date and row counts |

### Searching

`busqueda` is lowercase, accent-free text with **every spelling of the name used by any chain**
plus the brand, each word once. Match every word of the query as a prefix:

```sql
-- Postgres / SQLite: all words must appear
SELECT * FROM productos
WHERE busqueda LIKE '%fernet%' AND busqueda LIKE '%branca%' AND busqueda LIKE '%750%';
```

Normalise the user's query the same way (lowercase, no accents, punctuation to spaces).

## Columns (`comidas_y_bebidas.csv`)

One row per **chain + EAN**; prices are aggregated across that chain's branches.

| column | meaning |
|---|---|
| `categoria`, `subcategoria` | Comidas / Bebidas and a subcategory (see below) |
| `cadena` | chain name (SEPA `comercio_bandera_nombre`) |
| `codigo_producto`, `es_ean` | valid EAN-13/8 (UPC-A converted to EAN-13) |
| `descripcion`, `marca`, `cantidad_presentacion`, `unidad_presentacion` | product info |
| `n_sucursales` | branches of that chain selling it |
| `precio_min`, `precio_promedio`, `precio_max` | list price across branches |
| `precio_referencia`, `unidad_referencia` | price per reference unit (kg, l…) |

Subcategories — Bebidas: aguas, aperitivos y destilados, cervezas, gaseosas y jugos, infusiones,
vinos y espumantes. Comidas: carnes/pescados/fiambres, dulces/golosinas/snacks, frutas y verduras,
lácteos y huevos, panificados y galletitas, pastas/arroz/cereales.

## Known limitations

- SEPA has **no category field**: categories are inferred from keywords in the (abbreviated)
  description (`classifier.py`). Expect occasional misclassification.
- Rows without a valid EAN (e.g. weighed meat or produce with an internal chain code) are dropped.
- Prices come straight from the chains; outliers are not filtered.

## Update

`.github/workflows/update.yml` runs daily at 20:00 ART (and on demand from the Actions tab):
it fetches the newest weekday zip from CKAN, runs `build_dataset.py` and replaces the release assets.

Local run (stdlib only, Python 3.11+):

```
python test_dataset.py
python build_dataset.py                      # downloads latest dump into dist/
python build_dataset.py --source <zip|dir>   # use a local dump
```
