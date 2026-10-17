import { byEan, cheapest, fetchMetadata, loadProducts, parseCsv, search } from "./sepita.ts";

// self-check of the parser on the tricky cases (commas and quotes inside fields)
const parsed = parseCsv('a,b\n"x, y","say ""hi"""\n');
if (parsed[1][0] !== "x, y" || parsed[1][1] !== 'say "hi"') throw new Error("parseCsv broken");

const meta = await fetchMetadata();
console.log(`Source: ${meta.fuente} (${meta.fuente_actualizada}), ${meta.filas} rows`);

const products = await loadProducts();

const yerbas = search(products, "yerba");
console.log(`\n${yerbas.length} products match "yerba". Cheapest:`);
const best = cheapest(yerbas);
if (best) console.log(`  ${best.descripcion} @ ${best.cadena}: $${best.precioPromedio}`);

// pick the yerba EAN sold by the most chains, then compare prices across them
const chains = new Map<string, number>();
for (const p of yerbas) chains.set(p.ean, (chains.get(p.ean) ?? 0) + 1);
const [topEan] = [...chains.entries()].sort((a, b) => b[1] - a[1])[0];
const sample = byEan(products, topEan);
console.log(`\n${sample[0].descripcion} (EAN ${topEan}) across chains:`);
for (const p of sample.sort((a, b) => a.precioPromedio - b.precioPromedio))
  console.log(`  ${p.cadena.padEnd(24)} $${p.precioPromedio}  (${p.nSucursales} branches)`);
