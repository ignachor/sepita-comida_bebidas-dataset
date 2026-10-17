"""Download the latest SEPA dump and build comidas_y_bebidas.csv (one row per chain+EAN)."""
import argparse
import csv
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

from classifier import cls

CKAN = "https://datos.produccion.gob.ar/api/3/action/package_show?id=sepa-precios"
COLUMNS = ["categoria", "subcategoria", "cadena", "codigo_producto", "es_ean", "descripcion", "marca",
           "cantidad_presentacion", "unidad_presentacion", "n_sucursales", "precio_min",
           "precio_promedio", "precio_max", "precio_referencia", "unidad_referencia"]
csv.field_size_limit(10**7)
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def fetch(url, timeout):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=timeout)


def valid_ean(code):
    """EAN-8/13 with a valid check digit; UPC-A (12) is normalised to EAN-13. None if invalid."""
    if not code.isdigit() or len(code) not in (8, 12, 13):
        return None
    if len(code) == 12:
        code = "0" + code
    digits = [int(x) for x in code[:-1]][::-1]
    check = (10 - sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(digits)) % 10) % 10
    return code if check == int(code[-1]) else None


def latest_resource():
    with fetch(CKAN, 60) as r:
        res = json.load(r)["result"]["resources"]
    zips = [x for x in res if (x.get("format") or "").upper() == "ZIP"]
    return max(zips, key=lambda x: x["last_modified"])


def download(url, dest):
    with fetch(url, 120) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def inner_zips(path):
    """Yield (name, zipfile) for each per-chain zip, from the outer SEPA zip or a folder of them."""
    path = Path(path)
    if path.is_dir():
        for p in sorted(path.glob("*.zip")):
            try:
                yield p.name, zipfile.ZipFile(p)
            except zipfile.BadZipFile:
                print(f"skip (not a zip): {p.name}", file=sys.stderr)
        return
    with zipfile.ZipFile(path) as outer:
        for n in sorted(outer.namelist()):
            if n.endswith(".zip"):
                try:
                    yield n, zipfile.ZipFile(io.BytesIO(outer.read(n)))
                except zipfile.BadZipFile:
                    print(f"skip (not a zip): {n}", file=sys.stderr)


def rows(z, name):
    with z.open(name) as raw:
        r = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline=""), delimiter="|")
        next(r)
        yield from r


def aggregate(source):
    agg, dropped = {}, 0
    for n, z in inner_zips(source):
        names = set(z.namelist())
        if not {"comercio.csv", "productos.csv"} <= names:
            print(f"skip (missing csv): {n}", file=sys.stderr)
            continue
        banner = next(rows(z, "comercio.csv"))[4].strip()
        for row in rows(z, "productos.csv"):
            if len(row) < 13:
                continue
            c = cls(row[5].strip())
            if not c:
                continue
            ean = valid_ean(row[3].strip())
            if row[4].strip() != "1" or not ean:
                dropped += 1
                continue
            try:
                p = float(row[9])
            except ValueError:
                continue
            if p <= 0:
                continue
            try:
                ref = float(row[10])
            except ValueError:
                ref = None
            a = agg.get((banner, ean))
            if a is None:
                agg[(banner, ean)] = dict(c=c, ean=row[4].strip(), d=" ".join(row[5].split()), m=row[8].strip(),
                                          q=row[6].strip(), u=row[7].strip(), s={row[2]}, lo=p, hi=p, sum=p,
                                          n=1, ref=ref, ru=row[12].strip())
            else:
                a["s"].add(row[2]); a["lo"] = min(a["lo"], p); a["hi"] = max(a["hi"], p)
                a["sum"] += p; a["n"] += 1
                if a["ref"] is None:
                    a["ref"] = ref
    return agg, dropped


def write(agg, out):
    items = sorted(agg.items(), key=lambda x: (x[1]["c"], x[1]["d"], x[0][0]))
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for (banner, code), a in items:
            w.writerow([a["c"][0], a["c"][1], banner, code, a["ean"], a["d"], a["m"], a["q"], a["u"], len(a["s"]),
                        round(a["lo"], 2), round(a["sum"] / a["n"], 2), round(a["hi"], 2),
                        "" if a["ref"] is None else round(a["ref"], 2), a["ru"]])
    return len(items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="local outer SEPA zip or folder of per-chain zips (skips download)")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    meta = {}
    source = args.source
    if not source:
        res = latest_resource()
        source = out / "sepa.zip"
        print(f"downloading {res['name']} (modified {res['last_modified']})")
        download(res["url"], source)
        meta = {"fuente": res["name"], "fuente_actualizada": res["last_modified"]}
    agg, dropped = aggregate(source)
    n = write(agg, out / "comidas_y_bebidas.csv")
    meta.update(filas=n, filas_descartadas_ean_invalido=dropped)
    (out / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    if not args.source:
        Path(source).unlink()
    print(meta)


if __name__ == "__main__":
    main()
