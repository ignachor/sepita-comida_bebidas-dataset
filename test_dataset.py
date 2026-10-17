"""Run: python test_dataset.py"""
from build_dataset import valid_ean
from classifier import cls

assert valid_ean("7790070335968") == "7790070335968"
assert valid_ean("7790070335969") is None          # bad check digit
assert valid_ean("036000291452") == "0036000291452"  # UPC-A -> EAN-13
assert valid_ean("1234") is None and valid_ean("ABC") is None

assert cls("VINO MALBEC 750CC") == ("Bebidas", "Vinos y espumantes")
assert cls("YERBA MATE SUAVE ANDRESITO X 500 GRS") == ("Bebidas", "Infusiones")
assert cls("YOGUR FIRME VAINILLA, MILKAUT") == ("Comidas", "Lácteos y huevos")
assert cls("AGUA MICELAR CON ALOE VERA") is None
assert cls("SHAMPOO MANZANA") is None
assert cls("DETERGENTE LIMON") is None
print("ok")

from build_dataset import normalize
assert normalize("FERNET Branca, 750cc ÑOQUIS") == "fernet branca 750cc noquis"
print("ok normalize")

import normalizer as nz
assert nz.parse_qty("1.5", "LT") == (1500.0, "ml") and nz.parse_qty("2", "Kg.") == (2000.0, "g")
assert nz.parse_qty("6", "UNIDAD") == (6.0, "un") and nz.parse_qty("3", "mtr")[0] is None
name, v, b = nz.clean_name("fernet BRANCA menta x 750cc BOT-750-ml.", "750", "cc")
assert nz.display_name(name, v, b) == "Fernet Branca Menta 750 ml"
assert nz.display_name(*nz.clean_name("YERBA MATE X 500 GRS", "500", "grm")) == "Yerba Mate 500 g"
assert "354" in nz.clean_name("PACK 6 LATAS 354 CC", "6", "UNI")[0]  # a size different from cantidad is kept
assert nz.clean_name("GASEOSA 7UP LIMA", "1", "UNI")[0] == "Gaseosa 7UP Lima"
brands = nz.Brands()
assert brands.complete("SALEN", "VINO MALBEC SALENTEIN 750") == "Salentein"
assert brands.complete("NIETO", "VINO NIETO SENETINER MALBEC") == "Nieto"  # whole word in the name: not truncated
assert brands.complete("ARCOR", "GALLETITAS ARCOR") == "Arcor"
assert brands.complete("FANTA", "FANTA NARANJA 2L") == "Fanta"
assert brands.complete("SALEN", "VINO MALBEC") == "Salen"  # no evidence in the name -> not completed
assert brands.complete("QUESO RALLADO SERENI", "QUESO RALLADO SERENISIMA 70gr.") == "Queso Rallado Serenisima"
assert brands.complete("", "X") == "" and brands.complete("NO APLICA MARCA", "X") == ""
assert nz.Brands({"X": "Y"}).complete("x", "z") == "Y"  # manual overrides win
assert nz.display_name(*nz.clean_name("Vino CONTRACARA chardonnay BOT-750-ml.", "0.75", "ml")) == "Vino Contracara Chardonnay 750 ml"
assert nz.display_name(*nz.clean_name("BALSAMO BIFERDIL X 400 ML", "1", "ml")) == "Balsamo Biferdil 400 ml"
assert nz.display_name(*nz.clean_name("Frutillas GREEN LIFE 400g DOY-400-gr.", "1", "UNI")) == "Frutillas Green Life 400 g"
assert nz.display_name(*nz.clean_name("CAFE 20 SAQUITOS X 5G.", "100", "g")) == "Cafe 20 Saquitos 100 g"  # multipack keeps declared
assert nz.display_name(*nz.clean_name("CAFE LA MORENITA TORRADO INT.500G.", "500", "g")) == "Cafe la Morenita Torrado Int 500 g"
assert nz.Brands().complete("LEVITE", "AGUA LEVITEX1 2L") == "Levite"  # continuation must be letters only
print("ok normalizer")
