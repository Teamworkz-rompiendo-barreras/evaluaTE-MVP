// frontend/main.js

/**
 * Función para tomar los campos del formulario (guardados en localStorage),
 * los 10 scores de los minijuegos y el cv_text, y devolver un objeto listo
 * para enviar al backend.
 */
function recogerDatosFormulario() {
  return {
    nombre: localStorage.getItem("nombre") || "",
    apellidos: localStorage.getItem("apellidos") || "",
    email: localStorage.getItem("email") || "",
    whatsapp: localStorage.getItem("whatsapp") || "",
    discapacidad: localStorage.getItem("discapacidad") || "",
    tipo: localStorage.getItem("tipo-puesto") || "",
    puesto: localStorage.getItem("tipo-puesto") || "",
    jornada: localStorage.getItem("jornada") || "",
    disponibilidad: localStorage.getItem("disponibilidad") || "",
    traslado: localStorage.getItem("traslado") || "",
    cv_text: localStorage.getItem("cv_text") || "",
    // Convertir a enteros:
    decision_score: parseInt(localStorage.getItem("decision_score") || "0", 10),
    resolucion_score: parseInt(localStorage.getItem("resolucion_score") || "0", 10),
    comunicacion_score: parseInt(localStorage.getItem("comunicacion_score") || "0", 10),
    adaptabilidad_score: parseInt(localStorage.getItem("adaptabilidad_score") || "0", 10),
    tiempo_score: parseInt(localStorage.getItem("tiempo_score") || "0", 10),
    equipo_score: parseInt(localStorage.getItem("equipo_score") || "0", 10),
    creatividad_score: parseInt(localStorage.getItem("creatividad_score") || "0", 10),
    liderazgo_score: parseInt(localStorage.getItem("liderazgo_score") || "0", 10),
    pensamiento_score: parseInt(localStorage.getItem("pensamiento_score") || "0", 10),
    emocional_score: parseInt(localStorage.getItem("emocional_score") || "0", 10),
  };
}

/**
 * Función principal: hace un POST a /api/generar-informe, recibiendo
 * un JSON con toda la información. Luego pinta el informe en pantalla
 * e inicia el radar chart.
 */
async function generarInforme() {
  const datos = recogerDatosFormulario();
  // Asegurarnos de que no hay nulos:
  if (
    !datos.nombre.trim() ||
    !datos.apellidos.trim() ||
    (!datos.email.trim() && !datos.whatsapp.trim()) ||
    !datos["discapacidad"] ||
    !datos["tipo"] ||
    !datos["puesto"] ||
    !datos["jornada"] ||
    !datos["cv_text"] ||
    Object.values(datos).slice(-10).every(val => val === 0)
  ) {
    alert("Falta información obligatoria para generar el informe.");
    return;
  }

  try {
    const respuesta = await fetch("http://localhost:8000/api/generar-informe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    });
    if (!respuesta.ok) {
      alert("⚠️ Error al generar el informe: " + respuesta.statusText);
      return;
    }
    const data = await respuesta.json();
    const info = data.informe;
    if (window.mostrarInforme) {
      window.mostrarInforme(info);
    }
  } catch (err) {
    console.error(err);
    alert("❌ No se pudo conectar con el servidor. Verifica que el backend esté activo.");
  }
}

// Esperar a que cargue la página para llamar a generarInforme()
document.addEventListener("DOMContentLoaded", generarInforme);

/**
 * Función que recibe el objeto `info` y rellena cada parte de la página:
 *  - Datos personales
 *  - Radar chart (Chart.js)
 *  - Resumen, fortalezas, áreas de mejora, orientación, conclusión
 */
function mostrarInforme(info) {
  // 1) Datos personales
  document.getElementById("informe-nombre").innerText = `${info.nombre} ${info.apellidos}`;
  document.getElementById("informe-email").innerText = info.email;
  document.getElementById("informe-whatsapp").innerText = info.whatsapp;
  document.getElementById("informe-jornada").innerText = info.jornada;
  document.getElementById("informe-disponibilidad").innerText = info.disponibilidad;
  document.getElementById("informe-discapacidad").innerText = info.discapacidad;
  document.getElementById("informe-tipo").innerText = info.tipo;
  document.getElementById("informe-puesto").innerText = info.puesto;

  // 2) Radar Chart con Chart.js
  const ctx = document.getElementById("radarChart").getContext("2d");
  const labels = Object.keys(info.scores);
  const valores = Object.values(info.scores);

  new Chart(ctx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Nivel de soft skills (1–3)",
          data: valores,
          backgroundColor: "rgba(59, 113, 243, 0.2)",    // semitransparente azul
          borderColor: "#374BA6",                        // color principal Teamworkz
          pointBackgroundColor: "#F2D680",               // color secundario Teamworkz
          pointBorderColor: "#374BA6",
          pointHoverBackgroundColor: "#374BA6"
        }
      ]
    },
    options: {
      scales: {
        r: {
          beginAtZero: true,
          min: 0,
          max: 3,
          ticks: {
            stepSize: 1
          },
          pointLabels: {
            font: {
              size: 14
            },
            color: "#0B474B"
          },
          grid: {
            color: "#ccc"
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });

  // 3) Texto del resumen
  document.getElementById("texto-resumen").innerText = info.resumen || "";

  // 4) Fortalezas (lista)
  const ulFort = document.getElementById("informe-fortalezas");
  ulFort.innerHTML = "";
  (info.fortalezas || []).forEach(item => {
    const li = document.createElement("li");
    li.innerText = item;
    ulFort.appendChild(li);
  });

  // 5) Áreas de mejora (lista)
  const ulMej = document.getElementById("informe-mejoras");
  ulMej.innerHTML = "";
  (info.areas_mejora || []).forEach(item => {
    const li = document.createElement("li");
    li.innerText = item;
    ulMej.appendChild(li);
  });

  // 6) Orientación
  document.getElementById("informe-orientacion").innerText = info.orientacion || "";

  // 7) Conclusión
  document.getElementById("informe-conclusion").innerText = info.conclusion || "";

  // 8) Botón PDF
  document.getElementById("descargar-pdf").addEventListener("click", () => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF("p", "pt", "a4");
    const informeDiv = document.getElementById("informe-wrapper");
    doc.html(informeDiv, {
      callback: function (doc) {
        doc.save("informe-empleabilidad.pdf");
      },
      margin: [20, 20, 20, 20],
      x: 10,
      y: 10,
      width: 560,
      windowWidth: 800
    });
  });
}
