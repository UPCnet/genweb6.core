# Instalación: Limpieza Asíncrona de PDFs

Guía completa de instalación de `collective.taskqueue2` para procesamiento asíncrono.

## 📋 Requisitos Previos

- Python 3.11+
- Plone 6.0+
- Git
- SQLite (incluido en Python)
- Acceso a GitHub (para descargar collective.taskqueue2)

## 🔧 Instalación

### Paso 1: Actualizar Código

```bash
cd /Dades/plone/genweb6.zope  # o tu ruta local
git pull origin master  # O la branch correspondiente
```

### Paso 2: Verificar Configuración

#### `sources.cfg` (ya incluido en el repo)

```ini
# collective.taskqueue2 desde GitHub (no está en PyPI)
collective.taskqueue2 = git https://github.com/collective/collective.taskqueue2.git branch=master
```

#### `genwebupc.cfg` (ya incluido en el repo)

```ini
[instance]
eggs +=
    collective.taskqueue2
    # ... otros eggs ...

developeggs +=
    collective.taskqueue2
    # ... otros develop eggs ...

environment-vars =
    # ... otras variables ...
    GENWEB_ASYNC_PDF_CLEANING ${custom:async_pdf_enabled}
    HUEY_CONSUMER ${custom:huey_consumer}
    HUEY_TASKQUEUE_URL ${custom:huey_taskqueue_url}
    HUEY_LOG_LEVEL ${custom:huey_log_level}
    HUEY_WORKERS ${custom:huey_workers}
```

### Paso 3: Ejecutar Buildout

```bash
./bootstrap.sh
```

**Duración**: 2-5 minutos (primera vez)

**Qué hace**:
- Descarga `collective.taskqueue2` desde GitHub
- Instala Huey y dependencias
- Configura eggs y environment vars

### Paso 4: Crear Directorio para Cola

```bash
mkdir -p var/huey
chown plone:plone var/huey  # Si es necesario
chmod 755 var/huey
```

## ✅ Verificación de Instalación

### 1. Verificar Código Descargado

```bash
ls -la src/collective.taskqueue2/
```

**Esperado**: Directorio existe con código fuente.

### 2. Verificar Huey Instalado

```bash
./bin/instance debug
>>> import huey
>>> huey.__version__
'2.5.0'  # O similar
>>> exit()
```

### 3. Verificar collective.taskqueue2

```bash
./bin/instance debug
>>> from collective.taskqueue2.huey_config import huey_taskqueue
>>> huey_taskqueue
<huey.api.SqliteHuey object at 0x...>
>>> exit()
```

### 4. Verificar Variables de Entorno

Añadir a `customizeme.cfg`:

```ini
[custom]
async_pdf_enabled = 1
huey_consumer = 1
huey_taskqueue_url = sqlite://${buildout:directory}/var/huey/instance.db
huey_log_level = DEBUG  # Para testing
huey_workers = 2
```

Arrancar instancia:

```bash
./bin/instance fg
```

**En los logs deberías ver**:

```
INFO [genweb6.core.async_tasks] collective.taskqueue2 disponible - Modo asíncrono habilitado
INFO [huey.consumer] Huey consumer started with 2 threads
INFO [huey.consumer] The following commands are available:
+ genweb6.core.async_tasks.clean_pdf_async
+ collective.taskqueue2.huey_tasks.dump_queue_stats
```

## 🐛 Troubleshooting

### Error: "Couldn't find index page for 'collective.taskqueue2'"

**Causa**: Buildout intenta buscar en PyPI, pero el paquete no está ahí.

**Solución**: Verificar que `sources.cfg` tiene:

```bash
grep collective.taskqueue2 sources.cfg
```

Debe mostrar:
```
collective.taskqueue2 = git https://github.com/collective/collective.taskqueue2.git branch=master
```

Si falta, añadirlo y ejecutar `./bootstrap.sh` de nuevo.

---

### Error: "No such file or directory: newrelic-admin"

**Causa**: El script intenta usar New Relic que no está instalado localmente.

**Solución (local)**: Usar instancia sin New Relic:

```bash
./bin/instance fg  # En lugar de ./bin/instance-newrelic fg
```

**En producción**: New Relic está configurado correctamente, no afecta.

---

### Error: "Permission denied" al crear var/huey/

**Causa**: Usuario no tiene permisos para crear directorios.

**Solución**:

```bash
sudo mkdir -p /Dades/plone/genweb6.zope/var/huey
sudo chown -R plone:plone /Dades/plone/genweb6.zope/var/huey
```

---

### collective.taskqueue2 no se descarga

**Verificar conexión a GitHub**:

```bash
git ls-remote https://github.com/collective/collective.taskqueue2.git
```

**Si falla**: Problema de red/firewall bloqueando GitHub.

**Solución temporal**: Descargar manualmente:

```bash
cd src/
git clone https://github.com/collective/collective.taskqueue2.git
cd ../
./bootstrap.sh
```

---

### Logs muestran "collective.taskqueue2 NO disponible"

**Verificar instalación**:

```bash
./bin/instance debug
>>> import collective.taskqueue2
>>> # Si da ImportError, no está instalado
```

**Solución**: Repetir instalación:

```bash
./bootstrap.sh
grep collective.taskqueue2 genwebupc.cfg  # Verificar que está en eggs
```

---

### Base de datos SQLite no se crea

**Verificar ruta**:

```bash
echo "sqlite://${PWD}/var/huey/instance.db"
```

**Verificar permisos**:

```bash
ls -ld var/huey/
# Debe ser escribible por el usuario que corre Plone
```

**Crear manualmente**:

```bash
touch var/huey/instance.db
chmod 644 var/huey/instance.db
```

---

### Workers no arrancan

**Verificar en logs**:

```bash
grep -i "huey.*worker" var/log/instance.log
```

**Esperado**:
```
INFO [huey] Worker-1 started
INFO [huey] Worker-2 started
```

**Si no aparece**: Verificar `customizeme.cfg`:

```ini
huey_workers = 2  # Debe ser > 0
huey_consumer = 1  # Debe estar en 1
```

---

### Error: "Unable to find binary pdftotext"

**Esto es NORMAL** - Es un warning de Plone intentando indexar PDFs para búsqueda.

**NO afecta** la limpieza de metadatos, que usa un API externo.

Puedes ignorar este mensaje o instalar poppler-utils:

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# CentOS/RHEL
sudo yum install poppler-utils
```

## 📦 Instalación por Tipo de Entorno

### Desarrollo Local

```bash
# 1. Clonar/actualizar repo
git pull

# 2. Bootstrap
./bootstrap.sh

# 3. Configurar (customizeme.cfg)
async_pdf_enabled = 1
huey_workers = 2
huey_log_level = DEBUG  # Ver todos los logs

# 4. Crear directorio
mkdir -p var/huey

# 5. Arrancar
./bin/instance fg
```

### Pre-producción

Igual que desarrollo pero:

```ini
huey_log_level = INFO  # Menos verbose
```

### Producción (20 máquinas)

```bash
# Por cada máquina:

# 1. Actualizar código
cd /Dades/plone/genweb6.zope
git pull

# 2. Bootstrap
./bootstrap.sh

# 3. Editar customizeme.cfg (ver CONFIGURACION_ASYNC_PDF.md)

# 4. Crear directorio
mkdir -p var/huey
chown plone:plone var/huey

# 5. Reiniciar
supervisorctl restart zc1 zc2 zc3 zc4

# 6. Verificar
tail -f var/log/zc1.log | grep -i huey
```

Ver plan de deployment gradual en `CONFIGURACION_ASYNC_PDF.md`.

## 🔍 Verificación Post-Instalación

### Checklist

- [ ] `src/collective.taskqueue2/` existe
- [ ] `var/huey/` existe con permisos correctos
- [ ] `customizeme.cfg` tiene variables configuradas
- [ ] Al arrancar, logs muestran "Huey consumer started"
- [ ] Al arrancar, logs muestran "clean_pdf_async" disponible
- [ ] Al subir PDF, respuesta inmediata (<0.1s)
- [ ] En logs, aparece "[ASYNC MODE] Encolando"
- [ ] `@@taskqueue-stats` responde con `{"pending": 0, "scheduled": 0}`

### Test Básico

```bash
# 1. Arrancar instancia
./bin/instance fg

# 2. En navegador, subir PDF
http://localhost:11001/2/genwebupc/folder

# 3. Verificar logs inmediatamente
tail -20 var/log/instance.log | grep -E "ASYNC|huey"
```

**Esperado**:
```
INFO [ASYNC] Programado para encolar después del commit
INFO [ASYNC MODE] Encolando limpieza PDF: ...
INFO [huey] Executing clean_pdf_async: ...
INFO [ASYNC TASK START] Limpiando PDF: ...
INFO [ASYNC TASK SUCCESS] PDF limpiado: ...
```

## ➡️ Siguiente Paso

Una vez verificada la instalación, configurar producción siguiendo:

**[CONFIGURACION_ASYNC_PDF.md](CONFIGURACION_ASYNC_PDF.md)**

## 📞 Soporte

Si persisten problemas tras seguir este troubleshooting:

1. Revisar logs completos: `var/log/zc*.log`
2. Verificar versiones: `./bin/instance debug` y hacer imports
3. Consultar documentación collective.taskqueue2: https://github.com/collective/collective.taskqueue2
