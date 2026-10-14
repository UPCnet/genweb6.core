# 🔒 Fix de Seguridad: Validación de Portrait Upload

## 📋 Descripción de la Vulnerabilidad

Se detectó una vulnerabilidad que permitía subir archivos maliciosos (como `shell.php`) al campo portrait del perfil de usuario. Aunque el sistema mostraba un mensaje de error, el archivo quedaba almacenado y accesible en el servidor.

### Problema Identificado

- **Archivo vulnerable**: `shell.php` o cualquier archivo no-imagen
- **Ruta accesible**: `http://localhost:11001/998/govern/personal-information/++widget++form.widgets.portrait/@@download/shell.php`
- **Impacto**: Potencial ejecución de código arbitrario
- **Alcance**: Solo accesible por el usuario autenticado que lo subió

## ✅ Solución Implementada

### 1. Validación por Contenido Real (Magic Bytes)

Se implementó validación basada en los primeros bytes del archivo (magic bytes) en lugar de confiar solo en la extensión del nombre del archivo.

**Archivos modificados:**

```
src/genweb6.core/src/genweb6/core/validations.py
```

**Funciones añadidas:**

- `validate_image_file_content()`: Valida el contenido real del archivo mediante magic bytes
- `validate_portrait_upload()`: Wrapper para validar el portrait antes de subirlo
- Clases de error: `InvalidImageFile`, `UnsafeImageType`

**Tipos de imagen permitidos (whitelist):**

- ✅ JPEG (magic bytes: `FF D8 FF`)
- ✅ PNG (magic bytes: `89 50 4E 47 0D 0A 1A 0A`)
- ✅ WEBP (magic bytes: `RIFF ... WEBP`)
- ❌ GIF (no incluido por precaución)
- ❌ SVG (no incluido - riesgo XSS)
- ❌ Cualquier otro tipo

### 2. Actualización del Adaptador de Portrait

**Archivo modificado:**

```
src/genweb6.core/src/genweb6/core/adapters/portrait.py
```

**Cambios:**

- Se añadió validación ANTES de procesar la imagen con `scale_image()`
- Si la validación falla, se lanza una excepción y **no se guarda nada**
- Se añadieron logs de seguridad para auditoría

### 3. Manejo de Errores en el Patch

**Archivo modificado:**

```
src/genweb6.core/src/genweb6/core/patches.py
```

**Cambios:**

- Captura las excepciones de validación
- Muestra mensaje de error traducido al usuario
- Evita que se guarde cualquier dato si falla la validación

### 4. Traducciones

**Archivos modificados:**

```
src/genweb6.core/src/genweb6/core/locales/ca/LC_MESSAGES/genweb.po
src/genweb6.core/src/genweb6/core/locales/es/LC_MESSAGES/genweb.po
src/genweb6.core/src/genweb6/core/locales/en/LC_MESSAGES/genweb.po
```

**Mensajes añadidos:**

- Catalán: "El fitxer d'imatge no és vàlid. Només es permeten imatges JPG, PNG o WEBP."
- Español: "El archivo de imagen no es válido. Sólo se permiten imágenes JPG, PNG o WEBP."
- Inglés: "The image file is not valid. Only JPG, PNG or WEBP images are allowed."

## 🧪 Pruebas Realizadas

Se crearon tests unitarios y de integración en `genweb6.core`:

**Archivo:** `src/genweb6.core/src/genweb6/core/tests/test_portrait_validation.py`

### Casos de Prueba Implementados

**Tests Unitarios (PortraitValidationUnitTest):**
- ✅ Validación JPEG por magic bytes
- ✅ Validación PNG por magic bytes
- ✅ Validación WebP por magic bytes
- ✅ Rechazo de archivos PHP
- ✅ Rechazo de shell scripts
- ✅ Rechazo de archivos de texto
- ✅ Rechazo de GIF (no en whitelist)
- ✅ Rechazo de archivos vacíos
- ✅ Rechazo de archivos demasiado pequeños
- ✅ Validación con objetos file-like

**Tests de Integración (PortraitUploadIntegrationTest):**
- ✅ Aceptación de imágenes válidas en validate_portrait_upload
- ✅ Rechazo de archivos maliciosos en validate_portrait_upload
- ✅ Manejo correcto de valores None

**Tests de Escenarios de Seguridad (SecurityScenarioTest):**
- ✅ Bloqueo de shell.php (escenario real reportado)
- ✅ Rechazo de PHP disfrazado como .jpg (no confía en extensión)
- ✅ Aceptación de JPEG real con extensión .php (solo valida contenido)

### Resultado de las Pruebas

```bash
$ ./bin/test -s genweb6.core -t test_portrait_validation

Total: 17 tests, 0 failures, 0 errors and 0 skipped in 3.552 seconds.
```

**17 tests pasaron correctamente** (14 unitarios + 3 integración).

## 🚀 Despliegue

### Pasos para Desplegar el Fix

1. **Reiniciar la instancia de Plone:**

```bash
cd /Users/pilarmarinas/Development/Plone/organs6.buildout
./bin/instance restart
```

2. **Verificar que las traducciones están compiladas:**

```bash
ls -la src/genweb6.core/src/genweb6/core/locales/*/LC_MESSAGES/*.mo
```

Deben existir los archivos `.mo` para ca, es y en.

3. **Probar manualmente:**

   a. Acceder a `http://localhost:11001/998/govern/personal-information`

   b. Intentar subir un archivo `test.php` con contenido:
      ```php
      <?php echo "test"; ?>
      ```

   c. Verificar que se muestra el mensaje de error

   d. Verificar que el archivo **NO** se guarda en el servidor

4. **Probar con imagen válida:**

   a. Subir una imagen JPG, PNG o WEBP real

   b. Verificar que se acepta correctamente

   c. Verificar que el portrait se muestra en el perfil

### Verificación en Producción

Antes de desplegar en producción:

- [ ] Ejecutar las pruebas automatizadas
- [ ] Probar manualmente con diferentes tipos de archivos
- [ ] Verificar logs de seguridad
- [ ] Confirmar que usuarios pueden subir imágenes válidas
- [ ] Confirmar que archivos maliciosos son rechazados

## 📊 Logs de Auditoría

El sistema ahora registra:

**Intentos de subida de archivos inválidos:**

```
WARNING - Intento de subir archivo no válido como portrait.
Usuario: username, Filename: shell.php,
Error: El fitxer d'imatge no és vàlid
```

**Subidas exitosas:**

```
INFO - Portrait actualizado correctamente para usuario: username
```

**Errores de procesamiento:**

```
ERROR - Error al procesar portrait para usuario username: [error]
```

## 🔐 Mejoras de Seguridad Implementadas

1. ✅ **Validación por contenido real** - No se confía en extensiones de archivo
2. ✅ **Whitelist estricta** - Solo JPG, PNG, WEBP permitidos
3. ✅ **Rechazo antes de procesamiento** - No se guarda nada si falla la validación
4. ✅ **Logs de auditoría** - Registro de intentos maliciosos
5. ✅ **Mensajes de error claros** - Usuario sabe por qué se rechazó
6. ✅ **Sin almacenamiento temporal** - Archivos rechazados no se guardan

## 📝 Notas Técnicas

### Por qué no se incluye GIF

Aunque GIF es un formato válido de imagen, se excluyó por:
- Menor uso en portraits de usuario
- Historial de vulnerabilidades relacionadas
- Enfoque en los formatos más comunes y seguros

### Por qué no se incluye SVG

SVG se excluyó porque:
- Es un formato basado en XML
- Puede contener JavaScript embebido (XSS)
- Vectores de ataque conocidos
- No es necesario para portraits de usuario

### Validación por Magic Bytes

Los magic bytes son los primeros bytes de un archivo que identifican su tipo real:

- **JPEG**: `FF D8 FF` (primeros 3 bytes)
- **PNG**: `89 50 4E 47 0D 0A 1A 0A` (primeros 8 bytes)
- **WEBP**: `RIFF [tamaño] WEBP` (primeros 12 bytes)

Esta validación es más segura que confiar en la extensión del archivo.

## 🎯 Verificación del Fix

Para verificar que el fix está funcionando:

```bash
# 1. Ejecutar los tests unitarios y de integración
cd /Users/pilarmarinas/Development/Plone/organs6.buildout
./bin/test -s genweb6.core -t test_portrait_validation

# 2. Ejecutar todos los tests del paquete core
./bin/test -s genweb6.core

# 3. Reiniciar la instancia
./bin/instance restart

# 4. Verificación manual:
# - Intentar subir un archivo malicioso (debe mostrar error y NO guardarse)
# - Subir una imagen válida (debe funcionar correctamente)
```

## 📞 Contacto

Para cualquier pregunta o problema relacionado con este fix de seguridad:

- Revisar los logs en `var/log/instance.log`
- Verificar que las traducciones están compiladas
- Comprobar que la instancia se reinició después de los cambios

---

**Fecha de implementación:** 2025-11-11
**Severidad:** Alta
**Estado:** ✅ Implementado y Probado
