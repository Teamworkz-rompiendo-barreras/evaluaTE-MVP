#!/bin/bash

# Script de monitoreo automático para EvaluaTE
echo "🔍 EvaluaTE - Monitor de Servicios"
echo "=================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
CHECK_INTERVAL=30  # segundos
MAX_RETRIES=3
LOG_FILE="monitor.log"

# Función para logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Función para verificar servicios
check_services() {
    local backend_ok=false
    local frontend_ok=false
    
    # Verificar backend
    if curl -s --max-time 10 http://localhost:8000/health >/dev/null 2>&1; then
        backend_ok=true
    fi
    
    # Verificar frontend
    if curl -s --max-time 10 http://localhost:3005 >/dev/null 2>&1; then
        frontend_ok=true
    fi
    
    echo "$backend_ok:$frontend_ok"
}

# Función para reiniciar servicios
restart_services() {
    log_message "🔄 Reiniciando servicios..."
    ./app.sh stop
    sleep 5
    ./app.sh start
    sleep 10
}

# Función para verificar memoria
check_memory() {
    local mem_available=$(free -m | grep Mem | awk '{print $7}')
    local mem_total=$(free -m | grep Mem | awk '{print $2}')
    local mem_percent=$(( (mem_available * 100) / mem_total ))
    
    if [ $mem_percent -lt 20 ]; then
        log_message "⚠️  Memoria baja: ${mem_available}MB disponibles (${mem_percent}%)"
        return 1
    fi
    
    return 0
}

# Función para limpiar recursos si es necesario
cleanup_if_needed() {
    if ! check_memory; then
        log_message "🧹 Ejecutando limpieza de recursos..."
        ./app.sh clean
        sleep 5
    fi
}

# Función principal de monitoreo
monitor_loop() {
    local consecutive_failures=0
    
    log_message "🚀 Iniciando monitoreo automático..."
    
    while true; do
        # Verificar memoria
        cleanup_if_needed
        
        # Verificar servicios
        local status=$(check_services)
        local backend_status=$(echo $status | cut -d: -f1)
        local frontend_status=$(echo $status | cut -d: -f2)
        
        if [ "$backend_status" = "true" ] && [ "$frontend_status" = "true" ]; then
            if [ $consecutive_failures -gt 0 ]; then
                log_message "✅ Servicios restaurados después de $consecutive_failures intentos"
                consecutive_failures=0
            fi
            log_message "✅ Servicios funcionando correctamente"
        else
            consecutive_failures=$((consecutive_failures + 1))
            log_message "❌ Problemas detectados (intento $consecutive_failures/$MAX_RETRIES)"
            
            if [ "$backend_status" = "false" ]; then
                log_message "   - Backend no responde"
            fi
            
            if [ "$frontend_status" = "false" ]; then
                log_message "   - Frontend no responde"
            fi
            
            # Intentar reiniciar si hemos tenido múltiples fallos
            if [ $consecutive_failures -ge $MAX_RETRIES ]; then
                log_message "🔄 Intentando reinicio automático..."
                restart_services
                consecutive_failures=0
            fi
        fi
        
        # Esperar antes de la siguiente verificación
        sleep $CHECK_INTERVAL
    done
}

# Función para mostrar estadísticas
show_stats() {
    echo -e "${BLUE}📊 Estadísticas del monitor:${NC}"
    if [ -f "$LOG_FILE" ]; then
        echo "Últimas 10 entradas del log:"
        tail -10 $LOG_FILE
    else
        echo "No hay archivo de log disponible"
    fi
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}📋 Uso del monitor:${NC}"
    echo "  start   - Iniciar monitoreo automático"
    echo "  stats   - Mostrar estadísticas"
    echo "  check   - Verificación única"
    echo "  help    - Mostrar esta ayuda"
}

# Función para verificación única
single_check() {
    echo -e "${BLUE}🔍 Verificación única de servicios:${NC}"
    local status=$(check_services)
    local backend_status=$(echo $status | cut -d: -f1)
    local frontend_status=$(echo $status | cut -d: -f2)
    
    if [ "$backend_status" = "true" ]; then
        echo -e "${GREEN}✅ Backend: Funcionando${NC}"
    else
        echo -e "${RED}❌ Backend: No responde${NC}"
    fi
    
    if [ "$frontend_status" = "true" ]; then
        echo -e "${GREEN}✅ Frontend: Funcionando${NC}"
    else
        echo -e "${RED}❌ Frontend: No responde${NC}"
    fi
    
    check_memory
}

# Manejo de argumentos
case "$1" in
    "start")
        monitor_loop
        ;;
    "stats")
        show_stats
        ;;
    "check")
        single_check
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac 