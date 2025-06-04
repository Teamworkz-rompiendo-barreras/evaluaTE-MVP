// main.js

/**
 * Esta función recoge TODOS los datos almacenados en localStorage:
 * - Campos del formulario (nombre, apellidos, email, etc.)
 * - Resultados de los minijuegos
 * - Texto extraído del CV ("cv_text")
 * Luego llama a POST /api/generar-informe, y pinta en pantalla las secciones
 * que el backend devuelve (resumen, fortalezas, áreas de mejora, orientación, conclusión).
 */

function recogerDatosFormulario() {
  return {
    nombre: localStorage.getItem('formulario_nombre') || '',
    apellidos: localStorage.getItem('formulario_apellidos') || '',
    email: localStorage.getItem('formulario_email') || '',
    whatsapp: localStorage.getItem('formulario_whatsapp') || '',
    discapacidad: localStorage.getItem('formulario_discapacidad') || '',
    tipo: localStorage.getItem('formulario_tipo') || '',
    puesto: localStorage.getItem('formulario_puesto') || '',
    jornada: localStorage.getItem('formulario_jornada') || '',
    disponibilidad: localStorage.getItem('formulario_disponibilidad') || '',
    traslado: localStorage.getItem('formulario_traslado') || '',
    minijuego_decisiones_score: localStorage.getItem('minijuego_decisiones_score') || '',
    minijuego_resolucion_score: localStorage.getItem('minijuego_resolucion_score') || '',
    minijuego_comunicacion_score: localStorage.getItem('minijuego_comunicacion_score') || '',
    minijuego_adaptabilidad_score: localStorage.getItem('minijuego_adaptabilidad_score') || '',
    minijuego_tiempo_score: localStorage.getItem('minijuego_tiempo_score') || '',
    minijuego_equipo_score: localStorage.getItem('minijuego_equipo_score') || '',
    minijuego_creatividad_score: localStorage.getItem('minijuego_creatividad_score') || '',
    minijuego_liderazgo_score: localStorage.getItem('minijuego_liderazgo_score') || '',
    minijuego_pensamiento_score: localStorage.getItem('minijuego_pensamiento_score') || '',
    minijuego_emocional_score: localStorage.getItem('minijuego_emocional_score') || '',
    cv_text: localStorage.getItem('cv_text') || ''
  };
}

async function generarInforme() {
  const datos = recogerDatosFormulario();

  try {
    const respuesta = await fetch('http://localhost:8000/api/generar-informe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });

    if (respuesta.ok) {
      const data = await respuesta.json();
      if (window.mostrarInforme) {
        window.mostrarInforme(data.informe);
      }
    } else {
      alert('⚠️ Error al generar el informe');
    }
  } catch (err) {
    alert('❌ No se pudo conectar con el servidor. Verifica que el backend esté activo.');
  }
}

// Al cargar la página de resultados, generamos el informe automáticamente
document.addEventListener('DOMContentLoaded', generarInforme);

/**
 * Podrías necesitar la función mostrarInforme(...) si aún no existe:
 * Por ejemplo:
 *
 * function mostrarInforme(info) {
 *   document.getElementById('informe-nombre').innerText = `${info.nombre} ${info.apellidos}`;
 *   // ... pintar todos los campos en su lugar
 * }
 *
 * Sin embargo, en este caso, la tenemos definida dentro de <script> en resultados.html.
 */
