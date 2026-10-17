-- Replace the whole dataset atomically (run with psql --single-transaction, from the repo root).
truncate public.precios, public.productos;
\copy public.productos (ean, nombre, marca, categoria, subcategoria, cantidad_presentacion, unidad_presentacion, n_cadenas, precio_mediano, busqueda) from 'dist/productos.csv' with (format csv, header, force_not_null (marca))
\copy public.precios (ean, cadena, n_sucursales, precio_min, precio_promedio, precio_max, precio_referencia, unidad_referencia) from 'dist/precios.csv' with (format csv, header)
analyze public.productos;
analyze public.precios;
