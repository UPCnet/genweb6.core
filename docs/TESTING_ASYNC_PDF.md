# Testing: Limpieza Asíncrona de PDFs

Guía completa de testing local y validación de persistencia.

## 🧪 Tests Disponibles

| Test | Duración | Objetivo |
|------|----------|----------|
| Test Básico | 2 min | Verificar que el sistema async funciona |
| Test Persistencia | 5 min | Verificar que tareas sobreviven reinicio |
| Test Carga | 10 min | Verificar comportamiento con múltiples PDFs |

## ✅ Test Básico: Funcionamiento Asíncrono

### Objetivo

Verificar que el usuario recibe respuesta inmediata y el procesamiento se hace en background.

### Pasos

#### 1. Configurar Modo Asíncrono

Edita `customizeme.cfg`:

```ini
[custom]
async_pdf_enabled = 1
huey_consumer = 1
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
huey_log_level = INFO  # Para ver los logs
huey_workers = 2
```

#### 2. Crear Directorio

```bash
mkdir -p var/huey
```

#### 3. Arrancar Instancia

```bash
./bin/instance fg
```

**Verificar en logs**:
```
INFO [genweb6.core.async_tasks] collective.taskqueue2 disponible - Modo asíncrono habilitado
INFO [huey.consumer] Huey consumer started with 2 threads
INFO [huey.consumer] The following commands are available:
+ genweb6.core.async_tasks.clean_pdf_async
```

#### 4. Subir un PDF

Desde el navegador:
```
http://localhost:11001/2/genwebupc/ca/documentacio/pdfs-test
```

**Observar**: La página responde **inmediatamente** (<0.1s)

#### 5. Verificar Logs

```bash
tail -30 var/log/instance.log | grep -E "ASYNC|huey"
```

**Esperado**:
```
INFO [genweb6.core.subscribers] [ASYNC] Programado para encolar después del commit
INFO [genweb6.core.async_tasks] [ASYNC MODE] Encolando limpieza PDF: ... (UID: abc123)
INFO [huey] Executing clean_pdf_async: ...
INFO [genweb6.core.async_tasks] [ASYNC TASK] Objeto encontrado por UID: abc123
INFO [genweb6.core.async_tasks] [ASYNC TASK START] Limpiando PDF: ...
ERROR [genweb6.core.subscribers] [GW6 METADADAS CHECK SIGNED] ... Tiempo: 0.001s
ERROR [genweb6.core.subscribers] [GW6 METADADAS CLEAN PDF] ... Tiempo: 0.3s
INFO [genweb6.core.subscribers] [OK] ... - PDF sense metadades
INFO [genweb6.core.async_tasks] [ASYNC TASK SUCCESS] PDF limpiado: ...
INFO [huey] executed in 0.4s
```

#### 6. Verificar Estado

```bash
curl http://localhost:11001/2/genwebupc/@@taskqueue-stats
```

**Esperado**:
```json
{"pending": 0, "scheduled": 0}
```

### ✅ Criterios de Éxito

- [ ] Instancia arranca con Huey consumer
- [ ] Usuario recibe respuesta inmediata (<0.1s)
- [ ] Logs muestran "[ASYNC MODE] Encolando"
- [ ] Worker procesa tarea en background
- [ ] PDF se limpia correctamente
- [ ] `@@taskqueue-stats` muestra pending: 0

---

## 🔄 Test de Persistencia: Sobrevivir Reinicios

### Objetivo

Verificar que tareas encoladas **persisten en disco** y se procesan tras reiniciar la máquina.

### Método 1: Script Automático (Más Fácil)

```bash
./test_persistencia_simple.sh
```

El script te guía paso a paso y verifica SQLite automáticamente.

### Método 2: Manual

#### Paso 1: Desactivar Workers

Edita `customizeme.cfg`:

```ini
huey_workers = 0  # ← Desactivar procesamiento
```

Reinicia:
```bash
# Ctrl+C
./bin/instance fg
```

#### Paso 2: Verificar SQLite Inicial

```bash
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**Esperado**: `0` o número bajo

#### Paso 3: Encolar Tareas (Sin Procesar)

Sube 5 PDFs desde el navegador:
```
http://localhost:11001/2/genwebupc/ca/documentacio/pdfs-test
```

Con `huey_workers = 0`, las tareas se **encolan** pero **NO se procesan**.

#### Paso 4: Verificar Tareas Encoladas

```bash
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**Esperado**: Número > 5 (cada tarea genera varios registros)

Ver claves:
```bash
sqlite3 var/huey/instance.db "SELECT key FROM kv LIMIT 10;"
```

#### Paso 5: Detener Instancia

```bash
Ctrl+C  # En terminal de la instancia
```

#### Paso 6: Verificar Persistencia (SIN Instancia Corriendo)

```bash
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**SIGUE mostrando el mismo número** ✅

También:
```bash
ls -lh var/huey/instance.db  # Archivo existe
du -h var/huey/instance.db   # Tiene tamaño
```

#### Paso 7: Reactivar Workers

Edita `customizeme.cfg`:

```ini
huey_workers = 2  # ← Reactivar procesamiento
```

#### Paso 8: Arrancar Instancia

```bash
./bin/instance fg
```

**Observar logs**:
```
INFO [huey] Worker-1 started
INFO [huey] Worker-2 started
INFO [huey] Executing clean_pdf_async: ...
INFO [ASYNC TASK START] Limpiando PDF: ...
INFO [ASYNC TASK SUCCESS] PDF limpiado: ...
```

**Las tareas se procesan automáticamente!** 🎉

#### Paso 9: Verificar Cola Vacía

```bash
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**Esperado**: `0` o número muy bajo (tareas procesadas)

### ✅ Criterios de Éxito

| Paso | SQLite Count | Instancia | Estado |
|------|--------------|-----------|---------|
| Inicial | 0-2 | Corriendo (workers=0) | Vacía |
| Tras subir 5 PDFs | 10-20 | Corriendo (workers=0) | Encoladas ✅ |
| Instancia detenida | 10-20 | **Apagada** | **Persisten** ✅ |
| Tras arrancar | 0-2 | Corriendo (workers=2) | Procesadas ✅ |

**Resultado**: collective.taskqueue2 sobrevive reinicios de máquina ✅

---

## 🚀 Test de Carga: Múltiples PDFs Simultáneos

### Objetivo

Verificar que el sistema maneja múltiples uploads simultáneos correctamente.

### Pasos

#### 1. Configurar Workers

```ini
# customizeme.cfg
huey_workers = 2
huey_log_level = INFO
```

#### 2. Arrancar Instancia

```bash
./bin/instance fg
```

#### 3. Subir 10 PDFs Rápidamente

Desde el navegador, subir 10 PDFs lo más rápido posible.

#### 4. Monitorear Logs

```bash
# Terminal 2
tail -f var/log/instance.log | grep -E "ASYNC|huey"
```

**Esperado**:
```
INFO [ASYNC MODE] Encolando limpieza PDF: ... (1)
INFO [ASYNC MODE] Encolando limpieza PDF: ... (2)
INFO [ASYNC MODE] Encolando limpieza PDF: ... (3)
...
INFO [huey] Executing clean_pdf_async: ... (Worker-1)
INFO [huey] Executing clean_pdf_async: ... (Worker-2)
INFO [ASYNC TASK SUCCESS] ... (Worker-1)
INFO [ASYNC TASK SUCCESS] ... (Worker-2)
```

**Los 2 workers procesan en paralelo** ✅

#### 5. Verificar Estado

```bash
# Mientras procesa
curl http://localhost:11001/2/genwebupc/@@taskqueue-stats
# Puede mostrar: {"pending": 3-8, "scheduled": 0}

# Después de procesar (esperar 10-20s)
curl http://localhost:11001/2/genwebupc/@@taskqueue-stats
# Debe mostrar: {"pending": 0, "scheduled": 0}
```

#### 6. Medir Tiempos

**Usuario**: Cada upload tarda <0.1s (respuesta inmediata)

**Sistema**: Logs muestran tiempo real de procesamiento (~0.3-0.5s cada uno)

### ✅ Criterios de Éxito

- [ ] 10 uploads responden todos <0.5s
- [ ] Workers procesan en paralelo (2 a la vez)
- [ ] Todas las tareas se completan
- [ ] Cola queda vacía
- [ ] Sin errores en logs

---

## 🧩 Test de Fallback: Modo Síncrono

### Objetivo

Verificar que si async falla, el sistema funciona en modo síncrono.

### Paso 1: Desactivar Async

```ini
# customizeme.cfg
async_pdf_enabled = 0  # ← Desactivar
```

Reinicia:
```bash
# Ctrl+C
./bin/instance fg
```

### Paso 2: Subir PDF

Sube un PDF.

### Paso 3: Verificar Logs

```bash
tail -20 var/log/instance.log | grep -E "SYNC|ASYNC"
```

**Esperado**:
```
INFO [genweb6.core.subscribers] PDF será procesado de forma síncrona
ERROR [GW6 METADADAS CHECK SIGNED] ... Tiempo: 0.001s
ERROR [GW6 METADADAS CLEAN PDF] ... Tiempo: 0.3s
INFO [genweb6.core.subscribers] [OK] ... - PDF sense metadades
```

**NO aparece** "ASYNC MODE" ni "huey Executing" ✅

### Paso 4: Observar Experiencia

El usuario **espera** los 0.3-0.5s completos (comportamiento anterior).

### ✅ Criterio de Éxito

- [ ] Sistema funciona en modo síncrono
- [ ] PDF se limpia correctamente
- [ ] Usuario espera todo el procesamiento
- [ ] Fácil cambiar de async a sync y viceversa

---

## 🔬 Test de Reintentos: Tareas que Fallan

### Objetivo

Verificar que Huey reintenta tareas que fallan (configurado con `retries=3`).

### Simular Fallo

**Opción A**: Configurar API inválida temporalmente

Edita en el panel de control:
```
http://localhost:11001/2/genwebupc/@@genwebmetadades-controlpanel
```

Cambia la URL a una inválida: `http://invalid-api.test/api/limpiar`

### Subir PDF

Sube un PDF.

### Verificar Reintentos en Logs

```bash
tail -50 var/log/instance.log | grep -E "huey.*retry|ASYNC.*EXCEPTION"
```

**Esperado**:
```
INFO [huey] Executing clean_pdf_async: ... 3 retries
ERROR [ASYNC TASK EXCEPTION] Error limpiando PDF: ...
INFO [huey] Re-enqueueing task (attempt 1 of 3)
# ...
INFO [huey] Re-enqueueing task (attempt 2 of 3)
# ...
INFO [huey] Re-enqueueing task (attempt 3 of 3)
# Tras 3 intentos, la tarea se marca como fallida
```

### Restaurar API Válida

Vuelve a configurar la URL correcta del API.

### ✅ Criterio de Éxito

- [ ] Tarea falla inicialmente
- [ ] Huey reintenta 3 veces
- [ ] Logs muestran los reintentos
- [ ] Tras restaurar API, siguiente PDF funciona

---

## 🏁 Test de Integración Completo

### Objetivo

Simular un día completo de operación.

### Escenario

1. Arrancar instancia
2. Subir 20 PDFs a lo largo de 30 minutos
3. Detener instancia (simular reinicio memon)
4. Arrancar instancia
5. Subir 10 PDFs más
6. Verificar que todo se procesó

### Comandos

```bash
# 1. Arrancar
./bin/instance fg

# 2. Subir PDFs (manual o con script)
# ... subir 20 PDFs ...

# 3. Verificar stats
curl http://localhost:11001/2/genwebupc/@@taskqueue-stats
# {"pending": 0, "scheduled": 0}

# 4. Ver SQLite
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
# Número bajo (solo metadata interna)

# 5. Detener (Ctrl+C)
# 6. Arrancar de nuevo
./bin/instance fg

# 7. Subir 10 PDFs más
# ...

# 8. Verificar todo procesado
curl http://localhost:11001/2/genwebupc/@@taskqueue-stats
# {"pending": 0, "scheduled": 0}
```

### ✅ Criterios de Éxito

- [ ] 30 PDFs procesados correctamente
- [ ] Todos con respuesta inmediata
- [ ] Reinicio no afecta procesamiento
- [ ] Cola siempre en 0 al final
- [ ] Sin errores en logs

---

## 🔍 Test de Persistencia Detallado

### Objetivo

Demostrar que las tareas **sobreviven reinicios de máquina**.

### Script Automático

```bash
cd /Users/pmarinas/Development/Plone/genweb6.buildout
./test_persistencia_simple.sh
```

### Manual: 9 Pasos Detallados

#### 1. Desactivar Workers

```ini
# customizeme.cfg
huey_workers = 0  # ← Tareas se encolan pero NO se procesan
```

Reinicia:
```bash
# Ctrl+C
./bin/instance fg
```

#### 2. Verificar SQLite Vacía

```bash
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**Esperado**: `0` o `1-2`

#### 3. Subir 5 PDFs

```
http://localhost:11001/2/genwebupc/ca/documentacio/pdfs-test
```

Con workers=0, tareas se **encolan** sin procesarse.

#### 4. Verificar Tareas Encoladas

```bash
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**Esperado**: `10-20` (cada PDF genera múltiples registros)

Ver detalles:
```bash
sqlite3 var/huey/instance.db "SELECT key FROM kv LIMIT 10;"
```

Verás claves tipo: `huey.result.abc123...`, `huey.task.def456...`

#### 5. Verificar Endpoint

```bash
curl http://localhost:11001/2/genwebupc/@@taskqueue-stats
```

**Esperado**:
```json
{"pending": 5, "scheduled": 0}
```

#### 6. Detener Instancia (Simular Reinicio)

```bash
Ctrl+C  # En terminal de la instancia
```

#### 7. Verificar Persistencia (Instancia Apagada)

```bash
# Verificar archivo existe
ls -lh var/huey/instance.db

# Verificar tareas persisten
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**SIGUE mostrando 10-20** ✅ (las tareas persisten en disco)

También:
```bash
du -h var/huey/instance.db
# Tamaño: ~20-50 KB
```

#### 8. Reactivar Workers

```ini
# customizeme.cfg
huey_workers = 2  # ← Reactivar procesamiento
```

#### 9. Arrancar y Observar

```bash
./bin/instance fg
```

**En los logs verás**:
```
INFO [huey] Worker-1 started
INFO [huey] Worker-2 started
INFO [huey] Executing clean_pdf_async: ... (1)
INFO [huey] Executing clean_pdf_async: ... (2)
INFO [ASYNC TASK SUCCESS] PDF limpiado: ... (1)
INFO [ASYNC TASK SUCCESS] PDF limpiado: ... (2)
...
INFO [ASYNC TASK SUCCESS] PDF limpiado: ... (5)
```

**Las 5 tareas se procesan automáticamente** 🎉

#### 10. Verificar Cola Vacía

```bash
curl http://localhost:11001/2/genwebupc/@@taskqueue-stats
```

**Esperado**:
```json
{"pending": 0, "scheduled": 0}
```

```bash
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**Esperado**: `0-2` (solo metadata interna de Huey)

### ✅ Criterios de Éxito

| Momento | SQLite | Instancia | Resultado |
|---------|--------|-----------|-----------|
| Inicial | 0-2 | Corriendo (workers=0) | Vacía |
| Tras subir 5 PDFs | 10-20 | Corriendo (workers=0) | ✅ Encoladas |
| Instancia detenida | 10-20 | **Apagada** | ✅ **Persisten** |
| Tras arrancar | 0-2 | Corriendo (workers=2) | ✅ **Procesadas** |

**Conclusión**: Las tareas sobreviven reinicios ✅

---

## 🐛 Debugging de Tests

### Test Falla: Tareas No se Encolan

**Verificar**:

```bash
./bin/instance debug
>>> import os
>>> os.environ.get('GENWEB_ASYNC_PDF_CLEANING')
'1'  # Debe ser '1'
>>> from genweb6.core.async_tasks import is_async_enabled
>>> is_async_enabled()
True  # Debe ser True
```

**Si es False**: Revisar `customizeme.cfg` y reiniciar instancia.

---

### Test Falla: Objeto No se Encuentra

**Error en logs**:
```
ERROR [ASYNC TASK ERROR] No se pudo obtener objeto. UID: ...
```

**Causa**: La tarea se encoló antes del commit.

**Solución**: Verificar que `subscribers.py` usa `addAfterCommitHook`:

```python
# Debe tener:
transaction.get().addAfterCommitHook(_schedule_after_commit)
```

---

### Test Falla: Workers No Arrancan

**Verificar logs**:
```bash
grep -i "worker.*start" var/log/instance.log
```

**Si no aparece**: Verificar `customizeme.cfg`:
```ini
huey_workers = 2  # NO puede ser 0
huey_consumer = 1  # Debe estar en 1
```

---

### Test Falla: Persistencia No Funciona

**Verificar**:

```bash
# Con instancia detenida
ls -lh var/huey/instance.db
# Debe existir

sqlite3 var/huey/instance.db ".tables"
# Debe mostrar: kv  schedule
```

**Si no existe**: Verificar permisos del directorio `var/huey/`.

---

## 📊 Métricas de Testing

### Tiempos Esperados

| Operación | Tiempo |
|-----------|--------|
| Usuario sube PDF (async) | <0.1s |
| Usuario sube PDF (sync) | 2-5s |
| Procesamiento background | 0.2-0.5s |
| Startup Huey consumer | 1-2s |
| Encolar tarea | <0.01s |

### Recursos Esperados

| Recurso | Sin Async | Con Async | Diferencia |
|---------|-----------|-----------|------------|
| RAM (por ZC) | 200MB | 250MB | +50MB |
| CPU (idle) | <1% | <1% | Sin cambio |
| CPU (procesando) | 5-10% | 5-10% | Sin cambio |
| Disco | - | +20-50MB | SQLite |

## ✅ Validación Final

Antes de desplegar en producción, verificar:

### Checklist de Validación Local

- [ ] Test básico: OK
- [ ] Test persistencia: OK
- [ ] Test carga (10 PDFs): OK
- [ ] Test fallback (mode sync): OK
- [ ] Sin errores en logs (excepto 404 API si no configurado)
- [ ] RAM estable (no crece indefinidamente)
- [ ] SQLite no crece >50MB
- [ ] `@@taskqueue-stats` siempre en 0 tras procesar

### Condiciones para Go to Production

✅ Todos los tests pasados  
✅ Sistema estable por >24h  
✅ Sin memory leaks observados  
✅ Experiencia de usuario mejorada  
✅ Documentación completa  

## 📞 Soporte

Si algún test falla:

1. **Revisar logs completos**: `var/log/instance.log`
2. **Verificar variables**: `grep HUEY customizeme.cfg`
3. **Verificar SQLite**: `sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"`
4. **Consultar troubleshooting**: `INSTALACION_ASYNC_PDF.md`

---

**Documentación relacionada**:
- [README_ASYNC_PDF.md](README_ASYNC_PDF.md) - Overview
- [INSTALACION_ASYNC_PDF.md](INSTALACION_ASYNC_PDF.md) - Instalación
- [CONFIGURACION_ASYNC_PDF.md](CONFIGURACION_ASYNC_PDF.md) - Configuración producción
