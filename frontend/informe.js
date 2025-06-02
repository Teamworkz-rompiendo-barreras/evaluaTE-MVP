async function generarInformeEmpleabilidad() {
  // 1. Recoge los datos del formulario (localStorage)
  const nombre = localStorage.getItem('formulario_nombre') || '';
  const apellidos = localStorage.getItem('formulario_apellidos') || '';
  const email = localStorage.getItem('formulario_email') || '';
  const whatsapp = localStorage.getItem('formulario_whatsapp') || '';
  const cv_filename = localStorage.getItem('formulario_cv_pdf') || '';

  if (!cv_filename) {
    alert("No se ha detectado un CV cargado. Por favor vuelve a seleccionarlo.");
    return;
  }

  // 2. Prepara el JSON a enviar al backend
  const datos = { nombre, apellidos, email, whatsapp, cv_filename };

  // 3. Llama al backend FastAPI
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
      <div style="margin-top: 20px;">
        <button id="descargar-pdf">Descargar informe en PDF</button>
      </div>
    `;

    // 6. Activar descarga en PDF
    document.getElementById("descargar-pdf").addEventListener("click", function () {
      const element = document.getElementById("informe-container");
      const opt = {
        margin: 0.5,
        filename: 'Informe_Empleabilidad.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
      };
      html2pdf().from(element).set(opt).save();
    });

  } catch (error) {
    document.getElementById('informe-container').innerHTML =
      `<p style="color:red;">${error.message}</p>`;
  }
}

