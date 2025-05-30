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

// Función para enviar datos al backend y mostrar el informe
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
      mostrarInforme(data.informe); // Aquí mostramos el informe
      // Si quieres redirigir a otra página tras recibir el informe, descomenta la línea siguiente:
      // window.location.href = 'resultados.html';
    } else {
      alert('Error al generar el informe.');
    }
  } catch (error) {
    alert('No se pudo conectar con el servidor backend.');
  }
}

// Muestra el informe en pantalla
function mostrarInforme(textoInforme) {
  const resultadoDiv = document.getElementById('resultadoInforme');
  if (resultadoDiv) {
    resultadoDiv.innerText = textoInforme;
  } else {
    alert('No se encontró el área para mostrar el informe.');
  }
}

// Asigna el evento al botón "Enviar todo y ver resultados"
document.addEventListener('DOMContentLoaded', function() {
  const botonEnviar = document.getElementById('botonEnviarTodo');
  if (botonEnviar) {
    botonEnviar.addEventListener('click', function(event) {
      event.preventDefault();

      // Recoge los datos de localStorage y crea el objeto con los datos del formulario y minijuegos
      const datosFormulario = recogerDatosFormulario();

      // Enviar los datos al backend para generar el informe
      enviarDatosAlBackend(datosFormulario);
    });
  }
});