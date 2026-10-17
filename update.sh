#!/usr/bin/env bash
# Build the dataset from the latest SEPA dump and publish it to the `datos` release.
# Runs locally because datos.produccion.gob.ar blocks GitHub-hosted runners (403).
set -euo pipefail
cd "$(dirname "$0")"
# scheduled tasks run a non-interactive shell without brew on PATH
[ -d /home/linuxbrew/.linuxbrew/bin ] && export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
# never keep the downloaded dump or the built CSV locally, pass or fail
trap 'rm -rf dist' EXIT
python3 test_dataset.py
python3 build_dataset.py
gh release view datos >/dev/null 2>&1 || gh release create datos \
  --title "Dataset de comidas y bebidas (SEPA)" \
  --notes "Actualizado automáticamente todos los días. Fuente: Precios Claros / SEPA, Secretaría de Comercio (CC BY 4.0)."
gh release upload datos dist/productos.csv dist/precios.csv dist/comidas_y_bebidas.csv dist/metadata.json --clobber
echo "published $(date -Is)"
