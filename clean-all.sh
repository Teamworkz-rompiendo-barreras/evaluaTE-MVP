#!/bin/bash

# Script de limpieza completa para EvaluaTE
echo "🧹 EvaluaTE - Limpieza Completa"
echo "==============================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para detener todos los servicios
stop_all_services() {
    echo -e "${BLUE}🛑 Deteniendo todos los servicios...${NC}"
    
    # Detener servicios de la aplicación
    ./app.sh stop 2>/dev/null || true
    
    # Detener monitor si está corriendo
    if [ -f monitor.pid ]; then
        MONITOR_PID=$(cat monitor.pid)
        kill $MONITOR_PID 2>/dev/null || true
        rm -f monitor.pid
    fi
    
    # Detener procesos relacionados
    pkill -f "python main.py" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm" 2>/dev/null || true
    pkill -f "serve" 2>/dev/null || true
    pkill -f "monitor.sh" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para limpiar cachés
clean_caches() {
    echo -e "${BLUE}🧹 Limpiando cachés...${NC}"
    
    # Limpiar cachés de Python
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # Limpiar cachés de Node.js
    if [ -d "nuevo-frontend/node_modules/.cache" ]; then
        rm -rf nuevo-frontend/node_modules/.cache
    fi
    
    # Limpiar cachés del sistema
    sudo rm -rf /tmp/* 2>/dev/null || true
    sudo rm -rf /var/tmp/* 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cachés limpiados${NC}"
}

# Función para limpiar builds
clean_builds() {
    echo -e "${BLUE}🏗️  Limpiando builds...${NC}"
    
    # Limpiar build del frontend
    if [ -d "nuevo-frontend/dist" ]; then
        rm -rf nuevo-frontend/dist
        echo -e "${GREEN}✅ Build del frontend eliminado${NC}"
    fi
    
    # Limpiar build del backend
    if [ -d "backend/__pycache__" ]; then
        rm -rf backend/__pycache__
        echo -e "${GREEN}✅ Cache del backend eliminado${NC}"
    fi
    
    echo -e "${GREEN}✅ Builds limpiados${NC}"
}

# Función para limpiar logs
clean_logs() {
    echo -e "${BLUE}📋 Limpiando logs...${NC}"
    
    # Eliminar archivos de log
    rm -f monitor.log 2>/dev/null || true
    rm -f *.log 2>/dev/null || true
    
    echo -e "${GREEN}✅ Logs limpiados${NC}"
}

# Función para limpiar dependencias (opcional)
clean_dependencies() {
    echo -e "${BLUE}📦 Limpiando dependencias...${NC}"
    
    read -p "¿Eliminar también node_modules y reinstalar dependencias? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Eliminar node_modules
        if [ -d "nuevo-frontend/node_modules" ]; then
            rm -rf nuevo-frontend/node_modules
            echo -e "${GREEN}✅ node_modules eliminado${NC}"
        fi
        
        # Limpiar cache de npm
        npm cache clean --force 2>/dev/null || true
        echo -e "${GREEN}✅ Cache de npm limpiado${NC}"
    fi
    
    echo -e "${GREEN}✅ Dependencias limpiadas${NC}"
}

# Función para optimizar memoria
optimize_memory() {
    echo -e "${BLUE}🧠 Optimizando memoria...${NC}"
    
    # Limpiar caché de memoria
    sudo sync && sudo sysctl vm.drop_caches=3 >/dev/null 2>&1
    
    # Ajustar swappiness
    if [ -f /proc/sys/vm/swappiness ]; then
        echo 5 | sudo tee /proc/sys/vm/swappiness >/dev/null 2>&1
    fi
    
    echo -e "${GREEN}✅ Memoria optimizada${NC}"
}

# Función para mostrar información del sistema
show_system_info() {
    echo -e "${BLUE}📊 Información del sistema después de la limpieza:${NC}"
    echo "Memoria disponible: $(free -h | grep Mem | awk '{print $7}')"
    echo "Espacio en disco: $(df -h . | tail -1 | awk '{print $4}') disponibles"
    echo "Procesos activos: $(ps aux | grep -E "(python|node|npm|vite)" | grep -v grep | wc -l)"
}

# Función principal
main() {
    echo -e "${BLUE}🚀 Iniciando limpieza completa...${NC}"
    
    # Detener servicios
    stop_all_services
    
    # Limpiar cachés
    clean_caches
    
    # Limpiar builds
    clean_builds
    
    # Limpiar logs
    clean_logs
    
    # Limpiar dependencias (opcional)
    clean_dependencies
    
    # Optimizar memoria
    optimize_memory
    
    # Mostrar información del sistema
    show_system_info
    
    echo -e "${GREEN}🎉 ¡Limpieza completa finalizada!${NC}"
    echo -e "${YELLOW}💡 Ahora puedes ejecutar ./startup-prod.sh para iniciar en modo producción${NC}"
}

# Ejecutar función principal
main "$@" 