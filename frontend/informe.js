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
    return {
      habilidad: skill.charAt(0).toUpperCase() + skill.slice(1),
      puntuacion: score ? parseInt(score) : null
    };
  });

  // Análisis de fortalezas y áreas de mejora
  const fortalezas = resultadosSoftSkills.filter(skill => skill.puntuacion !== null && skill.puntuacion >= 80);
  const areasMejora = resultadosSoftSkills.filter(skill => skill.puntuacion !== null && skill.puntuacion < 80);

  // Generar contenido del informe
  const informe = {
    datosPersonales: {
      nombreCompleto: `${nombre} ${apellidos}`,
      email,
      whatsapp,
      discapacidad
    },
    preferenciasLaborales: {
      tipoPuesto,
      tipoTrabajo,
      jornada,
      disponibilidad,
      traslado
    },
    analisisSoftSkills: {
      fortalezas,
      areasMejora
    },
    recomendaciones: []
  };

  // Generar recomendaciones basadas en áreas de mejora
  areasMejora.forEach(area => {
    switch (area.habilidad.toLowerCase()) {
      case 'comunicacion':
        informe.recomendaciones.push('Se recomienda participar en talleres de comunicación efectiva para mejorar la interacción en entornos laborales.');
        break;
      case 'liderazgo':
        informe.recomendaciones.push('Considerar programas de desarrollo de liderazgo para potenciar la capacidad de dirigir equipos.');
        break;
      case 'adaptabilidad':
        informe.recomendaciones.push('Trabajar en la flexibilidad cognitiva mediante ejercicios que simulen cambios en el entorno laboral.');
        break;
      // Agregar más casos según sea necesario
      default:
        informe.recomendaciones.push(`Se sugiere desarrollar la habilidad de ${area.habilidad.toLowerCase()} mediante formación específica.`);
        break;
    }
  });

  // Retornar el informe generado
  return informe;
}