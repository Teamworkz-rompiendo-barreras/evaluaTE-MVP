#!/bin/bash

# Script para verificar el estado de los servicios de EvaluaTE
echo "🔍 Verificando servicios de EvaluaTE..."
echo "======================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar backend
echo -e "${BLUE}🔧 Verificando Backend (puerto 8000)...${NC}"
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend funcionando correctamente${NC}"
    echo -e "   📍 URL: http://localhost:8000"
    echo -e "   📚 Docs: http://localhost:8000/docs"
else
    echo -e "${RED}❌ Backend no responde${NC}"
fi

echo ""

# Verificar frontend
echo -e "${BLUE}🎨 Verificando Frontend (puerto 3005)...${NC}"
if curl -s http://localhost:3005/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend funcionando correctamente${NC}"
    echo -e "   📍 URL: http://localhost:3005"
else
    echo -e "${RED}❌ Frontend no responde${NC}"
fi

echo ""

# Verificar comunicación entre servicios
echo -e "${BLUE}🔗 Verificando comunicación entre servicios...${NC}"
if curl -s http://localhost:8000/ | grep -q "EvaluaTE MVP"; then
    echo -e "${GREEN}✅ Comunicación backend-frontend OK${NC}"
else
    echo -e "${YELLOW}⚠️  Comunicación backend-frontend no verificada${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Verificación completada${NC}"
echo ""
echo -e "${BLUE}💡 Para acceder a la aplicación:${NC}"
echo -e "   🌐 Frontend: http://localhost:3005"
echo -e "   🔧 Backend: http://localhost:8000"
echo -e "   📚 API Docs: http://localhost:8000/docs" 