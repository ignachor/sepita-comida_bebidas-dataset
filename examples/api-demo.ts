import { cheapestPrice, getByEan, normalize, searchProducts } from "./api.ts";

if (normalize("  FERNET Branca, 750cc ÑOQUIS ") !== "fernet branca 750cc noquis") throw new Error("normalize broken");

const found = await searchProducts("Fernet Branca 750", 3);
console.log(`Search "Fernet Branca 750" -> ${found.length} results`);
for (const p of found) {
  const best = cheapestPrice(p);
  console.log(`- ${p.nombre} [${p.marca}] EAN ${p.ean}, ${p.n_cadenas} chains, cheapest: ${best.cadena} $${best.precio_promedio}`);
}

const one = await getByEan(found[0].ean);
console.log(`\nBy EAN ${one?.ean}: ${one?.categoria} / ${one?.subcategoria}, median $${one?.precio_mediano}`);
for (const pr of one?.precios.slice(0, 3) ?? []) console.log(`  ${pr.cadena}: $${pr.precio_promedio} (${pr.n_sucursales} branches)`);
