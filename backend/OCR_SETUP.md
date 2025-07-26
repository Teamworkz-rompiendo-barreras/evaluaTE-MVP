# Configuración de OCR para Análisis de CV

Este documento explica cómo instalar Tesseract OCR para que el sistema pueda analizar CVs escaneados.

## ¿Qué es OCR?

OCR (Optical Character Recognition) permite extraer texto de imágenes y PDFs escaneados. Sin OCR, el sistema solo puede leer PDFs que contengan texto seleccionable.

## Instalación de Tesseract OCR

### Ubuntu/Debian (WSL/Linux)
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

### macOS
```bash
# Con Homebrew
brew install tesseract tesseract-lang

# O descargar desde: https://github.com/tesseract-ocr/tesseract
```

### Windows
1. Descargar el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar y agregar al PATH
3. Descargar archivos de idioma español e inglés

### Verificar instalación
```bash
tesseract --version
```

## Dependencias de Python

Las dependencias de Python ya están incluidas en `requirements.txt`:
- `pytesseract==0.3.13`
- `pillow==11.3.0`
- `PyMuPDF==1.23.8`

## Funcionamiento del Sistema

### Con OCR instalado:
- Lee PDFs con texto seleccionable
- Lee PDFs escaneados (imágenes)
- Análisis más completo y preciso

### Sin OCR instalado:
- Solo lee PDFs con texto seleccionable
- Muestra advertencia pero sigue funcionando
- Análisis limitado para PDFs escaneados

## Pruebas

Para probar el sistema:
```bash
cd backend
source venv/bin/activate
python test_ocr.py cv_prueba.pdf
```

## Solución de Problemas

### Error: "tesseract not found"
- Instalar Tesseract OCR según las instrucciones arriba
- Verificar que esté en el PATH del sistema

### Error: "No module named 'pytesseract'"
```bash
pip install pytesseract pillow
```

### Error: "No module named 'PIL'"
```bash
pip install pillow
```

## Compatibilidad

El sistema es compatible con:
- PDFs con texto seleccionable
- PDFs escaneados (con OCR)
- Imágenes de CV (con OCR)
- Diferentes formatos y estructuras de CV

## Mejoras Implementadas

1. **Extracción de texto flexible**: Usa PyMuPDF primero, OCR si es necesario
2. **Análisis independiente de estructura**: No depende de encabezados específicos
3. **Detección de habilidades**: Busca tecnologías en todo el texto
4. **Extracción de contacto**: Encuentra emails y teléfonos automáticamente
5. **Análisis de experiencia**: Detecta fechas y empresas con patrones flexibles
6. **Manejo de errores robusto**: Continúa funcionando incluso si OCR falla 