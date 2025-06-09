/* softskills.js: Motor de los 10 minijuegos de Soft Skills */

document.addEventListener("DOMContentLoaded", () => {
  // Índices de juego y escena
  let indiceJuego = 0;
  let indiceEscena = 0;

  // Cargar progreso previo si existe
  const progreso = JSON.parse(localStorage.getItem('softskills_progress'));
  if (progreso) ({ indiceJuego, indiceEscena } = progreso);

  // Definición de los minijuegos (primeros 3 completados)
  const juegos = [
    {
      id: 'decision',
      titulo: 'Primera llamada del día',
      descripcion: 'Hoy es tu primer día en la empresa y suena el teléfono en recepción.',
      escenas: [
        { texto: 'Suena el teléfono. Una persona pregunta por tu compañer@ de área.', opciones: [ { texto: 'Tomo nota y le digo que espere para pasarlo.', valor: 3 }, { texto: 'Intento ayudar aunque no conozco el tema.', valor: 2 }, { texto: 'Le pido que llame más tarde.', valor: 1 } ] },
        { texto: 'Te piden una tarea urgente, pero tu compañero está en reunión.', opciones: [ { texto: 'Anotas los detalles y se lo envías después.', valor: 3 }, { texto: 'Intentas resolverlo sin saber cómo.', valor: 2 }, { texto: 'Dices que no puedes hacerlo.', valor: 1 } ] },
        { texto: 'Tu supervisora solicita un informe rápido.', opciones: [ { texto: 'Preguntas los datos necesarios antes.', valor: 3 }, { texto: 'Lo haces sin confirmar todo.', valor: 2 }, { texto: 'Demoras porque no sabes qué poner.', valor: 1 } ] },
        { texto: 'Cambio de plan a última hora en la reunión.', opciones: [ { texto: 'Adapto mi agenda y confirmo.', valor: 3 }, { texto: 'Me confundo con las tareas.', valor: 2 }, { texto: 'No asisto a la nueva hora.', valor: 1 } ] },
        { texto: 'Un cliente llama y pide atención inmediata.', opciones: [ { texto: 'Le ofreces ayuda y tomas el caso.', valor: 3 }, { texto: 'Lo derivas sin más.', valor: 2 }, { texto: 'Le indicas que intente mañana.', valor: 1 } ] }
      ]
    },
    {
      id: 'resolucion',
      titulo: 'Algo no cuadra',
      descripcion: 'Te han asignado revisar pedidos y notas que hay un error.',
      escenas: [
        { texto: 'Encuentras un pedido duplicado en el sistema.', opciones: [ { texto: 'Lo reporto al supervisor.', valor: 3 }, { texto: 'Lo corrijo sin avisar.', valor: 2 }, { texto: 'Lo dejo igual.', valor: 1 } ] },
        { texto: 'Detectas falta de stock antes de enviar un pedido.', opciones: [ { texto: 'Comunicas y buscas alternativa.', valor: 3 }, { texto: 'Lo envías incompleto.', valor: 2 }, { texto: 'Ignoras el faltante.', valor: 1 } ] },
        { texto: 'Se rompe una máquina clave en producción.', opciones: [ { texto: 'Organizas soporte técnico.', valor: 3 }, { texto: 'Intentas arreglarla sin saber.', valor: 2 }, { texto: 'Cancelas la producción.', valor: 1 } ] },
        { texto: 'Hay un fallo en la base de datos que impide facturar.', opciones: [ { texto: 'Elevas el incidente al área TI.', valor: 3 }, { texto: 'Reinicias el sistema sin protocolo.', valor: 2 }, { texto: 'No facturas.', valor: 1 } ] },
        { texto: 'Un compañero solicita ayuda con un error que no entiendes.', opciones: [ { texto: 'Investigas y le explicas.', valor: 3 }, { texto: 'Le das una solución genérica.', valor: 2 }, { texto: 'Le dices que pregunte a otro.', valor: 1 } ] }
      ]
    },
    {
      id: 'comunicacion',
      titulo: 'Mensaje importante',
      descripcion: 'Debes transmitir información crucial al equipo.',
      escenas: [
        { texto: 'Recibes un email con instrucciones urgentes.', opciones: [ { texto: 'Respondes confirmando que lo has leído.', valor: 3 }, { texto: 'Lo lees pero no contestas.', valor: 2 }, { texto: 'No revisas el email.', valor: 1 } ] },
        { texto: 'Tienes que presentar un informe oral.', opciones: [ { texto: 'Preparo notas claras y practico.', valor: 3 }, { texto: 'Improviso sin preparación.', valor: 2 }, { texto: 'No presento.', valor: 1 } ] },
        { texto: 'El canal de chat está saturado de mensajes.', opciones: [ { texto: 'Organizo un resumen para el equipo.', valor: 3 }, { texto: 'Respondo solo al canal principal.', valor: 2 }, { texto: 'Ignoro mensajes.', valor: 1 } ] },
        { texto: 'Debes explicar un proceso complejo a un novato.', opciones: [ { texto: 'Uso ejemplos sencillos y gráficos.', valor: 3 }, { texto: 'Le paso un documento técnico.', valor: 2 }, { texto: 'Le indico que busque en internet.', valor: 1 } ] },
        { texto: 'Hay un malentendido en un correo grupal.', opciones: [ { texto: 'Aclaro todo en respuesta grupal.', valor: 3 }, { texto: 'Envió un mensaje privado.', valor: 2 }, { texto: 'Dejo que siga.', valor: 1 } ] }
      ]
    }
    // … Añadir los restantes 7 juegos …
  ];

  // Cálculo y persistencia de scores
  const scores = JSON.parse(localStorage.getItem('softskills_scores') || '{}');

  // Elementos básicos del DOM
  const contenedor = document.getElementById('evaluacion-softskills');
  const introBox = document.createElement('section');
  const preguntaBox = document.createElement('section');
  const opcionesBox = document.createElement('section');
  const contadorBox = document.createElement('div');
  const botonNext = document.createElement('button');

  // Atributos de accesibilidad
  introBox.setAttribute('role', 'region');
  introBox.setAttribute('aria-labelledby', 'intro-titulo');
  botonNext.setAttribute('aria-label', 'Siguiente');

  // Inyectar en el DOM
  contenedor.append(introBox, preguntaBox, opcionesBox, contadorBox, botonNext);

  // Renderizado según estado
  function render() {
    if (indiceJuego >= juegos.length) {
      return window.location.href = 'subircv.html';
    }
    const juego = juegos[indiceJuego];
    if (indiceEscena === 0) return showIntro(juego);
    showEscena(juego);
  }

  function showIntro(juego) {
    introBox.innerHTML = `<h2 id="intro-titulo">${juego.titulo}</h2><p>${juego.descripcion}</p>`;
    preguntaBox.hidden = opcionesBox.hidden = contadorBox.hidden = true;
    botonNext.textContent = 'Comenzar';
    botonNext.onclick = () => { indiceEscena = 1; saveProgress(); render(); };
  }

  function showEscena(juego) {
    const escena = juego.escenas[indiceEscena - 1];
    introBox.hidden = true;
    preguntaBox.hidden = false;
    opcionesBox.hidden = false;
    contadorBox.hidden = false;

    preguntaBox.innerHTML = `<p>${escena.texto}</p>`;
    opcionesBox.innerHTML = '';
    escena.opciones.forEach(opt => {
      const btn = document.createElement('button');
      btn.textContent = opt.texto;
      btn.onclick = () => selectOption(opt.valor);
      opcionesBox.appendChild(btn);
    });
    contadorBox.textContent = `Pregunta ${indiceEscena} de ${juego.escenas.length}`;
    botonNext.textContent = 'Siguiente';
    botonNext.onclick = null;
  }

  function selectOption(valor) {
    scores[juegos[indiceJuego].id] = scores[juegos[indiceJuego].id] || [];
    scores[juegos[indiceJuego].id].push(valor);
    if (indiceEscena < juegos[indiceJuego].escenas.length) {
      indiceEscena++;
      saveProgress(); render();
    } else finalizeGame();
  }

  function finalizeGame() {
    const arr = scores[juegos[indiceJuego].id];
    const media = Math.round(arr.reduce((a,b) => a+b,0)/arr.length);
    scores[juegos[indiceJuego].id] = media;
    localStorage.setItem('softskills_scores', JSON.stringify(scores));

    introBox.hidden = false;
    introBox.innerHTML = `<h2>¡Bien hecho!</h2><p>Has completado "${juegos[indiceJuego].titulo}".</p>`;
    preguntaBox.hidden = opcionesBox.hidden = contadorBox.hidden = true;
    botonNext.textContent = 'Siguiente juego';
    botonNext.onclick = () => { indiceEscena = 0; indiceJuego++; saveProgress(); render(); };
  }

  function saveProgress() {
    localStorage.setItem('softskills_progress', JSON.stringify({ indiceJuego, indiceEscena }));
  }

  // Atajos de teclado
  document.addEventListener('keydown', e => {
    if (e.key === 'PageDown' || e.key === 'ArrowRight') botonNext.click();
    if (e.key === 'PageUp' || e.key === 'ArrowLeft') {
      if (indiceEscena > 1) indiceEscena--;
      else if (indiceJuego > 0) { indiceJuego--; indiceEscena = juegos[indiceJuego].escenas.length; }
      saveProgress(); render();
    }
  });

  // Iniciar flujo
  render();
});
