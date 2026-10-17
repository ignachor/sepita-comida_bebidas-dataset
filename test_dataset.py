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
