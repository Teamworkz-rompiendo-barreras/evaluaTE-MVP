// softskills.js

// Lista de preguntas / habilidades a evaluar
const preguntas = [
  {
    habilidad: "decisiones",
    texto: "Cuando hay que tomar una decisión importante en el trabajo, yo...",
    opciones: [
      { texto: "Pido ayuda y analizo las opciones antes de decidir.", valor: 3 },
      { texto: "Decido rápido, sin pensar demasiado.", valor: 1 },
      { texto: "Me cuesta decidir y suelo postergar.", valor: 2 }
    ]
  },
  {
    habilidad: "resolucion",
    texto: "Si aparece un problema inesperado, yo...",
    opciones: [
      { texto: "Busco soluciones y pruebo alternativas.", valor: 3 },
      { texto: "Espero a que alguien me diga qué hacer.", valor: 1 },
      { texto: "Intento solucionarlo aunque me estrese.", valor: 2 }
    ]
  },
  {
    habilidad: "comunicacion",
    texto: "Cuando tengo que explicar algo a otras personas...",
    opciones: [
      { texto: "Uso ejemplos o dibujos si hace falta.", valor: 3 },
      { texto: "Explico con pocas palabras aunque no se entienda bien.", valor: 2 },
      { texto: "Evito explicar y prefiero que lo haga otra persona.", valor: 1 }
    ]
  },
  {
    habilidad: "adaptabilidad",
    texto: "Si hay cambios en el trabajo, yo...",
    opciones: [
      { texto: "Me adapto y busco cómo trabajar con el nuevo sistema.", valor: 3 },
      { texto: "Intento adaptarme pero me cuesta.", valor: 2 },
      { texto: "Me siento incómodo y me bloqueo.", valor: 1 }
    ]
  },
  {
    habilidad: "gestion_tiempo",
    texto: "En cuanto al uso del tiempo durante la jornada...",
    opciones: [
      { texto: "Organizo mi tiempo y cumplo con los plazos.", valor: 3 },
      { texto: "Trabajo a mi ritmo aunque a veces me retraso.", valor: 2 },
      { texto: "Pierdo tiempo con facilidad y me cuesta organizarme.", valor: 1 }
    ]
  },
  {
    habilidad: "trabajo_equipo",
    texto: "Cuando trabajo con otras personas...",
    opciones: [
      { texto: "Colaboro, doy ideas y respeto las opiniones.", valor: 3 },
      { texto: "Colaboro si me lo piden, pero prefiero trabajar a solas.", valor: 2 },
      { texto: "Evito trabajar con otras personas siempre que puedo.", valor: 1 }
    ]
  },
  {
    habilidad: "creatividad",
    texto: "Ante una tarea nueva o difícil, yo...",
    opciones: [
      { texto: "Propongo ideas diferentes y creativas.", valor: 3 },
      { texto: "Intento seguir ejemplos anteriores.", valor: 2 },
      { texto: "Me limito a repetir lo que ya sé hacer.", valor: 1 }
    ]
  },
  {
    habilidad: "liderazgo",
    texto: "En grupo, cuando hay que organizar o coordinar...",
    opciones: [
      { texto: "Propongo ideas y ayudo a organizar al grupo.", valor: 3 },
      { texto: "Participo pero no suelo tomar la iniciativa.", valor: 2 },
      { texto: "Prefiero que otra persona decida y organice.", valor: 1 }
    ]
  },
  {
    habilidad: "pensamiento",
    texto: "Cuando recibo nueva información...",
    opciones: [
      { texto: "La analizo y contrasto antes de aceptarla.", valor: 3 },
      { texto: "La acepto si me la dice alguien de confianza.", valor: 2 },
      { texto: "No suelo cuestionarla, simplemente la acepto.", valor: 1 }
    ]
  },
  {
    habilidad: "emocional",
    texto: "Cuando tengo un mal día en el trabajo...",
    opciones: [
      { texto: "Intento calmarme y sigo con mis tareas.", valor: 3 },
      { texto: "Me cuesta concentrarme pero lo intento.", valor: 2 },
      { texto: "Me bloqueo o discuto fácilmente.", valor: 1 }
    ]
  }
];

let indice = 0;
const respuestas = {};

const preguntaTexto = document.getElementById("pregunta-texto");
const opcionesContenedor = document.getElementById("opciones-contenedor");
const contador = document.getElementById("contador");
const barraProgreso = document.getElementById("barra-progreso");

// Muestra la pregunta actual y sus botones
function mostrarPregunta() {
  const actual = preguntas[indice];
  preguntaTexto.innerText = actual.texto;

  opcionesContenedor.innerHTML = "";
  actual.opciones.forEach((opcion) => {
    const boton = document.createElement("button");
    boton.innerText = opcion.texto;
    boton.className = "opcion";
    boton.addEventListener("click", () => {
      respuestas[`minijuego_${actual.habilidad}_score`] = opcion.valor;
      siguientePregunta();
    });
    opcionesContenedor.appendChild(boton);
  });

  contador.innerText = `Pregunta ${indice + 1} de ${preguntas.length}`;
  barraProgreso.style.width = `${((indice + 1) / preguntas.length) * 100}%`;
}

function siguientePregunta() {
  indice++;
  if (indice < preguntas.length) {
    mostrarPregunta();
  } else {
    // Llegamos al final: guardamos todas las puntuaciones en localStorage
    Object.keys(respuestas).forEach((key) => {
      localStorage.setItem(key, respuestas[key]);
    });
    // Redirigimos a la siguiente etapa: subir CV
    window.location.href = "subircv.html";
  }
}

// Iniciar al cargar
mostrarPregunta();
