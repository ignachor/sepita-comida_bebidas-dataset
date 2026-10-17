# Normalización de productos

Objetivo: cada producto con la misma estructura (marca_normalizada, cantidad, unidad, nombre_normalizado), conservando las columnas originales.

- [x] T1 `normalizer.py`: unidades, cantidad, ruido de envase, mayúsculas, marcas truncadas (+ `marcas.csv` de correcciones) con tests
- [x] T2 integrar en `build_dataset.py` (columnas nuevas en `productos.csv`) y probar con zips locales
- [ ] T3 (migración aplicada; falta cargar: la PC no tiene IPv6, usar Session pooler) migración de Supabase + `load.sql`, y publicar con `update.sh`
- [ ] T4 documentar en README y tutoriales

Ruta: directa en línea (archivos pequeños, ya entendidos). Espejo en Engram pendiente: conflicto de proyecto sin resolver.
