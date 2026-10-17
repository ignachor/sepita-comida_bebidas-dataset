# Hoja de ruta: actualizaciones sin intervención

## Estado actual (opción C, en uso)

`update.sh` corre en la PC del propietario mediante la tarea de Windows `SepitaDatasetUpdate` (todos los días a las 20:00).
Descarga el volcado de SEPA, genera los CSV, publica la release `datos` y recarga Supabase.
Solo se ejecuta mientras la PC está encendida (`StartWhenAvailable` recupera las ejecuciones perdidas).

## Por qué no puede correr en la nube tal como está (verificado el 2026-10-17)

- `datos.produccion.gob.ar` responde **403** a los runners alojados por GitHub (API, página del dataset y zip).
- El volcado diario pesa **324 MB** (~92 s de descarga) y requiere ~6 min de CPU para procesarse.
  Es un zip de zips, por lo que no se puede procesar en streaming. Las Edge Functions de Supabase (límites de memoria y
  de tiempo de ejecución) no pueden hacerlo. Esos límites provienen de la documentación de Supabase y no se volvieron a verificar.

## Planificado: opción B, VM siempre encendida

Ejecutar `update.sh` en una VM gratuita que esté siempre encendida (por ejemplo, Oracle Cloud Free Tier con Ubuntu).

1. **Condición previa: probar la IP.** Desde la VM: `curl -sI https://datos.produccion.gob.ar/api/3/action/package_show?id=sepa-precios`.
   Continuar solo si responde `HTTP/2 200`. Una IP de centro de datos podría estar bloqueada igual que las de GitHub.
2. Instalar `python3`, `git`, `gh` y `postgresql-client`; ejecutar `gh auth login`.
3. Clonar el repositorio y crear `.env` a partir de `.env.example` (con la cadena de conexión de Supabase).
4. Programar con cron, por ejemplo: `0 20 * * * /ruta/a/update.sh >> /ruta/a/update.log 2>&1`
   (atención a la zona horaria de la VM: ART es UTC-3).
5. Deshabilitar la tarea de Windows `SepitaDatasetUpdate` para evitar dos procesos escribiendo a la vez.

Si la IP de la VM está bloqueada: probar con otro proveedor o mantener la opción C.

## Descartado por ahora

- **Supabase descarga los CSV de la release (pg_cron + Edge Function):** solo traslada la carga de 7 MB; el
  procesamiento pesado seguiría ejecutándose en la PC.
