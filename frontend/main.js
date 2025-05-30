// main.js

// Función que recoge los datos de localStorage
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
    // Resultados minijuegos
    minijuego_decisiones_score: localStorage.getItem('minijuego_decisiones_score') || '',
    minijuego_resolucion_score: localStorage.getItem('minijuego_resolucion_score') || '',
    minijuego_comunicacion_score: localStorage.getItem('minijuego_comunicacion_score') || '',
    minijuego_adaptabilidad_score: localStorage.getItem('minijuego_adaptabilidad_score') || '',
    minijuego_tiempo_score: localStorage.getItem('minijuego_tiempo_score') || '',
    minijuego_equipo_score: localStorage.getItem('minijuego_equipo_score') || '',
    minijuego_creatividad_score: localStorage.getItem('minijuego_creatividad_score') || '',
    minijuego_liderazgo_score: localStorage.getItem('minijuego_liderazgo_score') || '',
    minijuego_pensamiento_score: localStorage.getItem('minijuego_pensamiento_score') || '',
    minijuego_emocional_score: localStorage.getItem('minijuego_emocional_score') || ''
    // Si quieres añadir más campos, agrégalos aquí.
  };
}

// Función para enviar datos al backend y mostrar el informe bonito
async function enviarDatosAlBackend(datosFormulario) {
  try {
    const respuesta = await fetch('http://localhost:8000/api/generar-informe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(datosFormulario)
    });

    if (respuesta.ok) {
      const data = await respuesta.json();
      console.log("RESPUESTA JSON DEL BACKEND:", data);
      // Usa la función global que tienes definida en resultados.html
      if (window.mostrarInforme) {
        window.mostrarInforme(data.informe);
      } else {
        alert("No se encuentra la función mostrarInforme en la página.");
      }
    } else {
      alert('Error al generar el informe.');
    }
  } catch (error) {
    alert('No se pudo conectar con el servidor backend.');
  }
}

// Asigna el evento al botón "Enviar todo y ver resultados"
document.addEventListener('DOMContentLoaded', function() {
  const botonEnviar = document.getElementById('botonEnviarTodo');
  if (botonEnviar) {
    botonEnviar.addEventListener('click', function(event) {
      event.preventDefault();
      const datosFormulario = recogerDatosFormulario();
      enviarDatosAlBackend(datosFormulario);
    });
  }
});