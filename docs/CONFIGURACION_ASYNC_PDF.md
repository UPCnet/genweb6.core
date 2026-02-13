# Configuración: Limpieza Asíncrona de PDFs

Guía completa de configuración de variables de entorno y deployment en producción.

## 📁 Estructura de Configuración

```
/Dades/plone/genweb6.zope/
├── genwebupc.cfg          # Común a todas las máquinas (Git)
├── customizeme.cfg        # Específico por máquina (NO en Git)
└── sources.cfg            # Común (Git)
```

**Filosofía**:
- `genwebupc.cfg`: Define REFERENCIAS a variables
- `customizeme.cfg`: Define VALORES de variables (por máquina)

## 🎛️ Variables de Configuración

### customizeme.cfg (Específico por Máquina)

```ini
[ldapconfig]
bindpasswd = [PASSWORD_MAQUINA]

[deployment]
varnish_url = [VARNISH_URL]
dorsal = [DORSAL]
varnish_to_ban = [VARNISH_TO_BAN]

[custom]
# Mount points activos en esta máquina
parts = 2 3 4 5 6 7 8 9 10  # Según los sitios Plone

home_user = [HOME_USER]
home_pass = [HOME_PASS]
home_url = [HOME_URL]
metadades_servei_apikey = [API_KEY]
metadades_indicadors_apikey = [API_KEY]

# ============================================================
# Configuración collective.taskqueue2 - Limpieza Asíncrona PDFs
# ============================================================
async_pdf_enabled = 1
huey_consumer = 1
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
huey_log_level = WARNING
huey_workers = 2

[newrelic]
license_key = [NEW_RELIC_KEY]
app_name = [APP_NAME]
monitor_mode = true
environment = [ENVIRONMENT]
```

### genwebupc.cfg (Común a Todas las Máquinas)

```ini
[instance]
environment-vars =
  # ... otras variables existentes ...
  GENWEB_ASYNC_PDF_CLEANING ${custom:async_pdf_enabled}
  HUEY_CONSUMER ${custom:huey_consumer}
  HUEY_TASKQUEUE_URL ${custom:huey_taskqueue_url}
  HUEY_LOG_LEVEL ${custom:huey_log_level}
  HUEY_WORKERS ${custom:huey_workers}
```

## 📊 Variables Explicadas

### async_pdf_enabled

**Valores**: `0` (desactivado) o `1` (activado)

**Propósito**: Activa/desactiva el modo asíncrono.

```ini
# Activar asíncrono (recomendado)
async_pdf_enabled = 1

# Desactivar (vuelve a comportamiento síncrono)
async_pdf_enabled = 0
```

**Cuándo cambiar a 0**:
- Debugging de problemas específicos
- Rollback temporal en caso de issues
- Máquinas con muy pocos uploads (<10 PDFs/día)

---

### huey_consumer

**Valores**: `0` o `1`

**Propósito**: Activa el consumer de Huey (siempre debe ser `1` si `async_pdf_enabled = 1`).

```ini
huey_consumer = 1  # Siempre 1 en producción
```

---

### huey_taskqueue_url

**Formato**: `sqlite://[ruta]/archivo.db`

**Opciones**:

#### Relativa al buildout (recomendado):
```ini
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
```

Se expande a: `/Dades/plone/genweb6.zope/var/huey/instance.db`

#### Absoluta:
```ini
huey_taskqueue_url = sqlite:////var/huey/genweb6_maquina01.db
```

**Recomendación**: Usar ruta relativa. Todos los mount points y ZEO clients de la máquina comparten la misma cola (eficiente).

---

### huey_log_level

**Valores**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

**Por entorno**:

```ini
# Desarrollo
huey_log_level = DEBUG    # Ver todo

# Pre-producción
huey_log_level = INFO     # Info importante

# Producción
huey_log_level = WARNING  # Solo warnings y errores
```

---

### huey_workers

**Valores**: Número de threads para procesar cola (recomendado: `2`)

**Impacto**:

| Workers/ZC | Workers/Máquina | RAM Extra | PDFs/min | Recomendado |
|------------|-----------------|-----------|----------|-------------|
| 1 | 4 | +25MB | 12-15 | Carga muy baja |
| **2** | **8** | **+100MB** | **20-25** | **✅ Estándar** |
| 3 | 12 | +150MB | 25-30 | Carga alta + RAM disponible |
| 4 | 16 | +300MB | 30-35 | ⚠️ Solo si >2GB RAM libre |

**Recomendación**: `huey_workers = 2` para la mayoría de máquinas.

## 🚀 Deployment en Producción

### Configuración por Tipo de Máquina

#### Máquinas Estándar (mayoría)

```ini
# customizeme.cfg
async_pdf_enabled = 1
huey_workers = 2
huey_log_level = WARNING
```

#### Máquinas con Alta Carga (>200 PDFs/día)

```ini
# customizeme.cfg
async_pdf_enabled = 1
huey_workers = 3  # Solo si hay RAM disponible
huey_log_level = WARNING
```

#### Máquinas de Desarrollo

```ini
# customizeme.cfg
async_pdf_enabled = 1
huey_workers = 2
huey_log_level = DEBUG  # Ver todos los detalles
```

### Plan de Rollout Gradual (Recomendado)

#### Fase 1: Testing (Semana 1)
- **Máquinas**: 1 de pre-producción
- **Objetivo**: Validar funcionamiento
- **Monitoreo**: Intensivo (logs, RAM, usuarios)

#### Fase 2: Pre-producción (Semana 2)
- **Máquinas**: +2-3 pre-producción
- **Objetivo**: Validar estabilidad
- **Monitoreo**: RAM, frecuencia reinicios memon

#### Fase 3: Producción Parcial (Semana 3-4)
- **Máquinas**: 10 de las 20
- **Objetivo**: Comparar con las 10 sin activar
- **Monitoreo**: Experiencia usuario, métricas

#### Fase 4: Producción Completa (Semana 5)
- **Máquinas**: Las 20 restantes
- **Objetivo**: Rollout completo
- **Monitoreo**: Continuo primeros días

## 📋 Checklist de Deployment por Máquina

### Antes de Deployment

- [ ] Backup de `customizeme.cfg` actual
- [ ] Verificar RAM disponible: `free -h` (>1GB recomendado)
- [ ] Verificar acceso SSH a la máquina
- [ ] Ventana de mantenimiento coordinada (opcional)

### Durante Deployment

- [ ] `git pull` (actualizar código)
- [ ] `./bootstrap.sh` (instalar dependencias)
- [ ] Editar `customizeme.cfg` (añadir variables taskqueue2)
- [ ] `mkdir -p var/huey` (crear directorio)
- [ ] `chown plone:plone var/huey` (permisos)
- [ ] `supervisorctl restart zc1 zc2 zc3 zc4` (reiniciar)

### Post-Deployment

- [ ] Verificar logs startup: `grep -i huey var/log/zc1.log`
- [ ] Verificar Huey consumer: "started with 2 threads"
- [ ] Subir PDF de prueba
- [ ] Verificar respuesta inmediata (<0.1s)
- [ ] Verificar logs procesamiento: "[ASYNC TASK SUCCESS]"
- [ ] Monitorear RAM: `free -h` (primeras 24h)
- [ ] Verificar `@@taskqueue-stats`: `{"pending": 0}`

## 🔧 Script de Deployment Automático

```bash
#!/bin/bash
# deploy_async_pdf.sh - Ejecutar en cada máquina

BUILDOUT_DIR="/Dades/plone/genweb6.zope"
HUEY_DIR="$BUILDOUT_DIR/var/huey"

echo "Desplegando limpieza asíncrona de PDFs..."

# 1. Backup configuración
cp "$BUILDOUT_DIR/customizeme.cfg" "$BUILDOUT_DIR/customizeme.cfg.backup.$(date +%Y%m%d)"

# 2. Crear directorio huey
if [ ! -d "$HUEY_DIR" ]; then
    mkdir -p "$HUEY_DIR"
    chown plone:plone "$HUEY_DIR"
    chmod 755 "$HUEY_DIR"
    echo "✅ Directorio $HUEY_DIR creado"
else
    echo "✅ Directorio $HUEY_DIR ya existe"
fi

# 3. Verificar customizeme.cfg
if grep -q "async_pdf_enabled" "$BUILDOUT_DIR/customizeme.cfg"; then
    echo "✅ customizeme.cfg ya tiene configuración taskqueue2"
else
    echo "⚠️  ADVERTENCIA: customizeme.cfg NO tiene configuración taskqueue2"
    echo "   Añade manualmente las variables (ver CONFIGURACION_ASYNC_PDF.md)"
    exit 1
fi

# 4. Ejecutar buildout
echo "Ejecutando bootstrap..."
cd "$BUILDOUT_DIR"
./bootstrap.sh

if [ $? -eq 0 ]; then
    echo "✅ Bootstrap completado"
else
    echo "❌ Error en bootstrap"
    exit 1
fi

# 5. Verificar instalación
if [ -d "$BUILDOUT_DIR/src/collective.taskqueue2" ]; then
    echo "✅ collective.taskqueue2 instalado"
else
    echo "❌ collective.taskqueue2 NO instalado"
    exit 1
fi

# 6. Reiniciar instancias
echo "Reiniciando instancias..."
supervisorctl restart zc1 zc2 zc3 zc4

echo ""
echo "=================================================="
echo "✅ Deployment completado"
echo "=================================================="
echo ""
echo "Verificar logs:"
echo "tail -f $BUILDOUT_DIR/var/log/zc1.log | grep -i huey"
echo ""
echo "Verificar estado:"
echo "curl http://localhost/2/@@taskqueue-stats"
```

## 📊 Monitoreo Post-Deployment

### Logs a Monitorear

```bash
# En cada máquina
tail -f /Dades/plone/genweb6.zope/var/log/zc*.log | grep -E "ASYNC|HUEY|collective.taskqueue2"
```

**Buscar**:
- `[ASYNC MODE] Encolando limpieza PDF` - PDFs encolándose ✅
- `[ASYNC TASK START]` - Tareas ejecutándose ✅
- `[ASYNC TASK SUCCESS]` - Tareas completadas ✅
- `[ASYNC TASK ERROR]` - Errores a investigar ⚠️

### Estado de Cola

```bash
curl http://[MAQUINA]/2/@@taskqueue-stats
```

**Valores normales**:
```json
{"pending": 0-5, "scheduled": 0}
```

**Valores problemáticos**:
```json
{"pending": 50, "scheduled": 0}  // Cola creciendo → Aumentar workers
```

### Uso de RAM

```bash
# Antes de activar async
free -h

# Después de activar async (esperar 1 hora)
free -h
```

**Esperado**: +100-150MB menos disponible por máquina.

**Preocupante**: Si baja a <500MB disponibles → Riesgo de más reinicios memon.

### Tamaño Base de Datos SQLite

```bash
du -h /Dades/plone/genweb6.zope/var/huey/instance.db
```

**Tamaños normales**:
- Carga baja: 5-20MB
- Carga media: 20-50MB
- Carga alta: 50-100MB

**Si crece >200MB**: Investigar si hay tareas acumulándose o fallando.

## 🔄 Rollback

### Opción 1: Desactivar Temporalmente (Sin Rebuild)

Más rápido, vuelve a comportamiento síncrono:

```ini
# customizeme.cfg
async_pdf_enabled = 0  # ← Cambiar de 1 a 0
```

```bash
supervisorctl restart zc1 zc2 zc3 zc4
```

El sistema vuelve a modo síncrono inmediatamente.

### Opción 2: Desactivar Completamente

```ini
# customizeme.cfg - Comentar todo
# async_pdf_enabled = 1
# huey_consumer = 1
# huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
# huey_log_level = WARNING
# huey_workers = 2
```

```bash
./bootstrap.sh
supervisorctl restart zc1 zc2 zc3 zc4
```

## 📝 Template por Entorno

### Desarrollo Local

```ini
[custom]
parts = 2 3  # Solo algunos mount points

# Limpieza asíncrona PDFs
async_pdf_enabled = 1
huey_consumer = 1
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
huey_log_level = DEBUG  # Ver todos los detalles
huey_workers = 2
```

### Pre-producción

```ini
[custom]
parts = 2 3 4 5 6

async_pdf_enabled = 1
huey_consumer = 1
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
huey_log_level = INFO  # Menos verbose
huey_workers = 2
```

### Producción - Máquina Estándar

```ini
[custom]
parts = 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26

async_pdf_enabled = 1
huey_consumer = 1
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
huey_log_level = WARNING  # Solo warnings y errores
huey_workers = 2
```

### Producción - Máquina con Alta Carga

Si identificas máquinas con >200 PDFs/día:

```ini
async_pdf_enabled = 1
huey_workers = 3  # Más workers
huey_log_level = WARNING
```

**IMPORTANTE**: Solo aumentar workers si hay >2GB RAM disponibles.

## 🌍 Deployment Multi-Máquina

### Por Cada Máquina (20 total)

#### 1. Actualizar Código

```bash
cd /Dades/plone/genweb6.zope
git pull
```

#### 2. Backup Configuración

```bash
cp customizeme.cfg customizeme.cfg.backup.$(date +%Y%m%d)
```

#### 3. Editar customizeme.cfg

Añadir sección taskqueue2 (ver templates arriba).

#### 4. Crear Directorio

```bash
mkdir -p var/huey
chown plone:plone var/huey
```

#### 5. Ejecutar Buildout

```bash
./bootstrap.sh
```

#### 6. Reiniciar

```bash
supervisorctl restart zc1 zc2 zc3 zc4
```

#### 7. Verificar

```bash
# Logs
tail -50 var/log/zc1.log | grep -i huey

# Esperado:
# INFO [huey.consumer] Huey consumer started with 2 threads
```

## 🔍 Configuración por Caso de Uso

### Compartir Cola entre Todos los ZEO Clients (Recomendado)

**Configuración actual** ✅

```ini
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
```

**Resultado**:
- zc1, zc2, zc3, zc4 usan misma base de datos
- 8 workers (2×4) procesando misma cola
- Balanceo automático
- Eficiente

### Colas Separadas por ZEO Client (NO Recomendado)

Solo si necesitas aislamiento total:

```ini
# Configuración diferente por cada ZC (complejo)
# NO USAR excepto casos muy específicos
```

**Problemas**:
- Sin balanceo entre ZCs
- Más archivos que gestionar
- Mayor complejidad

## 📈 Monitoreo Continuo

### Endpoint de Estado

```bash
curl http://[MAQUINA]/[MOUNT]/@@taskqueue-stats
```

**Respuesta esperada**:
```json
{
  "pending": 0,      // Tareas esperando
  "scheduled": 0     // Tareas programadas
}
```

**Alertas recomendadas**:
- Si `pending > 20` por más de 5 minutos → Investigar
- Si `pending > 50` por más de 10 minutos → Considerar aumentar workers

### Logs de Huey

```bash
# Ver actividad de Huey
tail -100 var/log/zc1.log | grep -E "huey|ASYNC"
```

**Logs saludables**:
```
INFO [ASYNC MODE] Encolando limpieza PDF: ...
INFO [ASYNC TASK START] Limpiando PDF: ...
INFO [ASYNC TASK SUCCESS] PDF limpiado: ...
```

**Logs problemáticos**:
```
ERROR [ASYNC TASK ERROR] No se pudo obtener objeto...
ERROR [ASYNC TASK EXCEPTION] Error limpiando PDF...
```

### Base de Datos SQLite

```bash
# Tamaño
du -h var/huey/instance.db

# Registros
sqlite3 var/huey/instance.db "SELECT COUNT(*) FROM kv;"
```

**Limpieza manual** (si crece >200MB):

```bash
supervisorctl stop zc1 zc2 zc3 zc4
rm var/huey/instance.db  # Se recreará
supervisorctl start zc1 zc2 zc3 zc4
```

## 🎯 Optimización por Máquina

### Identificar Carga por Máquina

```bash
# Ver cuántos PDFs se suben por día en una máquina
grep "ASYNC MODE.*Encolando" var/log/zc*.log | wc -l
```

### Ajustar Workers Según Carga

**<50 PDFs/día**:
```ini
huey_workers = 2  # Suficiente
```

**50-200 PDFs/día**:
```ini
huey_workers = 2  # OK
# Monitorear que pending no suba
```

**>200 PDFs/día**:
```ini
huey_workers = 3  # Solo si RAM disponible
```

### Máquinas con Baja RAM (<1GB disponible)

Si la máquina tiene poca RAM disponible:

**Opción 1**: Mantener async con workers mínimos
```ini
async_pdf_enabled = 1
huey_workers = 1  # Menos RAM
```

**Opción 2**: Desactivar async en esa máquina
```ini
async_pdf_enabled = 0
# (comentar resto de variables)
```

## 🚨 Alertas y Métricas

### Script de Monitoreo

```bash
#!/bin/bash
# monitor_taskqueue.sh

MACHINES=(
    "genweb-01.upc.edu"
    "genweb-02.upc.edu"
    # ... las 20 máquinas
)

for machine in "${MACHINES[@]}"; do
    stats=$(curl -s "http://$machine/2/@@taskqueue-stats" 2>/dev/null)
    pending=$(echo "$stats" | jq -r '.pending' 2>/dev/null)
    
    if [ "$pending" -gt 20 ]; then
        echo "⚠️  ALERTA: $machine tiene $pending tareas pendientes"
    else
        echo "✅ $machine: $pending tareas pendientes"
    fi
done
```

### Nagios/Prometheus

**Métricas a exportar**:
- `taskqueue_pending_tasks`: Número de tareas pendientes
- `taskqueue_failed_tasks`: Tareas que fallaron
- `taskqueue_avg_processing_time`: Tiempo promedio de procesamiento

## 🔄 Mantenimiento

### Limpieza Periódica (Opcional)

Si la base de datos SQLite crece mucho:

```bash
# Cronjob mensual (ejecutar cuando NO hay carga)
0 3 1 * * cd /Dades/plone/genweb6.zope && supervisorctl stop zc1 zc2 zc3 zc4 && rm -f var/huey/instance.db && supervisorctl start zc1 zc2 zc3 zc4
```

**NO necesario** si la cola se procesa correctamente.

### Actualización de Código

```bash
# 1. Actualizar
git pull
./bootstrap.sh

# 2. Reiniciar
supervisorctl restart zc1 zc2 zc3 zc4

# 3. Verificar
tail -f var/log/zc1.log | grep -i huey
```

Las tareas en cola se procesarán con el código nuevo ✅

## 💡 Tips de Configuración

### Desarrollo: Logs Verbosos

```ini
huey_log_level = DEBUG
```

Ver cada operación en detalle.

### Producción: Logs Mínimos

```ini
huey_log_level = WARNING
```

Solo errores y warnings (menos ruido en logs).

### Testing: Sin Procesamiento

```ini
huey_workers = 0  # Encola pero no procesa
```

Útil para testing de encolamiento sin ejecutar tareas.

## 🎓 Casos de Uso Avanzados

### Priorizar una Máquina Específica

Si una máquina es crítica:

```ini
huey_workers = 3  # Más workers
huey_log_level = INFO  # Más visibilidad
```

### Máquina de Testing Continuo

```ini
async_pdf_enabled = 1
huey_log_level = DEBUG
huey_workers = 2
# Mantener siempre para testing antes de producción
```

### Desactivación Temporal para Mantenimiento

```bash
# 1. Desactivar async
echo "async_pdf_enabled = 0" >> customizeme.cfg

# 2. Reiniciar
supervisorctl restart zc1 zc2 zc3 zc4

# 3. Hacer mantenimiento
# ...

# 4. Reactivar
echo "async_pdf_enabled = 1" >> customizeme.cfg
supervisorctl restart zc1 zc2 zc3 zc4
```

## 📞 Soporte

Para problemas de configuración:
1. Verificar `customizeme.cfg` tiene todas las variables
2. Verificar logs de startup: `grep -i huey var/log/zc1.log`
3. Verificar estado: `@@taskqueue-stats`
4. Revisar troubleshooting en `INSTALACION_ASYNC_PDF.md`

---

**Documentación relacionada**:
- [README_ASYNC_PDF.md](README_ASYNC_PDF.md) - Overview
- [INSTALACION_ASYNC_PDF.md](INSTALACION_ASYNC_PDF.md) - Instalación
- [TESTING_ASYNC_PDF.md](TESTING_ASYNC_PDF.md) - Pruebas y validación
