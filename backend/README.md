# 🚀 Backend EvaluaTE - API REST con FastAPI

Backend de la aplicación EvaluaTE que proporciona APIs para análisis de CVs, generación de informes de empleabilidad y servicios de IA.

## 🏗️ Arquitectura

- **Framework**: FastAPI (Python 3.8+)
- **IA**: Azure OpenAI (GPT-3.5/4)
- **Documentos**: Azure Document Intelligence
- **PDFs**: ReportLab
- **Validación**: Pydantic

## 📋 Prerrequisitos

- Python 3.8 o superior
- Credenciales de Azure OpenAI
- Credenciales de Azure Document Intelligence (opcional)

## 🚀 Instalación Rápida

### 1. Configurar entorno virtual
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
python setup-env.py
# Edita el archivo .env con tus credenciales de Azure
```

### 4. Verificar sistema
```bash
python verify-system.py
```

### 5. Iniciar servidor
```bash
python main.py
```

## 🔧 Configuración

### Variables de Entorno Críticas

```bash
# Azure OpenAI (REQUERIDO para funcionalidad completa)
AZURE_OPENAI_API_KEY=tu_api_key_aqui
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo

# Azure Document Intelligence (OPCIONAL)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=tu_document_intelligence_key_aqui
```

### Obtener Credenciales de Azure

1. Ve a [Azure Portal](https://portal.azure.com)
2. Crea un recurso "Azure OpenAI"
3. Ve a "Keys and Endpoint"
4. Copia la Key 1 y el Endpoint
5. Ve a "Model deployments" y crea un deployment

## 📡 Endpoints Principales

### Salud del Sistema
- `GET /health` - Estado del sistema
- `GET /api/system/status` - Estado detallado de servicios

### Análisis de CVs
- `POST /api/pdf/analyze-cv` - Analiza CV en PDF
- `POST /api/informe-ia` - Genera informe de empleabilidad

### Generación de PDFs
- `POST /api/pdf/generate-report` - Genera PDF del informe

## 🧪 Testing

### Verificar Sistema
```bash
python verify-system.py
```

### Tests Unitarios
```bash
python -m pytest tests/
```

### Tests de Integración
```bash
python test_complete_flow.py
```

## 🐛 Solución de Problemas

### Error: "uvicorn: command not found"
```bash
pip install uvicorn[standard]
```

### Error: "No module named 'openai'"
```bash
pip install openai
```

### Error: "Azure OpenAI no configurado"
1. Verifica que el archivo `.env` existe
2. Configura `AZURE_OPENAI_API_KEY` y `AZURE_OPENAI_ENDPOINT`
3. Reinicia el servidor

### Error: "Document Intelligence no disponible"
1. Configura `AZURE_DOCUMENT_INTELLIGENCE_KEY`
2. La aplicación funcionará en modo básico sin esta funcionalidad

## 📁 Estructura del Proyecto

```
backend/
├── main.py                 # Aplicación principal FastAPI
├── new_report_schema.py    # Esquema de informes estructurados
├── generate_report.py      # Generador de informes con IA
├── pdf_service.py          # Servicio de generación de PDFs
├── document_intelligence.py # Servicio de análisis de documentos
├── cv_analyzer.py          # Analizador de CVs
├── prompt_config.py        # Configuración de prompts de IA
├── requirements.txt        # Dependencias Python
├── setup-env.py           # Script de configuración automática
├── verify-system.py       # Script de verificación del sistema
└── README.md              # Este archivo
```

## 🔄 Modo de Funcionamiento

### Modo Completo (con Azure)
- ✅ Análisis avanzado de CVs con IA
- ✅ Generación de informes personalizados
- ✅ Extracción inteligente de información
- ✅ Procesamiento de PDFs escaneados

### Modo Básico (sin Azure)
- ✅ Análisis básico de CVs
- ✅ Generación de informes estándar
- ✅ Procesamiento de PDFs con texto
- ⚠️ Funcionalidad limitada de IA

## 🚀 Despliegue

### Desarrollo Local
```bash
python main.py
```

### Producción (Azure Web App)
```bash
# El proyecto incluye configuración automática para Azure
# Ver archivos web.config y startup.py
```

## 📞 Soporte

Si encuentras problemas:

1. Ejecuta `python verify-system.py` para diagnóstico
2. Verifica la configuración en `.env`
3. Revisa los logs del servidor
4. Consulta la documentación de Azure OpenAI

## 📄 Licencia

Este proyecto es parte de EvaluaTE MVP.
