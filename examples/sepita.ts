const BASE = "https://github.com/ignachor/sepita-comida_bebidas-dataset/releases/download/datos";

export interface Product {
  categoria: "Comidas" | "Bebidas";
  subcategoria: string;
  cadena: string;
  ean: string;
  descripcion: string;
  marca: string;
  cantidadPresentacion: string;
  unidadPresentacion: string;
  nSucursales: number;
  precioMin: number;
  precioPromedio: number;
  precioMax: number;
  precioReferencia: number | null;
  unidadReferencia: string;
}

export interface Metadata {
  fuente: string;
  fuente_actualizada: string;
  filas: number;
  filas_descartadas_ean_invalido: number;
}

/** Minimal RFC 4180 parser: handles quoted fields, escaped quotes and commas inside quotes. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field); field = "";
      if (row.length > 1) rows.push(row);
      row = [];
    } else field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  return rows;
}

export async function fetchMetadata(): Promise<Metadata> {
  const res = await fetch(`${BASE}/metadata.json`);
  if (!res.ok) throw new Error(`metadata: HTTP ${res.status}`);
  return res.json();
}

export async function loadProducts(): Promise<Product[]> {
  const res = await fetch(`${BASE}/comidas_y_bebidas.csv`); // fetch follows GitHub's redirect
  if (!res.ok) throw new Error(`csv: HTTP ${res.status}`);
  const text = (await res.text()).replace(/^﻿/, ""); // strip the UTF-8 BOM
  const [, ...rows] = parseCsv(text); // first row is the header
  return rows.map((r) => ({
    categoria: r[0] as Product["categoria"],
    subcategoria: r[1],
    cadena: r[2],
    ean: r[3],
    descripcion: r[5],
    marca: r[6],
    cantidadPresentacion: r[7],
    unidadPresentacion: r[8],
    nSucursales: Number(r[9]),
    precioMin: Number(r[10]),
    precioPromedio: Number(r[11]),
    precioMax: Number(r[12]),
    precioReferencia: r[13] === "" ? null : Number(r[13]),
    unidadReferencia: r[14],
  }));
}

export const byEan = (ps: Product[], ean: string) => ps.filter((p) => p.ean === ean);

export const cheapest = (ps: Product[]) =>
  ps.reduce<Product | undefined>((best, p) => (!best || p.precioPromedio < best.precioPromedio ? p : best), undefined);

export const search = (ps: Product[], text: string) => {
  const q = text.toUpperCase();
  return ps.filter((p) => p.descripcion.toUpperCase().includes(q));
};
