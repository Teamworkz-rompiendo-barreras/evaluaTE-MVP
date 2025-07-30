#!/bin/bash

# Script para verificar y reparar dependencias de EvaluaTE
echo "🔧 Verificando y reparando dependencias de EvaluaTE..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para verificar dependencias Python
check_python_deps() {
    local venv_path="$1"
    local venv_name="$2"
    
    echo -e "${BLUE}📋 Verificando dependencias en $venv_name...${NC}"
    
    if [ ! -d "$venv_path" ]; then
        echo -e "${RED}❌ Entorno virtual $venv_name no encontrado en $venv_path${NC}"
        return 1
    fi
    
    # Activar entorno virtual
    source "$venv_path/bin/activate"
    
    # Lista de dependencias críticas
    local critical_deps=(
        "python-dotenv"
        "openai"
        "pytesseract"
        "Pillow"
        "PyMuPDF"
        "fastapi"
        "uvicorn"
        "pypdf"
        "reportlab"
    )
    
    local missing_deps=()
    
    for dep in "${critical_deps[@]}"; do
        # Mapear nombres de paquetes a nombres de módulos
        local module_name
        case $dep in
            "python-dotenv") module_name="dotenv" ;;
            "PyMuPDF") module_name="fitz" ;;
            "Pillow") module_name="PIL" ;;
            *) module_name="${dep//-/_}" ;;
        esac
        
        if ! python -c "import $module_name" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Faltante: $dep${NC}"
            missing_deps+=("$dep")
        else
            echo -e "${GREEN}✅ $dep${NC}"
        fi
    done
    
    # Instalar dependencias faltantes
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${YELLOW}📦 Instalando dependencias faltantes en $venv_name...${NC}"
        
        # Verificar que estamos en un entorno virtual
        if [ -z "$VIRTUAL_ENV" ]; then
            echo -e "${RED}❌ Error: No estás en un entorno virtual${NC}"
            echo -e "${YELLOW}💡 Activa el entorno virtual primero:${NC}"
            echo -e "   source .venv/bin/activate"
            return 1
        fi
        
        pip install "${missing_deps[@]}"
        
        # Verificar instalación
        echo -e "${BLUE}🔍 Verificando instalación...${NC}"
        for dep in "${missing_deps[@]}"; do
            # Mapear nombres de paquetes a nombres de módulos
            local module_name
            case $dep in
                "python-dotenv") module_name="dotenv" ;;
                "PyMuPDF") module_name="fitz" ;;
                "Pillow") module_name="PIL" ;;
                *) module_name="${dep//-/_}" ;;
            esac
            
            if python -c "import $module_name" 2>/dev/null; then
                echo -e "${GREEN}✅ $dep instalado correctamente${NC}"
            else
                echo -e "${RED}❌ Error instalando $dep${NC}"
            fi
        done
    else
        echo -e "${GREEN}🎉 Todas las dependencias están instaladas en $venv_name${NC}"
    fi
    
    # Desactivar entorno virtual
    deactivate
}

# Función para verificar variables de entorno
check_env_vars() {
    echo -e "${BLUE}🔐 Verificando variables de entorno...${NC}"
    
    local env_file="backend/.env"
    if [ ! -f "$env_file" ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado en backend/${NC}"
        echo -e "${BLUE}📝 Creando archivo .env de ejemplo...${NC}"
        cat > "$env_file" << EOF
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database Configuration (if needed)
DATABASE_URL=your_database_url_here

# Other Configuration
DEBUG=True
LOG_LEVEL=INFO
EOF
        echo -e "${GREEN}✅ Archivo .env creado. Por favor, configura tus credenciales.${NC}"
    else
        echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
    fi
}

# Función para verificar estructura de directorios
check_structure() {
    echo -e "${BLUE}📁 Verificando estructura de directorios...${NC}"
    
    local required_dirs=(
        "backend"
        "nuevo-frontend"
        ".venv"
        "backend/uploads"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✅ $dir${NC}"
        else
            echo -e "${YELLOW}⚠️  Creando directorio: $dir${NC}"
            mkdir -p "$dir"
        fi
    done
}

# Función para crear script de activación automática
create_activation_script() {
    echo -e "${BLUE}📝 Creando script de activación automática...${NC}"
    
    cat > "activate_env.sh" << 'EOF'
#!/bin/bash

# Script para activar automáticamente el entorno correcto
echo "🚀 Activando entorno de EvaluaTE..."

# Verificar si estamos en el directorio correcto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: No estás en el directorio raíz de EvaluaTE"
    echo "   Navega al directorio del proyecto y ejecuta este script"
    exit 1
fi

# Activar entorno virtual
if [ -d ".venv" ]; then
    echo "✅ Activando entorno virtual..."
    source .venv/bin/activate
    echo "🎉 Entorno activado. Ahora puedes ejecutar:"
    echo "   python backend/main.py"
    echo "   uvicorn backend.main:app --reload"
else
    echo "❌ Entorno virtual no encontrado. Ejecuta:"
    echo "   ./fix_dependencies.sh"
fi
EOF

    chmod +x "activate_env.sh"
    echo -e "${GREEN}✅ Script de activación creado: ./activate_env.sh${NC}"
}

# Función para verificar servicios
check_services() {
    echo -e "${BLUE}🔍 Verificando servicios...${NC}"
    
    # Verificar si el backend está ejecutándose
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend ejecutándose en puerto 8000${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend no está ejecutándose${NC}"
        echo -e "${BLUE}💡 Para iniciar el backend:${NC}"
        echo -e "   source .venv/bin/activate"
        echo -e "   cd backend && python main.py"
    fi
    
    # Verificar si el frontend está ejecutándose
    if curl -s http://localhost:5173/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend ejecutándose en puerto 5173${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend no está ejecutándose${NC}"
        echo -e "${BLUE}💡 Para iniciar el frontend:${NC}"
        echo -e "   cd nuevo-frontend && npm run dev"
    fi
}

# Función principal
main() {
    echo -e "${BLUE}🚀 Iniciando verificación completa de dependencias...${NC}"
    
    # Verificar estructura
    check_structure
    
    # Verificar dependencias en .venv
    check_python_deps ".venv" ".venv"
    
    # Verificar variables de entorno
    check_env_vars
    
    # Crear script de activación
    create_activation_script
    
    # Verificar servicios
    check_services
    
    echo -e "${GREEN}🎉 Verificación completada!${NC}"
    echo -e "${BLUE}💡 Próximos pasos:${NC}"
    echo -e "   1. Configura las variables de entorno en backend/.env"
    echo -e "   2. Activa el entorno: source .venv/bin/activate"
    echo -e "   3. Inicia el backend: cd backend && python main.py"
    echo -e "   4. Inicia el frontend: cd nuevo-frontend && npm run dev"
}

# Ejecutar función principal
main "$@" 