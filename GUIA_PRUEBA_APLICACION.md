# 🚀 GUÍA DE PRUEBA - EVALUATE MVP

## 📋 **INFORMACIÓN DE ACCESO**

### **URLs de la Aplicación**
- **Frontend**: http://localhost:3007
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🎯 **FLUJO DE PRUEBA COMPLETO**

### **PASO 1: Acceso Inicial**
1. Abre tu navegador
2. Ve a: **http://localhost:3007**
3. Deberías ver la página de inicio de EvaluaTE MVP

### **PASO 2: Registro de Datos Personales**
1. Completa el formulario con datos de prueba:
   - **Nombre**: Ana García
   - **Apellidos**: López
   - **Email**: ana.garcia@test.com
   - **WhatsApp**: 612345678
   - **Discapacidad**: (dejar vacío)
   - **Tipo de discapacidad**: (dejar vacío)
   - **Puesto deseado**: Desarrolladora Frontend
   - **Jornada**: Remoto
   - **Disponibilidad**: Completa
   - **¿Traslado?**: No

2. Haz clic en **"Continuar"**

### **PASO 3: Preferencias Laborales**
1. Completa las preferencias:
   - **Tipo de trabajo**: Desarrollo Frontend
   - **Modalidad**: Remoto
   - **Disponibilidad**: Completa
   - **Fecha de inicio**: Inmediata
   - **¿Mudarse?**: No
   - **¿Certificado discapacidad?**: No
   - **Necesidades específicas**: Horario flexible

2. Haz clic en **"Guardar y Continuar"**

### **PASO 4: Pantalla de Bienvenida a Minijuegos**
1. Deberías ver la pantalla de bienvenida
2. Lee la información sobre los minijuegos
3. Haz clic en **"Comenzar"**

### **PASO 5: Dashboard de Minijuegos**
1. Verás una lista de minijuegos disponibles
2. Haz clic en el primer minijuego: **"Primera llamada del día"**
3. Este minijuego evalúa **Toma de Decisiones**

### **PASO 6: Jugar el Minijuego**
1. Lee la escena presentada
2. Selecciona una opción basada en tu criterio
3. Observa cómo se registra tu decisión
4. Completa el minijuego

### **PASO 7: Subir CV**
1. Regresa al dashboard
2. Ve a la sección de **"Subir CV"**
3. Prepara un archivo PDF con tu CV (o usa uno de prueba)
4. Sube el archivo
5. Verifica que se procese correctamente

### **PASO 8: Análisis de CV con IA**
1. Una vez subido el CV, se iniciará el análisis automático
2. Observa cómo la IA analiza:
   - Fortalezas del CV
   - Áreas de mejora
   - Habilidades técnicas detectadas
   - Feedback personalizado

### **PASO 9: Generación del Informe Final**
1. Al completar todos los pasos, se generará automáticamente el informe
2. Revisa:
   - Puntuación de empleabilidad
   - Nivel asignado (Alto/Medio/Bajo)
   - Recomendaciones personalizadas
   - Roles sugeridos
   - Recursos de formación

---

## 🧪 **DATOS DE PRUEBA RECOMENDADOS**

### **CV de Prueba**
Crea un archivo PDF con este contenido:

```
CURRICULUM VITAE

DATOS PERSONALES
Nombre: Ana García López
Email: ana.garcia@test.com
Teléfono: +34 612 345 678

EXPERIENCIA LABORAL
2020-2023: Desarrolladora Frontend
TechCorp S.L., Madrid
- Desarrollo de aplicaciones web con React y TypeScript
- Colaboración en equipo de 8 personas
- Optimización de rendimiento web

2018-2020: Técnica de Soporte
SoftServe, Barcelona
- Atención al cliente técnico
- Resolución de problemas de software

EDUCACIÓN
2014-2018: Grado en Ingeniería Informática
Universidad Politécnica de Madrid

HABILIDADES TÉCNICAS
- JavaScript, TypeScript, React
- HTML, CSS, Bootstrap
- Git, GitHub
- Metodologías ágiles

IDIOMAS
- Español: Nativo
- Inglés: B2
```

### **Respuestas de Minijuegos**
Para obtener resultados variados, prueba diferentes opciones:
- **Escena 1**: Opción A (más directa) vs Opción B (más analítica)
- **Escena 2**: Opción C (colaborativa) vs Opción D (individual)

---

## 🔍 **VERIFICACIONES IMPORTANTES**

### **Durante la Prueba**
1. ✅ **Navegación fluida** entre páginas
2. ✅ **Formularios** se guardan correctamente
3. ✅ **Minijuegos** registran decisiones
4. ✅ **Subida de CV** funciona
5. ✅ **Análisis de IA** genera resultados
6. ✅ **Informe final** es completo y personalizado

### **Logs del Backend**
Observa en la terminal del backend:
```
LOG SCENE: {'sceneId': 1, 'decisions': [...]}
GAME COMPLETE: {'sceneId': 1, 'completed': True}
INFO:main:Análisis de CV completado para usuario...
```

### **Respuestas de la IA**
Verifica que el análisis incluya:
- Fortalezas específicas del CV
- Áreas de mejora concretas
- Habilidades técnicas detectadas
- Feedback personalizado

---

## 🐛 **SOLUCIÓN DE PROBLEMAS**

### **Si el Frontend no carga**
```bash
cd nuevo-frontend
npm run dev
```

### **Si el Backend no responde**
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **Si hay errores de CORS**
- Verifica que el backend esté en puerto 8000
- Verifica que el frontend esté en puerto 3007
- Revisa los logs del backend

### **Si el análisis de CV falla**
- Verifica que el archivo sea PDF válido
- Verifica que tenga texto extraíble
- Revisa los logs de Azure OpenAI

---

## 📊 **RESULTADOS ESPERADOS**

### **Al completar la prueba deberías ver:**
1. **Puntuación de empleabilidad**: Entre 60-90 puntos
2. **Nivel**: Alto, Medio o Bajo según tus respuestas
3. **Recomendaciones**: Específicas para tu perfil
4. **Roles sugeridos**: Basados en tus habilidades
5. **Recursos**: Enlaces a formación relevante

### **Ejemplo de resultado exitoso:**
```
🎯 Puntuación: 82/100
📊 Nivel: Empleabilidad media
💼 Roles sugeridos: Desarrollador frontend, Soporte técnico
📚 Recursos: Platzi, Microsoft Learn
📝 Mejoras: Actualizar CV, completar juegos
```

---

## 🎉 **¡LISTO PARA PROBAR!**

**URLs activas:**
- 🌐 **Aplicación**: http://localhost:3007
- 🔧 **API Docs**: http://localhost:8000/docs
- 📊 **Backend**: http://localhost:8000

**¡Disfruta probando EvaluaTE MVP!** 🚀 