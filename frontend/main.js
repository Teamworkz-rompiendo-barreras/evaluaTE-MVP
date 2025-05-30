async function enviarDatosAlBackend(datosFormulario) {
  const respuesta = await fetch('http://localhost:8000/api/generar-informe', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(datosFormulario)
  });

  if (respuesta.ok) {
    const data = await respuesta.json();
    mostrarInforme(data.informe); // Aquí muestras el informe en pantalla
  } else {
    alert('Error al generar el informe.');
  }
}