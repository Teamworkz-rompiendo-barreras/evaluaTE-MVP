#!/bin/bash

# Script de optimización para WSL - EvaluaTE
echo "⚙️  EvaluaTE - Optimización de WSL"
echo "=================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para verificar si estamos en WSL
check_wsl() {
    if grep -qi microsoft /proc/version; then
        echo -e "${GREEN}✅ Ejecutando en WSL${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  No se detectó WSL${NC}"
        return 1
    fi
}

# Función para optimizar memoria
optimize_memory() {
    echo -e "${BLUE}🧠 Optimizando memoria...${NC}"
    
    # Limpiar caché de memoria
    sudo sync && sudo sysctl vm.drop_caches=3 >/dev/null 2>&1
    
    # Ajustar swappiness
    if [ -f /proc/sys/vm/swappiness ]; then
        echo 10 | sudo tee /proc/sys/vm/swappiness >/dev/null 2>&1
        echo -e "${GREEN}✅ Swappiness ajustado a 10${NC}"
    fi
    
    # Limpiar archivos temporales
    sudo rm -rf /tmp/* >/dev/null 2>&1
    sudo rm -rf /var/tmp/* >/dev/null 2>&1
    
    echo -e "${GREEN}✅ Optimización de memoria completada${NC}"
}

# Función para optimizar red
optimize_network() {
    echo -e "${BLUE}🌐 Optimizando red...${NC}"
    
    # Ajustar parámetros de red
    if [ -f /proc/sys/net/core/rmem_max ]; then
        echo 16777216 | sudo tee /proc/sys/net/core/rmem_max >/dev/null 2>&1
        echo 16777216 | sudo tee /proc/sys/net/core/wmem_max >/dev/null 2>&1
    fi
    
    # Ajustar timeouts de TCP
    if [ -f /proc/sys/net/ipv4/tcp_keepalive_time ]; then
        echo 300 | sudo tee /proc/sys/net/ipv4/tcp_keepalive_time >/dev/null 2>&1
        echo 60 | sudo tee /proc/sys/net/ipv4/tcp_keepalive_intvl >/dev/null 2>&1
        echo 3 | sudo tee /proc/sys/net/ipv4/tcp_keepalive_probes >/dev/null 2>&1
    fi
    
    echo -e "${GREEN}✅ Optimización de red completada${NC}"
}

# Función para configurar límites del sistema
configure_limits() {
    echo -e "${BLUE}📊 Configurando límites del sistema...${NC}"
    
    # Crear archivo de límites temporal
    cat > /tmp/evaluate-limits.conf << EOF
# Límites para EvaluaTE
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF
    
    # Aplicar límites
    if command -v ulimit >/dev/null 2>&1; then
        ulimit -n 65536 >/dev/null 2>&1
        ulimit -u 32768 >/dev/null 2>&1
        echo -e "${GREEN}✅ Límites aplicados${NC}"
    fi
    
    rm -f /tmp/evaluate-limits.conf
}

# Función para optimizar procesos
optimize_processes() {
    echo -e "${BLUE}⚡ Optimizando procesos...${NC}"
    
    # Ajustar nice para procesos de la aplicación
    if pgrep -f "python main.py" >/dev/null; then
        sudo renice -n -5 -p $(pgrep -f "python main.py") >/dev/null 2>&1
        echo -e "${GREEN}✅ Prioridad ajustada para backend${NC}"
    fi
    
    if pgrep -f "vite" >/dev/null; then
        sudo renice -n -5 -p $(pgrep -f "vite") >/dev/null 2>&1
        echo -e "${GREEN}✅ Prioridad ajustada para frontend${NC}"
    fi
}

# Función para crear configuración de WSL
create_wsl_config() {
    echo -e "${BLUE}📝 Creando configuración de WSL...${NC}"
    
    # Crear archivo .wslconfig en Windows (si es posible)
    cat > wsl-config-template.txt << EOF
# Configuración recomendada para EvaluaTE en WSL
# Copiar este contenido a %USERPROFILE%\.wslconfig en Windows

[wsl2]
# Memoria asignada a WSL
memory=4GB

# Número de procesadores
processors=2

# Configuración de swap
swap=2GB

# Configuración de red
networkingMode=mirrored

# Configuración de archivos
localhostForwarding=true

# Configuración de rendimiento
kernelCommandLine=cgroup_enable=1 cgroup_memory=1 cgroup_enable=cpu

# Configuración de almacenamiento
automount.enabled=true
automount.root=/mnt/
automount.options="metadata,umask=22,fmask=11"
EOF
    
    echo -e "${GREEN}✅ Plantilla de configuración creada${NC}"
    echo -e "${YELLOW}📋 Copia el contenido de wsl-config-template.txt a %USERPROFILE%\.wslconfig en Windows${NC}"
}

# Función para mostrar información del sistema
show_system_info() {
    echo -e "${BLUE}📊 Información del sistema:${NC}"
    echo "Memoria total: $(free -h | grep Mem | awk '{print $2}')"
    echo "Memoria disponible: $(free -h | grep Mem | awk '{print $7}')"
    echo "CPU: $(nproc) núcleos"
    echo "Versión de kernel: $(uname -r)"
    echo "Distribución: $(lsb_release -d | cut -f2)"
}

# Función para optimización completa
full_optimization() {
    echo -e "${BLUE}🚀 Iniciando optimización completa...${NC}"
    
    if ! check_wsl; then
        echo -e "${YELLOW}⚠️  Algunas optimizaciones pueden no ser aplicables${NC}"
    fi
    
    optimize_memory
    optimize_network
    configure_limits
    optimize_processes
    create_wsl_config
    
    echo -e "${GREEN}✅ Optimización completa finalizada${NC}"
    echo -e "${YELLOW}💡 Reinicia WSL para aplicar todos los cambios${NC}"
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}📋 Comandos disponibles:${NC}"
    echo "  full    - Optimización completa"
    echo "  memory  - Optimizar memoria"
    echo "  network - Optimizar red"
    echo "  limits  - Configurar límites"
    echo "  info    - Mostrar información del sistema"
    echo "  help    - Mostrar esta ayuda"
}

# Manejo de argumentos
case "$1" in
    "full")
        full_optimization
        ;;
    "memory")
        optimize_memory
        ;;
    "network")
        optimize_network
        ;;
    "limits")
        configure_limits
        ;;
    "info")
        show_system_info
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