document.addEventListener('DOMContentLoaded', () => {
  const generarBtn = document.getElementById('generar-informe');
  const descargarBtn = document.getElementById('descargar-pdf');

  generarBtn.addEventListener('click', () => {
    generarInformeEmpleabilidad();
  });

  descargarBtn.addEventListener('click', () => {
    descargarInformePDF();
  });
});

function generarInformeEmpleabilidad() {
  // Recuperar datos del localStorage
  const nombre = localStorage.getItem('formulario_nombre') || 'N/A';
  const apellidos = localStorage.getItem('formulario_apellidos') || 'N/A';
  const email = localStorage.getItem('formulario_email') || 'N/A';
  const whatsapp = localStorage.getItem('formulario_whatsapp') || 'N/A';
  const discapacidad = localStorage.getItem('formulario_discapacidad') || 'N/A';
  const tipoPuesto = localStorage.getItem('formulario_tipo-puesto') || 'N/A';
  const tipoTrabajo = localStorage.getItem('formulario_tipo-trabajo') || 'N/A';
  const jornada = localStorage.getItem('formulario_jornada') || 'N/A';
  const disponibilidad = localStorage.getItem('formulario_disponibilidad') || 'N/A';
  const traslado = localStorage.getItem('formulario_traslado') || 'N/A';

  // Recuperar resultados de soft skills
  const softSkills = [
    'decisiones',
    'resolucion',
    'comunicacion',
    'adaptabilidad',
    'tiempo',
    'equipo',
    'creatividad',
    'liderazgo',
    'pensamiento',
    'emocional'
  ];

  const resultadosSoftSkills = softSkills.map(skill => {
    const score = localStorage.getItem(`minijuego_${skill}_score`);
    return { habilidad: skill.charAt(0).toUpperCase() + skill.slice(1), puntuacion: score ? parseInt(score) : null };
  });

  // Análisis de fortalezas y áreas de mejora
  const fortalezas = resultadosSoftSkills.filter(skill => skill.puntuacion !== null && skill.puntuacion >= 80);
  const areasMejora = resultadosSoftSkills.filter(skill => skill.puntuacion !== null && skill.puntuacion < 80);

  // Generar recomendaciones basadas en áreas de mejora
  const recomendaciones = areasMejora.map(area => {
    switch (area.habilidad.toLowerCase()) {
      case 'comunicacion':
        return 'Se recomienda participar en talleres de comunicación efectiva para mejorar la interacción en entornos laborales.';
      case 'liderazgo':
        return 'Considerar programas de desarrollo de liderazgo para potenciar la capacidad de dirigir equipos.';
      case 'adaptabilidad':
        return 'Trabajar en la flexibilidad cognitiva mediante ejercicios que simulen cambios en el entorno laboral.';
      default:
        return `Se sugiere desarrollar la habilidad de ${area.habilidad.toLowerCase()} mediante formación específica.`;
    }
  });

  // Crear el contenido del informe
  const informeHTML = `
    <h2>Datos Personales</h2>
    <p><strong>Nombre:</strong> ${nombre} ${apellidos}</p>
    <p><strong>Email:</strong> ${email}</p>
    <p><strong>WhatsApp:</strong> ${whatsapp}</p>
    <p><strong>Certificado de Discapacidad:</strong> ${discapacidad}</p>

    <h2>Preferencias Laborales</h2>
    <p><strong>Tipo de Puesto:</strong> ${tipoPuesto}</p>
    <p><strong>Modalidad de Trabajo:</strong> ${tipoTrabajo}</p>
    <p><strong>Jornada:</strong> ${jornada}</p>
    <p><strong>Disponibilidad:</strong> ${disponibilidad}</p>
    <p><strong>Disposición para Trasladarse:</strong> ${traslado}</p>

    <h2>Fortalezas en Soft Skills</h2>
    <ul>
      ${fortalezas.map(f => `<li>${f.habilidad}: ${f.puntuacion}</li>`).join('')}
    </ul>

    <h2>Áreas de Mejora en Soft Skills</h2>
    <ul>
      ${areasMejora.map(a => `<li>${a.habilidad}: ${a.puntuacion}</li>`).join('')}
    </ul>

    <h2>Recomendaciones</h2>
    <ul>
      ${recomendaciones.map(r => `<li>${r}</li>`).join('')}
    </ul>
  `;

  // Mostrar el informe en la página
  document.getElementById('informe-container').innerHTML = informeHTML;
}

function descargarInformePDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  const informeElement = document.getElementById('informe-container');
  const informeText = informeElement.innerText;

  doc.setFontSize(12);
  const lines = doc.splitTextToSize(informeText, 180);
  doc.text(lines, 10, 10);

  doc.save('informe_empleabilidad.pdf');
}
