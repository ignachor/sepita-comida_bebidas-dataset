// Client for the Supabase REST API (PostgREST). Zero dependencies, Node 22.18+ / browsers / Deno / Bun.
const URL_BASE = process.env.SEPITA_URL ?? "https://fbhzibcingdanzlrslrq.supabase.co";
// Publishable key: safe to ship in a browser app. It can only READ (RLS blocks writes).
const KEY = process.env.SEPITA_KEY ?? "sb_publishable_MS2cjrHBl0_Jq1sqTSfckA_lzb7SWXT";

export interface Price {
  cadena: string;
  n_sucursales: number;
  precio_min: number;
  precio_promedio: number;
  precio_max: number;
}

export interface Product {
  ean: string;
  nombre: string;
  marca: string;
  categoria: "Comidas" | "Bebidas";
  subcategoria: string;
  n_cadenas: number;
  precio_mediano: number;
  precios: Price[];
}

/** Same normalisation the dataset uses for `busqueda`: lowercase, no accents, punctuation -> spaces. */
export function normalize(text: string): string {
  return text.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, " ").trim();
}

async function get<T>(path: string, params: Record<string, string>): Promise<T> {
  const url = new URL(`/rest/v1/${path}`, URL_BASE);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const res = await fetch(url, { headers: { apikey: KEY } });
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status} ${await res.text()}`);
  return res.json();
}

const SELECT = "ean,nombre,marca,categoria,subcategoria,n_cadenas,precio_mediano,precios(cadena,n_sucursales,precio_min,precio_promedio,precio_max)";

/** Every word of the query must appear in `busqueda`. Most widely sold products first. */
export function searchProducts(query: string, limit = 20, offset = 0): Promise<Product[]> {
  const words = normalize(query).split(" ").filter(Boolean);
  if (words.length === 0) return Promise.resolve([]);
  // words are [a-z0-9] only, so they can't break the filter syntax
  const filter = words.length === 1 ? { busqueda: `ilike.*${words[0]}*` } : { and: `(${words.map((w) => `busqueda.ilike.*${w}*`).join(",")})` };
  return get<Product[]>("productos", { select: SELECT, ...filter, order: "n_cadenas.desc,nombre.asc", limit: String(limit), offset: String(offset) });
}

export async function getByEan(ean: string): Promise<Product | undefined> {
  if (!/^\d{8,13}$/.test(ean)) throw new Error("invalid EAN");
  return (await get<Product[]>("productos", { select: SELECT, ean: `eq.${ean}` }))[0];
}

export const cheapestPrice = (p: Product) => [...p.precios].sort((a, b) => a.precio_promedio - b.precio_promedio)[0];
