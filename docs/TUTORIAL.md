# Tutorial: consumir el dataset desde TypeScript

Este tutorial usa los archivos estáticos de la release, sin API: se descargan con `fetch` y se filtran en el cliente.
Los archivos se actualizan a diario.

| Archivo | URL |
|---|---|
| CSV | `https://github.com/ignachor/sepita-comida_bebidas-dataset/releases/download/datos/comidas_y_bebidas.csv` |
| Metadata | `https://github.com/ignachor/sepita-comida_bebidas-dataset/releases/download/datos/metadata.json` |

Si prefieres una API para consultar, consulta el [tutorial de la API REST](API-TUTORIAL.md).

Requisitos: Node 22.18+ (ejecuta `.ts` de forma nativa) o cualquier entorno con `fetch`. Sin dependencias.

## 1. Comprobar qué tan reciente es el dato

```ts
const meta = await fetchMetadata();
// { fuente: "Jueves", fuente_actualizada: "2026-10-15T16:19:08", filas: 51391, ... }
```

## 2. Cargar y parsear el CSV

Las descripciones pueden contener comas y comillas, por lo que `split(",")` **no** alcanza.
`examples/sepita.ts` incluye un parser RFC 4180 mínimo (`parseCsv`) y elimina el BOM UTF-8 con el que empieza el archivo.
`loadProducts()` devuelve un `Product[]` tipado.

```ts
const products = await loadProducts();
```

## 3. Consultar

```ts
search(products, "yerba");        // coincidencia de texto en la descripción
byEan(products, "7792710000175"); // el mismo producto en todas las cadenas
cheapest(list);                   // menor precioPromedio de una lista
```

Cualquier otro filtro se hace con métodos de arreglos, por ejemplo:
`products.filter(p => p.subcategoria === "Cervezas" && p.cadena === "Vea")`.

## 4. Ejecutar el ejemplo completo

```
node examples/demo.ts
```

Salida esperada (los valores cambian cada día con los datos; el formato se mantiene):

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

## Cosas a tener en cuenta

- Los precios son **precios de lista por cadena**: `precioMin/Promedio/Max` se calculan entre las sucursales de esa cadena.
- Los precios no están depurados: existen valores atípicos (arriba, una yerba de 500 g a $415 es casi seguro un error del dato de origen).
- Las categorías se infieren por palabras clave, por lo que algunos productos están mal clasificados (ver el README).
- El CSV pesa ~8 MB; consérvalo en caché en lugar de descargarlo en cada consulta.
