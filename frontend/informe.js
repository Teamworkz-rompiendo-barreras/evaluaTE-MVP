async function generarInformeEmpleabilidad() {
  // 1. Recoge los datos del formulario (localStorage)
  const nombre = localStorage.getItem('formulario_nombre') || '';
  const apellidos = localStorage.getItem('formulario_apellidos') || '';
  const email = localStorage.getItem('formulario_email') || '';
  const whatsapp = localStorage.getItem('formulario_whatsapp') || '';

  // 2. Prepara el JSON a enviar al backend
  const datos = { nombre, apellidos, email, whatsapp };

  // 3. Llama al backend FastAPI (ajusta la URL si usas otro puerto)
  try {
    const response = await fetch('http://localhost:8000/api/generar-informe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });

    if (!response.ok) throw new Error('Error al generar el informe');

    // 4. El backend devuelve el informe (como JSON)
    const data = await response.json();
    const informe = data.informe;

    // 5. Muestra el informe en pantalla
    document.getElementById('informe-container').innerHTML = `
      <h2>Informe de Empleabilidad</h2>
      <p><strong>Nombre:</strong> ${informe.nombre}</p>
      <p><strong>Apellidos:</strong> ${informe.apellidos}</p>
      <p><strong>Email:</strong> ${informe.email}</p>
      <p><strong>WhatsApp:</strong> ${informe.whatsapp}</p>
      <h3>Resumen</h3>
      <p>${informe.resumen}</p>
      <h3>Fortalezas</h3>
      <ul>${informe.fortalezas.map(f => `<li>${f}</li>`).join('')}</ul>
      <h3>Áreas de mejora</h3>
      <ul>${informe.areas_mejora.map(a => `<li>${a}</li>`).join('')}</ul>
      <h3>Orientación laboral</h3>
      <p>${informe.orientacion}</p>
      <h3>Conclusión</h3>
      <p>${informe.conclusion}</p>
    `;
  } catch (error) {
    document.getElementById('informe-container').innerHTML = `<p style="color:red;">${error.message}</p>`;
  }
}
