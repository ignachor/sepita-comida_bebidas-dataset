# Tutorial: usar la API REST desde otra aplicación

Supabase expone las dos tablas (`productos`, `precios`) como una API REST (PostgREST). Tu aplicación solo necesita
una URL y una clave pública. No requiere backend ni dependencias.

| | |
|---|---|
| URL base | `https://fbhzibcingdanzlrslrq.supabase.co/rest/v1` |
| Header | `apikey: sb_publishable_MS2cjrHBl0_Jq1sqTSfckA_lzb7SWXT` |

La clave publicable **está pensada para ser pública** (navegador, app móvil). La seguridad a nivel de fila (RLS) solo permite
`SELECT`; cualquier escritura devuelve 401. Nunca incluyas en una app la clave `service_role` ni la contraseña de la base.

## 1. Prueba rápida con curl

```
curl -G "https://fbhzibcingdanzlrslrq.supabase.co/rest/v1/productos" \
  -H "apikey: sb_publishable_MS2cjrHBl0_Jq1sqTSfckA_lzb7SWXT" \
  --data-urlencode "busqueda=ilike.*fernet*" --data-urlencode "limit=3"
```

## 2. Las consultas que vas a necesitar

| Objetivo | Petición |
|---|---|
| Buscar por palabras | `GET /productos?and=(busqueda.ilike.*fernet*,busqueda.ilike.*branca*)` |
| Producto y precios en una sola llamada | agregar `&select=ean,nombre,precios(cadena,precio_promedio)` |
| Un producto | `GET /productos?ean=eq.7790290101602` |
| Precios de un EAN, del más barato al más caro | `GET /precios?ean=eq.7790290101602&order=precio_promedio.asc` |
| Navegar por categoría | `GET /productos?categoria=eq.Bebidas&subcategoria=eq.Cervezas` |
| Paginación | `&limit=20&offset=40` (máximo 1000 filas por petición) |
| Total de filas | header `Prefer: count=exact` y leer `Content-Range` |

Los joins funcionan porque `precios.ean` referencia a `productos.ean`.

### Campos normalizados

Cada producto trae, además de los datos originales de la fuente, una estructura uniforme:

| campo | ejemplo |
|---|---|
| `nombre_normalizado` | `Fernet Branca Menta 750 ml` |
| `marca_normalizada` | `Branca` (vacía si no se pudo determinar) |
| `cantidad` y `unidad` | `750` y `ml` (las unidades son solo `g`, `ml` o `un`; `kg` y `l` se convierten) |

Para mostrar productos en pantalla usa `nombre_normalizado`; `nombre` y `marca` quedan como respaldo.

## 3. Usarla desde TypeScript

`examples/api.ts` encapsula todo lo anterior (tipado, sin dependencias). Cópialo a tu aplicación:

```ts
import { searchProducts, getByEan, cheapestPrice } from "./api.ts";

const results = await searchProducts("fernet branca 750", 10); // Product[] con precios
const best = cheapestPrice(results[0]);                          // { cadena, precio_promedio, ... }
const detail = await getByEan(results[0].ean);
```

Para apuntar a otro proyecto o clave, usa las variables de entorno `SEPITA_URL` y `SEPITA_KEY`
(en un bundler de navegador, reemplaza `process.env` por tu propia configuración).

### Reglas para que la búsqueda funcione

1. **Normaliza el texto del usuario igual que el dataset**: minúsculas, sin tildes y puntuación convertida en espacios
   (`normalize()` en `api.ts`). La columna `busqueda` está guardada así.
2. **Un `ilike` por palabra, combinados con `and`**, para que el orden de las palabras no importe.
3. Como las palabras normalizadas solo contienen `a-z0-9`, no pueden romper la sintaxis del filtro.
   No pases texto crudo del usuario en la URL.

## 4. Ejecutar el ejemplo completo

```
node examples/api-demo.ts
```

Salida esperada (los precios cambian a diario; el formato se mantiene):

```
Search "Fernet Branca 750" -> 3 results
- Aperitivo Fernet 750 ml [Vittone] EAN 7790290101459, 9 chains, cheapest: Supermercados DIA $6765.91
- Aperitivo Fernet 750 ml [Branca] EAN 7790290101602, 9 chains, cheapest: Sup. Unicoop $13734
- Fernet Menta 750 ml [Branc] EAN 7790290101473, 8 chains, cheapest: Sup. Unicoop $14689

By EAN 7790290101459: Bebidas / Aperitivos y destilados, median $7200
  Cooperativa Obrera Limitada de Consumo y Vivienda: $7473.14 (155 branches)
  COTO CICSA: $7208.89 (102 branches)
  La Anonima: $6866.67 (183 branches)
```

## Alternativa: supabase-js

```ts
import { createClient } from "@supabase/supabase-js";
const sb = createClient("https://fbhzibcingdanzlrslrq.supabase.co", "sb_publishable_MS2cjrHBl0_Jq1sqTSfckA_lzb7SWXT");
const { data } = await sb.from("productos").select("ean,nombre,precios(cadena,precio_promedio)")
  .ilike("busqueda", "%fernet%").ilike("busqueda", "%branca%").limit(10);
```

## Cosas a tener en cuenta

- Los datos se actualizan a diario (la fecha de la fuente está en `metadata.json` de la release `datos`).
- Los precios son precios de lista por cadena y no están depurados: hay valores atípicos (por ejemplo, $994,90 para un fernet de 750 cc).
- Las categorías se infieren por palabras clave; algunos productos están mal clasificados.
- En el plan gratuito de Supabase, un proyecto se pausa tras una semana sin actividad. La recarga diaria lo evita.
