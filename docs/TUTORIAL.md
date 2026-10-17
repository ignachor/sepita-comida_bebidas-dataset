# Tutorial: consuming the dataset from TypeScript

The repo has no API: it publishes two static files that are refreshed daily.
You download them with `fetch` and filter on the client.

| File | URL |
|---|---|
| CSV | `https://github.com/ignachor/sepita-comida_bebidas-dataset/releases/download/datos/comidas_y_bebidas.csv` |
| Metadata | `https://github.com/ignachor/sepita-comida_bebidas-dataset/releases/download/datos/metadata.json` |

Requirements: Node 22.18+ (runs `.ts` natively) or any runtime with `fetch`. No dependencies.

## 1. Check how fresh the data is

```ts
const meta = await fetchMetadata();
// { fuente: "Jueves", fuente_actualizada: "2026-10-15T16:19:08", filas: 51391, ... }
```

## 2. Load and parse the CSV

Descriptions can contain commas and quotes, so `split(",")` is **not** enough.
`examples/sepita.ts` includes a small RFC 4180 parser (`parseCsv`) and strips the UTF-8 BOM
that the file starts with. `loadProducts()` returns typed `Product[]`.

```ts
const products = await loadProducts();
```

## 3. Query it

```ts
search(products, "yerba");   // text match on the description
byEan(products, "7792710000175"); // same product, every chain
cheapest(list);              // lowest precioPromedio in a list
```

Filter anything else with plain array methods, e.g.
`products.filter(p => p.subcategoria === "Cervezas" && p.cadena === "Vea")`.

## 4. Run the full example

```
node examples/demo.ts
```

Expected output (values change every day with the data; the shape stays the same):

```
Source: Jueves (2026-10-15T16:19:08.834801), 51391 rows

1036 products match "yerba". Cheapest:
  YERBA MATE TARAGUI C/PALO 500gr. @ California Supermercados: $415

AMANDA YERBA MATE CON PALO 1KG (EAN 7792710000175) across chains:
  LA AGRICOLA REGIONAL COOPERATIVA LIMITADA $3400  (4 branches)
  Sup. Unicoop             $3657  (3 branches)
  Cooperativa Obrera Limitada de Consumo y Vivienda $4148.68  (155 branches)
  Supermercados DIA        $4873.53  (948 branches)
  COTO CICSA               $4993.28  (119 branches)
  Toledo                   $4999  (23 branches)
  Maxi                     $5029.31  (644 branches)
  La Anonima               $5066.35  (182 branches)
  SuperChangomas           $5110.72  (93 branches)
  Vea                      $5736.67  (18 branches)
```

## Things to know

- Prices are **list prices per chain**: `precioMin/Promedio/Max` are computed across that chain's branches.
- Prices are not cleaned: outliers exist (above, a 500 g yerba at $415 is almost certainly a data error in the source).
- Categories are inferred from keywords, so a few products are misclassified (see the README).
- The CSV is ~8 MB; cache it on your side instead of downloading it on every request.
