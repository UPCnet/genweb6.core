# Prueba de Concepto: collective.taskqueue2

Documentación para probar el procesamiento asíncrono de limpieza de PDFs usando collective.taskqueue2.

## Cambios Realizados

### 1. Dependencia añadida
- `setup.py`: Añadido `collective.taskqueue2` a `install_requires`

### 2. Nuevo módulo de tareas asíncronas
- `src/genweb6/core/async_tasks.py`: Contiene las tareas asíncronas

### 3. Subscriber modificado
- `src/genweb6/core/subscribers.py`: Modificado `clean_pdf_on_upload_file()` para soportar modo asíncrono

## Configuración para Prueba Local

### Paso 1: Instalar dependencias

```bash
cd /Users/pmarinas/Development/Plone/genweb6.buildout
./bootstrap.sh
```

Esto instalará `collective.taskqueue2` y sus dependencias (Huey).

### Paso 2: Configurar variables de entorno

Edita el archivo de configuración de tu instancia para añadir las variables de entorno:

**Opción A: Para testing rápido (en terminal)**

```bash
export GENWEB_ASYNC_PDF_CLEANING=1
export HUEY_CONSUMER=1
export HUEY_TASKQUEUE_URL=sqlite:///tmp/huey_genweb_test.db
export HUEY_LOG_LEVEL=DEBUG
export HUEY_WORKERS=2

# Luego inicia la instancia
./bin/instance fg
```

**Opción B: Añadir al buildout (más permanente)**

Edita `genwebupc.cfg` y añade en la sección `[instance]`:

```ini
environment-vars =
    # ... variables existentes ...
    GENWEB_ASYNC_PDF_CLEANING 1
    HUEY_CONSUMER 1
    HUEY_TASKQUEUE_URL sqlite:///var/huey/genweb_test.db
    HUEY_LOG_LEVEL DEBUG
    HUEY_WORKERS 2
```

Luego reconstruye y reinicia:

```bash
./bootstrap.sh
./bin/instance fg
```

### Paso 3: Verificar que está funcionando

Al iniciar la instancia, deberías ver en los logs:

```
INFO [genweb6.core.async_tasks] collective.taskqueue2 disponible - Modo asíncrono habilitado
INFO [huey.consumer] Huey consumer started with 2 threads, PID XXXXX
INFO [huey.consumer] Scheduler runs every 1 second(s).
INFO [huey.consumer] The following commands are available:
+ genweb6.core.async_tasks.clean_pdf_async
```

## Probar la Funcionalidad

### Prueba 1: Subir un PDF

1. Accede a tu sitio Plone local
2. Crea o edita un objeto File
3. Sube un PDF
4. Observa los logs:

**Modo asíncrono activado:**
```
INFO [genweb6.core.subscribers] [ASYNC] PDF encolado para limpieza asíncrona: http://...
INFO [genweb6.core.async_tasks] [ASYNC TASK START] Limpiando PDF: /Plone/...
INFO [genweb6.core.subscribers] [GW6 METADADAS CHECK SIGNED] ...
INFO [genweb6.core.async_tasks] [ASYNC TASK SUCCESS] PDF limpiado: /Plone/...
```

**Modo síncrono (sin variables de entorno):**
```
INFO [genweb6.core.subscribers] [GW6 METADADAS CHECK SIGNED] ...
```

### Prueba 2: Verificar estado de la cola

Accede a: `http://localhost:11001/Plone/@@taskqueue-stats`

Debería devolver JSON:
```json
{
  "pending": 0,
  "scheduled": 0
}
```

### Prueba 3: Comparar tiempos

**Modo síncrono (actual):**
- Usuario espera durante toda la limpieza (~2-5 segundos según PDF)

**Modo asíncrono:**
- Usuario recibe respuesta inmediata (<1 segundo)
- Limpieza ocurre en background

## Backends de Almacenamiento para Probar

### SQLite (Recomendado para testing local)
```bash
HUEY_TASKQUEUE_URL=sqlite:///tmp/huey_genweb_test.db
```

Ventajas:
- Sin configuración adicional
- Persiste tareas (sobrevive reinicios)
- Perfecto para desarrollo local

### Memory (Solo para testing rápido)
```bash
HUEY_TASKQUEUE_URL=memory://
```

Ventajas:
- Más rápido
- No usa disco

Desventajas:
- No persiste (se pierde al reiniciar)

### File (Alternativa a SQLite)
```bash
HUEY_TASKQUEUE_URL=file:///tmp/huey_queue
```

## Desactivar Modo Asíncrono

Para volver al comportamiento actual (síncrono), simplemente:

```bash
unset GENWEB_ASYNC_PDF_CLEANING
# O
export GENWEB_ASYNC_PDF_CLEANING=0
```

Luego reinicia la instancia. El código funcionará exactamente como antes.

## Troubleshooting

### collective.taskqueue2 no disponible
**Síntoma:** Logs muestran "collective.taskqueue2 NO disponible"

**Solución:**
```bash
cd /Users/pmarinas/Development/Plone/genweb6.buildout
./bootstrap.sh
```

### Tareas no se procesan
**Síntoma:** PDFs no se limpian en modo asíncrono

**Verificar:**
1. `HUEY_CONSUMER=1` está configurado
2. Logs muestran "Huey consumer started"
3. Verificar estado en `@@taskqueue-stats`

### Errores de permisos con SQLite
**Síntoma:** Error al escribir en base de datos

**Solución:**
```bash
mkdir -p /tmp/huey
chmod 777 /tmp/huey
HUEY_TASKQUEUE_URL=sqlite:////tmp/huey/genweb_test.db
```

## Siguiente Paso: Prueba en Producción

Si la prueba local funciona bien, para desplegar en las 20 máquinas:

1. Configurar variables de entorno en cada instancia:
   ```bash
   GENWEB_ASYNC_PDF_CLEANING=1
   HUEY_CONSUMER=1
   HUEY_TASKQUEUE_URL=sqlite:///var/huey/zc${INSTANCE_NUM}.db
   HUEY_WORKERS=2
   ```

2. Cada instancia tendrá su propia cola SQLite

3. Monitorear logs para verificar funcionamiento

## Rollback

Si necesitas volver atrás:

1. Desactivar variables de entorno
2. El código volverá automáticamente al modo síncrono (comportamiento actual)
3. No es necesario cambiar código ni reiniciar
