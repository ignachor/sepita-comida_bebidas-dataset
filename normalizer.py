"""Deterministic normalisation of product name, brand and quantity (same input -> same output)."""
import csv
import re
from bisect import bisect_left
from pathlib import Path

# unit spelling (lowercase, no dots) -> (base unit, factor to base). Bases: g, ml, un.
UNITS = {}
for _names, _base, _factor in [
    ("g gr grm grs gramos", "g", 1), ("kg kgm kgr kilo kilos", "g", 1000),
    ("ml cc cm3 cmq", "ml", 1), ("l lt lts ltr litro litros", "ml", 1000),
    ("un uni unid unida unidad unidades u ea ud cu", "un", 1),
]:
    for _n in _names.split():
        UNITS[_n] = (_base, _factor)

KEEP_UPPER = {"TACC", "UHT", "IPA", "PET", "XL", "BBQ", "DOP", "SA", "UD", "LED"}
LOWER_WORDS = {"de", "del", "con", "sin", "y", "e", "para", "en", "al", "la", "el", "los", "las", "a", "o", "x"}
PACKAGING = re.compile(r"\b[A-Za-z]{2,4}-(\d+(?:[.,]\d+)?)-([A-Za-z]+)\.?", re.I)  # e.g. BOT-750-ml. PZA-1-un. DOY-400-gr.
QTY = re.compile(r"(?<!\w)(?<!\d[.,])(?:x\s*)?(\d+(?:[.,]\d+)?)\s*(" + "|".join(sorted(UNITS, key=len, reverse=True)) + r")(?![a-z0-9])\.?", re.I)
DOT = re.compile(r"(?<!\d)\.|\.(?!\d)")
LETTERS = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")


def parse_qty(cantidad, unidad):
    """(value in base unit, base unit) or (None, unit) when the unit is unknown or the amount is not a number."""
    key = unidad.lower().replace(".", "").strip()
    try:
        value = float(str(cantidad).replace(",", "."))
    except ValueError:
        return None, key
    if key not in UNITS:
        return None, key
    base, factor = UNITS[key]
    return round(value * factor, 3), base


def fmt_num(x):
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def smart_title(text):
    """'fernet BRANCA menta' -> 'Fernet Branca Menta'; keeps 7UP, acronyms and lowercases connectors."""
    out = []
    for i, tok in enumerate(text.split()):
        if any(c.isdigit() for c in tok) and any(c.isalpha() for c in tok):
            out.append(tok.upper())
            continue

        def cb(m):
            w = m.group(0)
            if w.upper() in KEEP_UPPER:
                return w.upper()
            if i > 0 and w.lower() in LOWER_WORDS:
                return w.lower()
            return w[:1].upper() + w[1:].lower()

        out.append(LETTERS.sub(cb, tok))
    return " ".join(out)


def clean_name(name, cantidad, unidad):
    """Drop packaging noise and the size already given by cantidad/unidad; returns (name, value, base)."""
    value, base = parse_qty(cantidad, unidad)
    packaging = [parse_qty(m.group(1), m.group(2)) for m in PACKAGING.finditer(name)]
    s = PACKAGING.sub(" ", name)
    named = [parse_qty(m.group(1), m.group(2)) for m in QTY.finditer(s)]
    sizes = {q for q in packaging + named if q[0] is not None and q[1] in ("g", "ml")}
    if value is None or (base == "un" and value == 1):
        # a lone weight/volume in the name wins over a missing quantity or just "1 unit"
        if len(sizes) == 1:
            value, base = next(iter(sizes))
    elif base in ("g", "ml"):
        same = {v for v, b in sizes if b == base}
        # declared smaller than the name's size = unit slip in the source (0.75 "ml" for 750 ml)
        if len(same) == 1 and value < next(iter(same)):
            value = next(iter(same))
    same = {v for v, b in sizes if b == base}

    def drop_own_size(m):
        v, b = parse_qty(m.group(1), m.group(2))
        if value is None or b != base:
            return m.group(0)
        return " " if v == value or (base in ("g", "ml") and len(same) <= 1) else m.group(0)

    s = QTY.sub(drop_own_size, s)
    s = DOT.sub(" ", s).replace(",", " ").replace("_", " ").strip(" *-")
    s = re.sub(r"^\(\w{1,2}\)\s*", "", s)  # leading tags like "(F)"
    return smart_title(re.sub(r"\s+", " ", s)) or smart_title(name), value, base


def load_overrides(path=Path(__file__).with_name("marcas.csv")):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {r["alias"].strip().upper(): r["marca"].strip() for r in csv.DictReader(f) if r.get("alias")}


class Brands:
    """Completes a truncated brand only when the product name contains the full word(s)."""

    def __init__(self, overrides=None):
        self.overrides = overrides or {}

    def complete(self, brand, name):
        b = brand.strip().upper()
        if not b or b.startswith("NO APLICA"):
            return ""
        if b in self.overrides:
            return self.overrides[b]
        key = " ".join(re.findall(r"[A-Z0-9Ñ]+", b))
        padded = " " + " ".join(re.findall(r"[A-Z0-9Ñ]+", name.upper())) + " "
        if not key or f" {key} " in padded:  # brand appears whole (FANTA in "FANTA NARANJA"): not truncated
            return smart_title(b)
        m = re.search(" " + re.escape(key) + r"([A-ZÑ]+) ", padded)  # SALEN -> SALENTEIN
        return smart_title(key + m.group(1)) if m else smart_title(b)


def display_name(name, value, base):
    if value is None:
        return name
    if base == "un" and value == 1:
        return name
    return f"{name} {fmt_num(value)} {base}"
