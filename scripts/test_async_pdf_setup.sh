#!/bin/bash
# Script unificado para testing y setup de limpieza asíncrona de PDFs
# Fusiona: test_async_pdf.sh + test_persistencia_cola.sh + test_persistencia_simple.sh

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILDOUT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HUEY_DB="$BUILDOUT_DIR/var/huey/instance.db"

# Detectar puerto (leer de configuración o usar default)
PLONE_PORT="11001"

echo ""
echo "========================================"
echo "  Test Limpieza Asíncrona de PDFs"
echo "========================================"
echo ""
echo "Buildout: $BUILDOUT_DIR"
echo "Huey DB: $HUEY_DB"
echo "Puerto: $PLONE_PORT"
echo ""

# Función para contar tareas en SQLite
count_tasks() {
    if [ -f "$HUEY_DB" ]; then
        count=$(sqlite3 "$HUEY_DB" "SELECT COUNT(*) FROM kv;" 2>/dev/null || echo "0")
        echo -e "${YELLOW}Registros en SQLite: $count${NC}"
    else
        echo -e "${RED}Base de datos NO existe: $HUEY_DB${NC}"
    fi
}

# Menú principal
echo -e "${BLUE}Selecciona el tipo de test:${NC}"
echo ""
echo "1) Test Básico - Verificar funcionamiento asíncrono"
echo "2) Test Persistencia - Verificar que tareas sobreviven reinicio"
echo "3) Setup Completo - Instalar y configurar desde cero"
echo "4) Verificar Estado Actual - Ver estado de cola y SQLite"
echo "5) Salir"
echo ""
read -p "Opción (1-5): " opcion

case $opcion in
    1)
        echo ""
        echo "========================================"
        echo "  TEST BÁSICO: Funcionamiento Asíncrono"
        echo "========================================"
        echo ""
        
        echo "1️⃣  Verificar instancia corriendo"
        if ! curl -s "http://localhost:${PLONE_PORT}" >/dev/null 2>&1; then
            echo -e "${RED}❌ Instancia NO está corriendo en puerto ${PLONE_PORT}${NC}"
            echo "Arranca con: ./bin/instance fg"
            exit 1
        fi
        echo -e "${GREEN}✅ Instancia corriendo${NC}"
        echo ""
        
        echo "2️⃣  Verificar configuración"
        if ! grep -q "async_pdf_enabled = 1" "$BUILDOUT_DIR/customizeme.cfg" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  async_pdf_enabled NO está en 1${NC}"
            echo "Edita customizeme.cfg y configura: async_pdf_enabled = 1"
        else
            echo -e "${GREEN}✅ async_pdf_enabled = 1${NC}"
        fi
        echo ""
        
        echo "3️⃣  Estado actual de la cola"
        count_tasks
        echo ""
        
        echo -e "${BLUE}📝 AHORA:${NC}"
        echo "1. Sube un PDF en: http://localhost:${PLONE_PORT}/2/genwebupc/ca/documentacio/pdfs-test"
        echo "2. Observa que la respuesta es INMEDIATA (<0.1s)"
        echo "3. Revisa los logs: tail -30 var/log/instance.log | grep ASYNC"
        echo ""
        echo "Deberías ver:"
        echo "  INFO [ASYNC MODE] Encolando limpieza PDF: ..."
        echo "  INFO [huey] Executing clean_pdf_async: ..."
        echo "  INFO [ASYNC TASK SUCCESS] PDF limpiado: ..."
        ;;
        
    2)
        echo ""
        echo "========================================"
        echo "  TEST PERSISTENCIA: Reinicios"
        echo "========================================"
        echo ""
        
        echo "Este test verifica que las tareas sobreviven reinicios."
        echo ""
        echo "PASO 1: Desactivar workers"
        echo "=========================="
        echo "Edita customizeme.cfg:"
        echo "  huey_workers = 0  # Cambiar de 2 a 0"
        echo ""
        read -p "¿Ya cambiaste huey_workers a 0? (s/n): " resp
        if [ "$resp" != "s" ]; then
            echo "Edita customizeme.cfg y vuelve a ejecutar este script"
            exit 0
        fi
        
        echo ""
        echo "PASO 2: Reiniciar instancia"
        echo "==========================="
        echo "Ctrl+C en la terminal + ./bin/instance fg"
        read -p "¿Instancia reiniciada con workers=0? (s/n): " resp
        if [ "$resp" != "s" ]; then
            exit 0
        fi
        
        echo ""
        echo "PASO 3: Estado inicial"
        echo "======================"
        count_tasks
        
        echo ""
        echo "PASO 4: Subir PDFs"
        echo "=================="
        echo "Sube 5 PDFs en: http://localhost:${PLONE_PORT}/2/genwebupc/ca/documentacio/pdfs-test"
        read -p "¿Has subido 5 PDFs? (s/n): " resp
        if [ "$resp" != "s" ]; then
            exit 0
        fi
        
        echo ""
        echo "PASO 5: Verificar encoladas"
        echo "============================"
        count_tasks
        echo ""
        curl -s "http://localhost:${PLONE_PORT}/2/genwebupc/@@taskqueue-stats" 2>/dev/null || echo "Requiere login"
        echo ""
        read -p "¿Ves registros > 5 en SQLite? (s/n): " resp
        if [ "$resp" != "s" ]; then
            echo -e "${RED}Si no hay tareas, verifica que workers=0${NC}"
            exit 1
        fi
        
        echo ""
        echo "PASO 6: Detener instancia"
        echo "========================="
        echo "Ctrl+C en la terminal de la instancia"
        read -p "¿Instancia detenida? (s/n): " resp
        if [ "$resp" != "s" ]; then
            exit 0
        fi
        
        echo ""
        echo "PASO 7: Verificar persistencia (SIN instancia)"
        echo "==============================================="
        count_tasks
        echo ""
        if [ -f "$HUEY_DB" ]; then
            size=$(du -h "$HUEY_DB" | cut -f1)
            echo -e "${GREEN}✅ Base de datos existe: $size${NC}"
        else
            echo -e "${RED}❌ Base de datos NO existe${NC}"
            exit 1
        fi
        
        echo ""
        echo "PASO 8: Reactivar workers"
        echo "========================="
        echo "Edita customizeme.cfg:"
        echo "  huey_workers = 2  # Cambiar de 0 a 2"
        read -p "¿Ya cambiaste huey_workers a 2? (s/n): " resp
        if [ "$resp" != "s" ]; then
            exit 0
        fi
        
        echo ""
        echo "PASO 9: Arrancar instancia"
        echo "=========================="
        echo "./bin/instance fg"
        read -p "¿Instancia arrancada? (s/n): " resp
        if [ "$resp" != "s" ]; then
            exit 0
        fi
        
        echo ""
        echo "PASO 10: Esperar procesamiento"
        echo "==============================="
        echo "Esperando 15 segundos..."
        sleep 15
        
        echo ""
        echo "PASO 11: Verificar cola procesada"
        echo "=================================="
        count_tasks
        echo ""
        curl -s "http://localhost:${PLONE_PORT}/2/genwebupc/@@taskqueue-stats" 2>/dev/null || echo "Requiere login"
        
        echo ""
        echo "========================================"
        echo "✅ TEST COMPLETADO"
        echo "========================================"
        echo ""
        echo "Si SQLite muestra 0-2 registros, el test es EXITOSO ✅"
        echo "Esto demuestra que collective.taskqueue2 sobrevive reinicios"
        ;;
        
    3)
        echo ""
        echo "========================================"
        echo "  SETUP COMPLETO"
        echo "========================================"
        echo ""
        
        cd "$BUILDOUT_DIR"
        
        echo "1️⃣  Verificar sources.cfg"
        if grep -q "collective.taskqueue2" sources.cfg 2>/dev/null; then
            echo -e "${GREEN}✅ collective.taskqueue2 en sources.cfg${NC}"
        else
            echo -e "${RED}❌ collective.taskqueue2 NO está en sources.cfg${NC}"
            exit 1
        fi
        
        echo ""
        echo "2️⃣  Ejecutar bootstrap"
        echo "Esto puede tardar 2-5 minutos..."
        ./bootstrap.sh
        
        echo ""
        echo "3️⃣  Crear directorio huey"
        mkdir -p var/huey
        echo -e "${GREEN}✅ Directorio var/huey creado${NC}"
        
        echo ""
        echo "4️⃣  Verificar customizeme.cfg"
        if ! grep -q "async_pdf_enabled" customizeme.cfg 2>/dev/null; then
            echo -e "${YELLOW}⚠️  customizeme.cfg NO tiene variables taskqueue2${NC}"
            echo ""
            echo "Añade a customizeme.cfg:"
            echo ""
            echo "[custom]"
            echo "async_pdf_enabled = 1"
            echo "huey_consumer = 1"
            echo "huey_taskqueue_url = sqlite://\${buildout:directory}/var/huey/instance.db"
            echo "huey_log_level = INFO"
            echo "huey_workers = 2"
            echo ""
        else
            echo -e "${GREEN}✅ customizeme.cfg configurado${NC}"
        fi
        
        echo ""
        echo "========================================"
        echo "✅ SETUP COMPLETADO"
        echo "========================================"
        echo ""
        echo "Siguiente paso:"
        echo "  ./bin/instance fg"
        echo ""
        echo "Verifica en logs:"
        echo "  - collective.taskqueue2 disponible"
        echo "  - Huey consumer started with 2 threads"
        ;;
        
    4)
        echo ""
        echo "========================================"
        echo "  ESTADO ACTUAL"
        echo "========================================"
        echo ""
        
        echo "1️⃣  Configuración"
        if [ -f "$BUILDOUT_DIR/customizeme.cfg" ]; then
            echo ""
            echo "customizeme.cfg:"
            grep -A 5 "async_pdf_enabled" "$BUILDOUT_DIR/customizeme.cfg" 2>/dev/null || echo "  No configurado"
        fi
        
        echo ""
        echo "2️⃣  Base de datos SQLite"
        if [ -f "$HUEY_DB" ]; then
            size=$(du -h "$HUEY_DB" | cut -f1)
            echo -e "${GREEN}✅ Existe: $HUEY_DB ($size)${NC}"
            count_tasks
            
            echo ""
            echo "Tareas pendientes:"
            sqlite3 "$HUEY_DB" "SELECT COUNT(*) FROM kv WHERE key LIKE 'huey.task%';" 2>/dev/null || echo "0"
        else
            echo -e "${YELLOW}⚠️  Base de datos NO existe${NC}"
        fi
        
        echo ""
        echo "3️⃣  Estado de cola"
        if curl -s "http://localhost:${PLONE_PORT}" >/dev/null 2>&1; then
            echo "Instancia corriendo en puerto ${PLONE_PORT}"
            echo ""
            curl -s "http://localhost:${PLONE_PORT}/2/genwebupc/@@taskqueue-stats" 2>/dev/null || echo "Requiere autenticación"
        else
            echo -e "${YELLOW}⚠️  Instancia NO está corriendo${NC}"
        fi
        
        echo ""
        echo "4️⃣  Logs recientes"
        if [ -f "$BUILDOUT_DIR/var/log/instance.log" ]; then
            echo ""
            echo "Últimos logs de Huey:"
            tail -20 "$BUILDOUT_DIR/var/log/instance.log" | grep -E "huey|ASYNC" || echo "Sin logs recientes"
        fi
        ;;
        
    5)
        echo "Saliendo..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Test finalizado"
echo "========================================"
echo ""
echo "Documentación:"
echo "  - docs/README_ASYNC_PDF.md - Overview"
echo "  - docs/INSTALACION_ASYNC_PDF.md - Instalación"
echo "  - docs/CONFIGURACION_ASYNC_PDF.md - Configuración"
echo "  - docs/TESTING_ASYNC_PDF.md - Testing completo"
