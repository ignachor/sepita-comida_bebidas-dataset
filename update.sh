#!/usr/bin/env bash
# Build the dataset from the latest SEPA dump and publish it to the `datos` release.
# Runs locally because datos.produccion.gob.ar blocks GitHub-hosted runners (403).
set -euo pipefail
cd "$(dirname "$0")"
python3 test_dataset.py
python3 build_dataset.py
gh release view datos >/dev/null 2>&1 || gh release create datos \
  --title "Dataset de comidas y bebidas (SEPA)" \
  --notes "Actualizado automáticamente todos los días. Fuente: Precios Claros / SEPA, Secretaría de Comercio (CC BY 4.0)."
gh release upload datos dist/comidas_y_bebidas.csv dist/metadata.json --clobber
echo "published $(date -Is)"
