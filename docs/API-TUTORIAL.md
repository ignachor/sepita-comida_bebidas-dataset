# Tutorial: using the REST API from another app

Supabase exposes the two tables (`productos`, `precios`) as a REST API (PostgREST). Your app only
needs a URL and a public key. No backend and no dependencies are required.

| | |
|---|---|
| Base URL | `https://fbhzibcingdanzlrslrq.supabase.co/rest/v1` |
| Header | `apikey: sb_publishable_MS2cjrHBl0_Jq1sqTSfckA_lzb7SWXT` |

The publishable key is **meant to be public** (browser, mobile app). Row Level Security only
allows `SELECT`; any write returns 401. Never ship the `service_role` key or the DB password.

## 1. Quick check with curl

```
curl -G "https://fbhzibcingdanzlrslrq.supabase.co/rest/v1/productos" \
  -H "apikey: sb_publishable_MS2cjrHBl0_Jq1sqTSfckA_lzb7SWXT" \
  --data-urlencode "busqueda=ilike.*fernet*" --data-urlencode "limit=3"
```

## 2. The queries you need

| Goal | Request |
|---|---|
| Search by words | `GET /productos?and=(busqueda.ilike.*fernet*,busqueda.ilike.*branca*)` |
| Product + prices in one call | add `&select=ean,nombre,precios(cadena,precio_promedio)` |
| One product | `GET /productos?ean=eq.7790290101602` |
| Prices of one EAN, cheapest first | `GET /precios?ean=eq.7790290101602&order=precio_promedio.asc` |
| Category browsing | `GET /productos?categoria=eq.Bebidas&subcategoria=eq.Cervezas` |
| Pagination | `&limit=20&offset=40` (max 1000 rows per request) |
| Total count | header `Prefer: count=exact`, read `Content-Range` |

Joins work because `precios.ean` references `productos.ean`.

## 3. Use it from TypeScript

`examples/api.ts` wraps all of the above (typed, no dependencies). Copy it into your app:

```ts
import { searchProducts, getByEan, cheapestPrice } from "./api.ts";

const results = await searchProducts("fernet branca 750", 10); // Product[] with prices
const best = cheapestPrice(results[0]);                          // { cadena, precio_promedio, ... }
const detail = await getByEan(results[0].ean);
```

Point it at another project or key with the env vars `SEPITA_URL` and `SEPITA_KEY`
(in a browser bundler, replace `process.env` with your own config).

### Rules that make search work

1. **Normalise the user's text exactly like the dataset**: lowercase, no accents, punctuation to
   spaces (`normalize()` in `api.ts`). `busqueda` is stored that way.
2. **One `ilike` per word, combined with `and`**, so word order does not matter.
3. Because normalised words only contain `a-z0-9`, they cannot break the filter syntax.
   Do not pass raw user input into the URL.

## 4. Run the full example

```
node examples/api-demo.ts
```

Expected output (prices change daily; the shape stays the same):

```
Search "Fernet Branca 750" -> 3 results
- APERITIVO FERNET [VITTONE] EAN 7790290101459, 9 chains, cheapest: Supermercados DIA $6765.91
- APERITIVO FERNET [BRANCA] EAN 7790290101602, 9 chains, cheapest: Sup. Unicoop $13734
- FERNET MENTA [BRANC] EAN 7790290101473, 8 chains, cheapest: Sup. Unicoop $14689

By EAN 7790290101459: Bebidas / Aperitivos y destilados, median $7200
  Cooperativa Obrera Limitada de Consumo y Vivienda: $7473.14 (155 branches)
  COTO CICSA: $7208.89 (102 branches)
  La Anonima: $6866.67 (183 branches)
```

## Alternative: supabase-js

```ts
import { createClient } from "@supabase/supabase-js";
const sb = createClient("https://fbhzibcingdanzlrslrq.supabase.co", "sb_publishable_MS2cjrHBl0_Jq1sqTSfckA_lzb7SWXT");
const { data } = await sb.from("productos").select("ean,nombre,precios(cadena,precio_promedio)")
  .ilike("busqueda", "%fernet%").ilike("busqueda", "%branca%").limit(10);
```

## Things to know

- Data refreshes daily (see the `datos` release `metadata.json` for the source date).
- Prices are list prices per chain and are not cleaned: expect outliers (e.g. $994.90 for a 750 cc fernet).
- Categories are keyword-based; a few products are misclassified.
- Free-tier Supabase pauses a project after a week without activity. A daily reload prevents it.
