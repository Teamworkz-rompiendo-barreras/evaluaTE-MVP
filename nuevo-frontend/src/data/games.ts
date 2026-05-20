import { Game, GameProgress } from '../types/game';

export const games: Game[] = [
  {
    id: 'decision-making',
    title: 'Toma de decisiones',
    subtitle: 'Día 1',
    description: 'Tu primer día en IntegraPro. Tendrás que tomar decisiones en situaciones reales del trabajo.',
    softSkill: 'Toma de decisiones',
    day: 'Lunes',
    scenario: 'Primer día en un puesto de apoyo en una empresa de logística',
    icon: '📞',
    color: '#F2D680',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Te asignan tres tareas para empezar: archivar documentos, ayudar a una compañera con un informe, o revisar materiales nuevos.',
        type: 'choice',
        options: [
          { id: 'archivar', text: 'Archivas documentos porque te resulta sencillo. 🗄️', score: 50 },
          { id: 'ayudar', text: 'Ayudas a tu compañera, así os conocéis y colaboras. 🧑‍🤝‍🧑', score: 100 },
          { id: 'revisar', text: 'Revisas materiales nuevos porque te apetece aprender algo distinto. 🔍', score: 20 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Te proponen ir a una reunión o acabar una tarea pendiente.',
        type: 'choice',
        options: [
          { id: 'reunion', text: 'Prefieres ir a la reunión, aunque la tarea espere. 📅', score: 20 },
          { id: 'tarea', text: 'Terminas la tarea antes y luego, si puedes, vas a la reunión. ☑️', score: 100 },
          { id: 'ayuda', text: 'Pides ayuda para decidir porque ambas cosas parecen importantes. ✋', score: 50 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Llega un cliente con una petición urgente.',
        type: 'choice',
        options: [
          { id: 'compañero', text: 'Buscas a otra persona del equipo para que le atienda mientras tú acabas lo tuyo. 👥', score: 20 },
          { id: 'esperar', text: 'Le dices que le ayudas en cuanto termines lo que tienes. ⏰', score: 50 },
          { id: 'atender', text: 'Le atiendes enseguida, aunque dejes tu tarea a medias. 🧑', score: 100 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Hay un problema técnico con la impresora.',
        type: 'choice',
        options: [
          { id: 'solucionar', text: 'Lo intentas solucionar por tus medios. 🛠️', score: 100 },
          { id: 'mantenimiento', text: 'Buscas a alguien de mantenimiento. ☎️', score: 50 },
          { id: 'otra', text: 'Propones usar otra impresora y avisar después. 🖨️➡️', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Tu responsable te pide opinión para organizar una actividad.',
        type: 'choice',
        options: [
          { id: 'opinion', text: 'Das tu opinión, aunque no lo tengas muy claro. 💬', score: 100 },
          { id: 'no-opinar', text: 'Prefieres no opinar hasta tener más información. 📖', score: 20 },
          { id: 'preguntar', text: 'Preguntas antes a los demás miembros de la empresa. 👥', score: 50 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Excelente trabajo!',
        description: '¡Felicidades! Has completado exitosamente el primer minijuego. ¡Sigue así!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'analytical-thinking',
    title: 'Pensamiento Analítico',
    subtitle: 'Día 2',
    description: 'Hoy te piden analizar información, detectar problemas y organizar materiales.',
    softSkill: 'Pensamiento analítico',
    day: 'Martes',
    scenario: 'Segundo día en IntegraPro. Analizas información y resuelves problemas.',
    icon: '📊',
    color: '#A6D1F2',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Te entregan una lista de tareas con plazos distintos.',
        type: 'choice',
        options: [
          { id: 'calendario', text: 'Ordenas las tareas según la fecha de entrega. 📅', score: 100 },
          { id: 'facil', text: 'Haces las que te parecen más fáciles primero. 👍', score: 20 },
          { id: 'ayuda', text: 'Pides ayuda para organizarte. ✋', score: 50 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Encuentras un error en unos datos.',
        type: 'choice',
        options: [
          { id: 'lupa', text: 'Lo revisas y buscas dónde está el fallo. 🔍', score: 100 },
          { id: 'bocadillo', text: 'Informas del error pero dejas que lo revise otra persona. 💬', score: 50 },
          { id: 'interrogacion', text: 'Sigues adelante sin avisar. Puede que ya lo sepan. ❓', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Te dan instrucciones poco claras para un trabajo.',
        type: 'choice',
        options: [
          { id: 'grupo', text: 'Esperas a ver qué hacen los demás. 👥', score: 50 },
          { id: 'pregunta', text: 'Pides aclaraciones hasta entenderlo. ❔', score: 100 },
          { id: 'ojo', text: 'Haces lo que crees que piden aunque tengas alguna duda. 👁️', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Te piden que agrupes materiales similares.',
        type: 'choice',
        options: [
          { id: 'clasificacion', text: 'Analizas bien las características y creas grupos lógicos. 🗂️', score: 100 },
          { id: 'colores', text: 'Agrupas por colores o tamaño. 🎨', score: 20 },
          { id: 'ejemplo', text: 'Pides que te muestren un ejemplo antes. ✋', score: 50 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Te dan dos soluciones para un problema.',
        type: 'choice',
        options: [
          { id: 'dedo', text: 'Eliges la que te suena mejor. ☝️', score: 20 },
          { id: 'responsable', text: 'Pides la opinión del responsable antes de decidir. 👔', score: 50 },
          { id: 'balanza', text: 'Comparas ventajas e inconvenientes de cada opción. ⚖️', score: 100 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Muy bien!',
        description: '¡Felicidades! Has completado exitosamente este minijuego. ¡Lo estás haciendo muy bien!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'creativity',
    title: 'Creatividad',
    subtitle: 'Día 3',
    description: 'Hoy te toca aportar ideas y buscar nuevas formas de resolver problemas.',
    softSkill: 'Creatividad',
    day: 'Miércoles',
    scenario: 'Tercer día en IntegraPro. Es momento de innovar y proponer ideas.',
    icon: '💡',
    color: '#F2B6A6',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Surge un problema nuevo en el almacén/oficina.',
        type: 'choice',
        options: [
          { id: 'check', text: 'Aplicas una solución que ya se ha hecho antes. ✔️', score: 50 },
          { id: 'bombilla', text: 'Propones una idea original para resolverlo. 💡', score: 100 },
          { id: 'reloj', text: 'Esperas instrucciones para actuar. ⏰', score: 20 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Hay que decorar una zona para un evento.',
        type: 'choice',
        options: [
          { id: 'grupo', text: 'Pides ideas a los demás empleados. 👥', score: 50 },
          { id: 'pincel', text: 'Propones algo diferente y creativo. 🖌️', score: 100 },
          { id: 'repeticion', text: 'Repites la decoración de siempre. 🔁', score: 20 }
        
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Falta material de oficina y hay que improvisar.',
        type: 'choice',
        options: [
          { id: 'herramientas', text: 'Buscas un objeto alternativo para salir del paso. 🧰', score: 100 },
          { id: 'espera', text: 'Esperas a que lo repongan para seguir trabajando. ⏳', score: 20 },
          { id: 'manos', text: 'Usas lo que tienes aunque no sea perfecto. 👐', score: 50 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'El equipo se atasca en una reunión.',
        type: 'choice',
        options: [
          { id: 'flecha', text: 'Sugieres cambiar la forma de pensar para ver nuevas soluciones. 🔄', score: 100 },
          { id: 'oido', text: 'Te limitas a escuchar. 👂', score: 20 },
          { id: 'bloc', text: 'Intentas resumir lo que se ha dicho. 🗒️', score: 50 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Te piden ideas para mejorar el ambiente en el trabajo.',
        type: 'choice',
        options: [
          { id: 'bocadillo', text: 'Preguntas qué le gustaría a los demás. 💬', score: 50 },
          { id: 'ok', text: 'Dices que está bien como está. 👍', score: 20 },
          { id: 'fiesta', text: 'Propones una actividad distinta y divertida. 🎉', score: 100 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Fantástico!',
        description: '¡Enhorabuena! Has completado el tercer minijuego. ¡Eres imparable!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'social-influence',
    title: 'Influencia Social',
    subtitle: 'Día 4',
    description: 'Hoy tienes que interactuar, motivar, convencer y resolver desacuerdos.',
    softSkill: 'Influencia social',
    day: 'Jueves',
    scenario: 'Cuarto día en IntegraPro. Interactúas y resuelves desacuerdos en el equipo.',
    icon: '🤝',
    color: '#F2E2A6',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Un miembro del equipo está sin motivación para trabajar.',
        type: 'choice',
        options: [
          { id: 'corazon', text: 'Le animas y le propones apoyaros mutuamente. ❤️', score: 100 },
          { id: 'mano', text: 'Le dices que cada cual tiene que hacer su trabajo. ✋', score: 20 },
          { id: 'oido', text: 'Le escuchas y le ofreces ayuda si la necesita. 👂', score: 50 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Debes explicar una idea nueva al equipo.',
        type: 'choice',
        options: [
          { id: 'megafono', text: 'Argumentas con ejemplos y entusiasmo. 📣', score: 100 },
          { id: 'documento', text: 'Lo explicas de forma breve y a regañadientes. 📄', score: 50 },
          { id: 'persona', text: 'Prefieres que lo explique otra persona. 👤', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Hay un desacuerdo sobre una tarea.',
        type: 'choice',
        options: [
          { id: 'manos', text: 'Propones un acuerdo intermedio para resolverlo. 🤝', score: 100 },
          { id: 'corbata', text: 'Preguntas a una persona responsable para que decida. 👔', score: 50 },
          { id: 'puno', text: 'Te mantienes en tu posición y no cedes. ✊', score: 20 }
        ],  
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Debes pedir ayuda a alguien que está haciendo otra tarea',
        type: 'choice',
        options: [
          { id: 'bocadillo', text: 'Explicas claramente por qué necesitas ayuda. 💬', score: 100 },
          { id: 'reloj', text: 'Esperas a que esté libre aunque tardes más. ⏰', score: 50 },
          { id: 'solo', text: 'No le pides ayuda para no molestar. 🧑‍🦰', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Tienes una buena idea y quieres que te apoyen.',
        type: 'choice',
        options: [
          { id: 'susurro', text: 'Se lo cuentas solo a una persona de confianza. 🤫', score: 50 },
          { id: 'grupo-estrella', text: 'Buscas a varias personas a las que les guste la idea y explicas los beneficios para el equipo. 🌟', score: 100 },
          { id: 'puerta', text: 'Esperas a que surja la oportunidad. 🚪', score: 20 }        
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Excelente!',
        description: '¡Felicidades! Has completado un nuevo minijuego. ¡Que el ritmo no pare!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'curiosity-learning',
    title: 'Curiosidad y Aprendizaje',
    subtitle: 'Día 5',
    description: 'Hoy tienes oportunidad de aprender algo nuevo o mejorar.',
    softSkill: 'Curiosidad y aprendizaje',
    day: 'Viernes',
    scenario: 'Quinto día en IntegraPro. Se presentan oportunidades para aprender y mejorar.',
    icon: '📚',
    color: '#A6F2C2',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Te ofrecen apuntarte a una formación voluntaria.',
        type: 'choice',
        options: [
          { id: 'agenda-cerrada', text: 'Prefieres no apuntarte. 📔', score: 20 },
          { id: 'libro-abierto', text: 'Aceptas y te apuntas enseguida. 📖', score: 100 },
          { id: 'grupo', text: 'Preguntas a los demás antes de decidir. 👥', score: 50 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Te cambian una tarea y tienes que aprender a usar una herramienta nueva.',
        type: 'choice',
        options: [
          { id: 'pantalla-play', text: 'Buscas tutoriales o manuales para aprender por tu cuenta. ▶️', score: 100 },
          { id: 'persona-explicando', text: 'Pides a alguien que te lo explique todo antes de empezar. 🧑‍🏫', score: 50 },
          { id: 'brazos-cruzados', text: 'Te frustras y prefieres que te lo asignen a otra persona. 🙅‍♂️', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Escuchas una conversación sobre un tema que no conoces.',
        type: 'choice',
        options: [
          { id: 'interrogacion', text: 'Preguntas y muestras interés. ❓', score: 100 },
          { id: 'bloc', text: 'Tomas nota para buscar información después. 🗒️', score: 50 },
          { id: 'cara-indiferente', text: 'No prestas atención porque no te afecta. 😐', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Te piden ideas para mejorar un proceso.',
        type: 'choice',
        options: [
          { id: 'mapa', text: 'Propones explorar opciones nuevas aunque lleve tiempo. 🗺️', score: 100 },
          { id: 'grupo', text: 'Preguntas a otros cómo lo harían. 👥', score: 50 },
          { id: 'libros-cerrados', text: 'Usas solo lo que ya sabes bien. 📚', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Te dan feedback sobre cómo haces una tarea.',
        type: 'choice',
        options: [
          { id: 'cara-neutra', text: 'Lo aceptas pero no cambias nada. 😐', score: 50 },
          { id: 'cruz', text: 'Te molesta y te cierras al comentario. ❌', score: 20 },
          { id: 'pulgar-arriba', text: 'Lo agradeces y preguntas cómo mejorar. 👍', score: 100 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Increíble!',
        description: '¡Bravo! Has alcanzado el ecuador en esta fase. ¡Sigue así!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'resilience-flexibility',
    title: 'Resiliencia y Flexibilidad',
    subtitle: 'Día 6',
    description: 'Hoy surgen cambios inesperados, errores y tareas nuevas de última hora. ¿Cómo te adaptas?',
    softSkill: 'Resiliencia y flexibilidad',
    day: 'Lunes',
    scenario: 'Sexto día en IntegraPro. Te enfrentas a cambios y retos imprevistos.',
    icon: '🔄',
    color: '#F2A6D1',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Te avisan de que han cambiado una tarea que ya tenías casi terminada.',
        type: 'choice',
        options: [
          { id: 'interrogacion', text: 'Preguntas por qué han hecho el cambio y te cuesta aceptarlo. ❓', score: 50 },
          { id: 'cara-triste', text: 'Te frustras y prefieres que lo haga otra persona. 😞', score: 20 },
          { id: 'flecha-circulo', text: 'Te adaptas, revisas lo hecho y lo modificas sin problema. 🔄', score: 100 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Cometes un error y, aunque un poco tarde, te das cuenta.',
        type: 'choice',
        options: [
          { id: 'telefono', text: 'Lo avisas pero dejas que lo corrija otra persona. ☎️', score: 50 },
          { id: 'manos-cara', text: 'Intentas ocultarlo o te bloqueas. 🙈', score: 20 },
          { id: 'mano-levantada', text: 'Lo reconoces, buscas cómo solucionarlo y avisas. ✋', score: 100 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Te piden hacer una tarea urgente que nunca has hecho.',
        type: 'choice',
        options: [
          { id: 'libro-abierto', text: 'Lo intentas, pides instrucciones y te adaptas. 📖', score: 100 },
          { id: 'dos-personas', text: 'Prefieres que alguien con experiencia lo haga. 👥', score: 50 },
          { id: 'cruz', text: 'Dices que no puedes y te retiras. ❌', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Hoy hay mucho más trabajo de lo habitual.',
        type: 'choice',
        options: [
          { id: 'mano-levantada', text: 'Haces lo que puedes y pides ayuda si te desbordas. ✋', score: 50 },
          { id: 'exclamacion', text: 'Te agobias y no sabes por dónde empezar. ❗', score: 20 },
          { id: 'lista-check', text: 'Priorizar, organizar y mantener la calma. ✅', score: 100 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'El plan del día cambia varias veces por causas externas.',
        type: 'choice',
        options: [
          { id: 'pausa', text: 'Te bloqueas y necesitas parar. ⏸️', score: 20 },
          { id: 'puente', text: 'Te adaptas y buscas soluciones alternativas. 🌉', score: 100 },
          { id: 'cara-neutra', text: 'Te adaptas, aunque te molesta. 😐', score: 50 }        
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Magnífico!',
        description: '¡Felicidades! Has completado exitosamente este minijuego. ¡Lo estás logrando!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'self-awareness',
    title: 'Autoconciencia',
    subtitle: 'Día 7',
    description: 'Hoy toca reflexionar sobre tus puntos fuertes, límites y emociones en el trabajo.',
    softSkill: 'Autoconciencia',
    day: 'Martes',
    scenario: 'Séptimo día en IntegraPro. Reflexionas sobre tus emociones y capacidades.',
    icon: '🧠',
    color: '#A6C2F2',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Te cuesta terminar una tarea.',
        type: 'choice',
        options: [
          { id: 'cruz', text: 'Lo dejas sin hacer. ❌', score: 20 },
          { id: 'persona-sola', text: 'Insistes en hacerlo por tu cuenta aunque tardes mucho. 🧑‍🦰', score: 50 },
          { id: 'mano-levantada', text: 'Reconoces que necesitas ayuda y la pides. ✋', score: 100 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Recibes un elogio por tu trabajo.',
        type: 'choice',
        options: [
          { id: 'pulgar-arriba', text: 'Lo agradeces y reconoces tu propio esfuerzo. 👍', score: 100 },
          { id: 'cara-avergonzada', text: 'Te incomoda y no sabes qué decir. 😳', score: 20 },
          { id: 'mano-moviendo', text: 'Le quitas importancia ("no es para tanto"). 👋', score: 50 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Sientes que te estás estresando.',
        type: 'choice',
        options: [
          { id: 'taza-cafe', text: 'Paras y tomas un descanso corto. ☕', score: 100 },
          { id: 'reloj', text: 'Sigues trabajando aunque te cueste concentrarte. ⏰', score: 50 },
          { id: 'cara-cansada', text: 'Ignoras el malestar hasta que te bloqueas. 😩', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Notas que una tarea te motiva especialmente.',
        type: 'choice',
        options: [
          { id: 'cara-sonriente', text: 'Te alegras, pero no lo comunicas. 🙂', score: 50 },
          { id: 'cara-neutra', text: 'No prestas atención a cómo te sientes. 😐', score: 20 },
          { id: 'lupa-corazon', text: 'Analizas por qué te motiva y pides más de ese tipo. 🔍❤️', score: 100 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Te equivocas al decir algo delante de otras personas.',
        type: 'choice',
        options: [
          { id: 'bocadillo-ups', text: 'Reconoces el error con naturalidad. 💬', score: 100 },
          { id: 'dedo-senalando', text: 'Te justificas o echas la culpa a otra cosa. 👉', score: 50 },
          { id: 'cara-sonrojada', text: 'Te avergüenzas y no vuelves a hablar. 😳', score: 20 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Extraordinario!',
        description: '¡Enhorabuena! Has completado el séptimo minijuego. ¡Queda muy poco para el final!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'empathy',
    title: 'Empatía',
    subtitle: 'Día 8',
    description: 'Hoy tus colegas te cuentan situaciones personales y profesionales. ¿Cómo respondes?',
    softSkill: 'Empatía',
    day: 'Miércoles',
    scenario: 'Octavo día en IntegraPro. Escuchas y apoyas a otros empleados de la empresa.',
    icon: '💞',
    color: '#F2A6A6',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Una compañera se muestra preocupada por un familiar enfermo.',
        type: 'choice',
        options: [
          { id: 'oido-corazon', text: 'Le escuchas y te interesas sinceramente. 👂❤️', score: 100 },
          { id: 'pulgar-arriba', text: 'Le animas, pero cambias de tema. 👍', score: 50 },
          { id: 'cara-seria', text: 'Le dices que "todos tenemos problemas" y sigues a lo tuyo. 😐', score: 20 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Una persona del equipo está sobrecargada de trabajo.',
        type: 'choice',
        options: [
          { id: 'bocadillo', text: 'Le das ánimos, pero no cambias tu rutina. 💬', score: 50 },
          { id: 'cara-neutra', text: 'Ignoras la situación, no es tu problema. 😐', score: 20 },
          { id: 'manos-ayuda', text: 'Te ofreces a ayudar si puedes. 🤲', score: 100 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Un miembro del equipo comete un error y se siente mal.',
        type: 'choice',
        options: [
          { id: 'pulgar-arriba', text: 'Le dices que no pasa nada y cambias de tema. 👍', score: 50 },
          { id: 'manos-hombro', text: 'Le apoyas y le cuentas que tú también te equivocas a veces. 🤝', score: 100 },
          { id: 'carcajada', text: 'Te ríes o haces un comentario sarcástico. 😂', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Alguien del equipo se muestra callado y distante.',
        type: 'choice',
        options: [
          { id: 'mano-hombro', text: 'Te acercas y le preguntas si necesita algo. 🤲', score: 100 },
          { id: 'cara-amable', text: 'Respetas su silencio pero estás disponible. 🙂', score: 50 },
          { id: 'cara-otro-lado', text: 'Prefieres no intervenir. 🙄', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Un cliente se queja por un error.',
        type: 'choice',
        options: [
          { id: 'oido-bocadillo', text: 'Escuchas su queja y reconoces su molestia. 👂💬', score: 100 },
          { id: 'bocadillo', text: 'Le explicas que no es grave y que tenga paciencia. 💬', score: 50 },
          { id: 'cruz', text: 'Le dices que no tienes la culpa y te molestas. ❌', score: 20 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Maravilloso!',
        description: '¡Felicidades! Un nuevo minijuego completado. ¡Tu objetivo está cada vez más cerca!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'critical-thinking',
    title: 'Pensamiento Crítico',
    subtitle: 'Día 9',
    description: 'Hoy te enfrentas a información contradictoria y problemas complejos. ¿Cómo analizas y decides?',
    softSkill: 'Pensamiento Crítico',
    day: 'Jueves',
    scenario: 'Noveno día en IntegraPro. Tienes que tomar decisiones informadas y objetivas.',
    icon: '🧠',
    color: '#A6C8F2',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Recibes dos informes con datos opuestos sobre un proyecto.',
        type: 'choice',
        options: [
          { id: 'analizas', text: 'Analizas ambos informes y buscas fuentes adicionales. 🔍', score: 100 },
          { id: 'eliges-rapido', text: 'Eliges el que te parece más convincente. ⚡', score: 50 },
          { id: 'ignoras', text: 'Lo ignoras y sigues como si nada. 🙈', score: 20 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Otro empleado de la empresa propone una solución poco habitual.',
        type: 'choice',
        options: [
          { id: 'dudas', text: 'Dudas porque es diferente, pero no investigas más. 🤔', score: 50 },
          { id: 'escuchas', text: 'Escuchas y evalúas objetivamente la propuesta. 👂', score: 100 },
          { id: 'rechazas', text: 'La rechazas sin analizarla. ❌', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Debes priorizar tareas con información incompleta.',
        type: 'choice',
        options: [
          { id: 'preguntas', text: 'Preguntas y recopilas más datos antes de decidir. 📝', score: 100 },
          { id: 'decides-intuicion', text: 'Decides por intuición. 🎲', score: 50 },
          { id: 'azar', text: 'Eliges al azar. 🎯', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Te enfrentas a un rumor sobre cambios en la empresa.',
        type: 'choice',
        options: [
          { id: 'difundes', text: 'Comentas el rumor sin comprobarlo. 🗣️', score: 50 },
          { id: 'ignoras', text: 'Ignoras el tema, no te interesan los rumores. 🙈', score: 20 },
          { id: 'verificas', text: 'Verificas la información antes de reaccionar. ✅', score: 100 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Debes elegir entre dos proveedores con ventajas y desventajas.',
        type: 'choice',
        options: [
          { id: 'amigo', text: 'Eliges al que te cae mejor. 🤝', score: 20 },
          { id: 'comparacion', text: 'Haces una tabla comparativa y decides objetivamente. 📊', score: 100 },
          { id: 'elige-rapido', text: 'Eliges el más barato. 💸', score: 50 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Brillante!',
        description: '¡Felicidades! Has completado el noveno minijuego. ¡Continúa a por el último!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'leadership',
    title: 'Liderazgo',
    subtitle: 'Día 10',
    description: 'Hoy te asignan coordinar un pequeño equipo para un reto especial. ¿Cómo lideras?',
    softSkill: 'Liderazgo',
    day: 'Viernes',
    scenario: 'Décimo día en IntegraPro. Es tu oportunidad de guiar y motivar a tu equipo.',
    icon: '🌟',
    color: '#F2E2A6',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'El equipo está desmotivado por un reto difícil.',
        type: 'choice',
        options: [
          { id: 'presionas', text: 'Presionas para que trabajen más rápido. ⏩', score: 50 },
          { id: 'ignoras', text: 'Ignoras el ánimo del equipo. 🙈', score: 20 },
          { id: 'motivas', text: 'Motivas al equipo y reconoces sus logros. 💪', score: 100 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Debes delegar tareas para cumplir el objetivo.',
        type: 'choice',
        options: [
          { id: 'delegas', text: 'Delegas según las fortalezas de cada persona. 🧩', score: 100 },
          { id: 'aleatorio', text: 'Repartes tareas al azar. 🎲', score: 50 },
          { id: 'haces-todo', text: 'Prefieres hacerlo todo tú. 🏃', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Surge un conflicto entre dos miembros del equipo.',
        type: 'choice',
        options: [
          { id: 'tomas-parte', text: 'Tomas partido por uno de ellos. ⚖️', score: 20 },
          { id: 'ignoras', text: 'Ignoras el conflicto esperando que se resuelva solo. 🙈', score: 50 },
          { id: 'medias', text: 'Medias y facilitas el diálogo. 🤝', score: 100 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'El equipo logra un avance importante.',
        type: 'choice',
        options: [
          { id: 'celebras', text: 'Celebras el logro y agradeces el esfuerzo. 🎉', score: 100 },
          { id: 'sigues', text: 'Sigues trabajando sin reconocerlo. 🏃', score: 50 },
          { id: 'te-apropias', text: 'Te atribuyes el mérito. 🧍', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Debes tomar una decisión difícil para el grupo.',
        type: 'choice',
        options: [
          { id: 'decides-solo', text: 'Decides sin consultar a nadie. 🗣️', score: 50 },
          { id: 'escuchas', text: 'Escuchas las opiniones del equipo antes de decidir. 👂', score: 100 },
          { id: 'evitas', text: 'Evitas decidir. ⏸️', score: 20 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: '¡Sobresaliente!',
        description: '¡Enhorabuena! Has completado todos los minijuegos. ¡Lo has hecho de maravilla!',
        type: 'choice',
        options: [
          { id: 'volver-menu', text: 'Volver al menú', score: 0 }
        ]
      }
    ]
  }
];

// Los 10 minijuegos están completos

export const getGameById = (id: string): Game | undefined => {
  return games.find(game => game.id === id);
};

export const getNextGame = (currentGameId: string): Game | undefined => {
  const currentIndex = games.findIndex(game => game.id === currentGameId);
  return games[currentIndex + 1];
};

export const getGameProgress = (completedGames: string[]): GameProgress => {
  return {
    totalGames: games.length,
    completedGames: completedGames.length,
    currentGame: completedGames.length < games.length ? games[completedGames.length]?.id : undefined
  };
}; 