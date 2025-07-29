# Sistema de Análisis de CV con IA

## Descripción

Este sistema utiliza Inteligencia Artificial para analizar CVs de manera inteligente y flexible, extrayendo información estructurada independientemente del formato o estructura del documento.

## Características Principales

### ✅ **Análisis Inteligente**
- Utiliza IA para interpretar el contenido del CV
- No depende de patrones específicos o estructuras predefinidas
- Maneja diferentes idiomas (español e inglés)
- Interpreta fechas en cualquier formato

### ✅ **OCR Avanzado**
- Procesa PDFs escaneados de múltiples páginas
- Alta resolución para mejor calidad de OCR
- Fallback inteligente si OCR falla
- Configuración optimizada para CVs

### ✅ **Extracción Completa**
- Información de contacto
- Experiencia laboral detallada
- Formación académica
- Habilidades técnicas y blandas
- Idiomas y niveles
- Proyectos y certificaciones

### ✅ **Análisis de Calidad**
- Evaluación automática de la estructura del CV
- Detección de fortalezas y debilidades
- Recomendaciones personalizadas
- Puntuación de empleabilidad

## Instalación

### 1. Dependencias Python
```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR (para PDFs escaneados)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
- Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar y agregar al PATH

### 3. Variables de Entorno
Crear archivo `.env` en el directorio `backend/`:
```env
AZURE_OPENAI_API_KEY=tu_api_key
AZURE_OPENAI_ENDPOINT=tu_endpoint
AZURE_OPENAI_DEPLOYMENT=tu_deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Uso

### Uso Básico
```python
from cv_analyzer import extract_pdf_info

# Leer archivo PDF
with open('mi_cv.pdf', 'rb') as f:
    pdf_buffer = f.read()

# Analizar CV
result = extract_pdf_info(pdf_buffer)

# Obtener resultados
if result.get("error"):
    print(f"Error: {result['error']}")
else:
    analysis = result['analysis']
    cv_info = result['cv_info']
    full_data = result['full_cv_data']
    
    print(f"Estructura: {analysis['structure']}")
    print(f"Experiencia: {len(full_data['experiencia_laboral'])} puestos")
    print(f"Habilidades: {len(full_data['habilidades_tecnicas'])} técnicas")
```

### Uso con FastAPI
```python
from fastapi import FastAPI, UploadFile, File
from cv_analyzer import extract_pdf_info

app = FastAPI()

@app.post("/analyze-cv")
async def analyze_cv(file: UploadFile = File(...)):
    contents = await file.read()
    result = extract_pdf_info(contents)
    return result
```

## Estructura de Datos

### Resultado Completo
```python
{
    "cv_info": {
        "contacto": {...},
        "software": [...],
        "idiomas": [...],
        "perfil": "...",
        "experiencia": [...],
        "educacion": [...],
        "habilidades": [...],
        "proyectos": [...]
    },
    "analysis": {
        "structure": "excelente|bueno|regular|mejorable",
        "coherence": "excelente|bueno|regular|mejorable",
        "experience": "excelente|bueno|regular|mejorable",
        "skills": [...],
        "softSkills": [...],
        "languages": [...],
        "education": [...],
        "strengths": [...],
        "weaknesses": [...],
        "feedback": "...",
        "alerts": [...],
        "total_years_experience": 5,
        "technologies_count": 10,
        "soft_skills_count": 5,
        "languages_count": 3,
        "experience_count": 4,
        "education_count": 3,
        "projects_count": 2
    },
    "full_cv_data": {
        "contacto": {
            "nombre": "Juan Pérez",
            "email": "juan@email.com",
            "telefono": "+34 123 456 789",
            "ubicacion": "Madrid, España"
        },
        "experiencia_laboral": [
            {
                "empresa": "Empresa ABC",
                "cargo": "Desarrollador Senior",
                "fecha_inicio": "Enero 2020",
                "fecha_fin": "actualidad",
                "descripcion": "Desarrollo de aplicaciones web...",
                "logros": ["Logro 1", "Logro 2"],
                "tecnologias": ["Python", "React", "Docker"]
            }
        ],
        "formacion_academica": [...],
        "habilidades_tecnicas": [...],
        "habilidades_blandas": [...],
        "idiomas": [...],
        "proyectos": [...],
        "certificaciones": [...],
        "voluntariado": [...]
    },
    "raw_text": "Texto extraído del PDF...",
    "error": null
}
```

## Pruebas

### Ejecutar Pruebas Completas
```bash
cd backend
python test_cv_analyzer.py
```

### Probar Solo OCR
```bash
python test_cv_analyzer.py ocr
```

### Probar con Archivo Específico
```bash
python cv_analyzer.py mi_cv.pdf
```

## Configuración Avanzada

### Ajustar Calidad de OCR
```python
# En cv_analyzer.py, línea ~40
zoom = 2.0  # Aumentar para mejor calidad (más lento)
zoom = 1.5  # Reducir para mayor velocidad (menor calidad)
```

### Configurar Idiomas de OCR
```python
# En cv_analyzer.py, línea ~50
ocr_text = pytesseract.image_to_string(
    img, 
    lang='spa+eng+fra',  # Agregar más idiomas
    config=ocr_config
)
```

### Ajustar Prompt de IA
```python
# En cv_analyzer.py, función analyze_cv_with_ai
# Modificar el prompt para ajustar el comportamiento de la IA
```

## Solución de Problemas

### Error: "OCR no disponible"
```bash
# Instalar Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# Verificar instalación
tesseract --version
```

### Error: "Azure OpenAI no configurado"
```bash
# Verificar variables de entorno
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# O crear archivo .env
cp env.example .env
# Editar .env con tus credenciales
```

### Error: "No se pudo extraer texto"
- Verificar que el PDF no esté corrupto
- Probar con un PDF diferente
- Verificar que Tesseract esté instalado correctamente

### Rendimiento Lento
- Reducir el zoom en OCR (línea 40)
- Limitar el número de páginas procesadas
- Usar un modelo de IA más rápido

## Compatibilidad

### Formatos Soportados
- ✅ PDF con texto seleccionable
- ✅ PDF escaneado (con OCR)
- ✅ Múltiples páginas
- ✅ Diferentes idiomas

### Estructuras de CV
- ✅ Europea
- ✅ Americana
- ✅ Creativa
- ✅ Cronológica
- ✅ Funcional
- ✅ Mixta

### Idiomas
- ✅ Español
- ✅ Inglés
- 🔄 Francés (en desarrollo)
- 🔄 Alemán (en desarrollo)

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature
3. Hacer cambios y pruebas
4. Crear un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.