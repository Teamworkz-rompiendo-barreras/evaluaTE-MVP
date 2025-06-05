// main.js

/**
 * Función para recopilar TODOS los datos almacenados en localStorage
 * (datos del formulario inicial, resultados de softskills y CV).
 */
function recogerDatosFormulario() {
  return {
    nombre: localStorage.getItem("formulario_nombre") || "",
    apellidos: localStorage.getItem("formulario_apellidos") || "",
    email: localStorage.getItem("formulario_email") || "",
    whatsapp: localStorage.getItem("formulario_whatsapp") || "",
    discapacidad: localStorage.getItem("formulario_discapacidad") || "",
    tipo: localStorage.getItem("formulario_tipo") || "",
    puesto: localStorage.getItem("formulario_tipo") || "",
    jornada: localStorage.getItem("formulario_jornada") || "",
    disponibilidad: localStorage.getItem("formulario_disponibilidad") || "",
    traslado: localStorage.getItem("formulario_traslado") || "",
    // Puntajes de cada minijuego:
    minijuego_decisiones_score:
      localStorage.getItem("minijuego_decisiones_score") || "",
    minijuego_resolucion_score:
      localStorage.getItem("minijuego_resolucion_score") || "",
    minijuego_comunicacion_score:
      localStorage.getItem("minijuego_comunicacion_score") || "",
    minijuego_adaptabilidad_score:
      localStorage.getItem("minijuego_adaptabilidad_score") || "",
    minijuego_tiempo_score:
      localStorage.getItem("minijuego_gestion_tiempo_score") || "",
    minijuego_equipo_score:
      localStorage.getItem("minijuego_trabajo_equipo_score") || "",
    minijuego_creatividad_score:
      localStorage.getItem("minijuego_creatividad_score") || "",
    minijuego_liderazgo_score:
      localStorage.getItem("minijuego_liderazgo_score") || "",
    minijuego_pensamiento_score:
      localStorage.getItem("minijuego_pensamiento_score") || "",
    minijuego_emocional_score:
      localStorage.getItem("minijuego_emocional_score") || "",
    // Nombre de archivo del CV:
    cv_filename: localStorage.getItem("cv_filename") || "",
  };
}

/**
 * Con los datos en la mano, hacemos POST a /api/generar-informe,
 * y luego pintamos en pantalla el informe con `mostrarInforme(...)`.
 */
async function generarInforme() {
  const datos = recogerDatosFormulario();

  // Si falta algún campo crítico, podríamos mostrar un alert aquí
  // pero asumimos que ya se almacenaron antes.
  if (!datos.cv_filename) {
    alert(
      "⚠️ No se encontró el nombre de tu CV. Asegúrate de haber subido tu PDF en la etapa 'Sube tu CV'."
    );
    return;
  }

  try {
    const respuesta = await fetch(
      "http://localhost:8000/api/generar-informe",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
      }
    );

    if (respuesta.ok) {
      const data = await respuesta.json();
      if (window.mostrarInforme) {
        window.mostrarInforme(data.informe);
      }
    } else {
      // Si el backend responde con un error (500, 422, etc.)
      alert("⚠️ Error al generar el informe. Por favor revisa la consola.");
      console.error("Respuesta del servidor:", await respuesta.text());
    }
  } catch (err) {
    alert(
      "❌ No se pudo conectar con el servidor. Verifica que el backend esté activo."
    );
    console.error(err);
  }
}

// Ejecutamos generarInforme() en cuanto cargue la página resultados.html
document.addEventListener("DOMContentLoaded", generarInforme);
