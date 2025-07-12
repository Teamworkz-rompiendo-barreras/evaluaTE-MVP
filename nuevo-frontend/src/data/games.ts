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
          { id: 'atender', text: 'Le atiendes enseguida, aunque dejas tu tarea a medias. 🧑', score: 100 },
          { id: 'esperar', text: 'Le dices que le ayudas en cuanto termines lo que tienes. ⏰', score: 50 },
          { id: 'compañero', text: 'Buscas a otro compañero/a para que le atienda mientras tú acabas lo tuyo. 👥', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Hay un problema técnico con la impresora.',
        type: 'choice',
        options: [
          { id: 'solucionar', text: 'Lo intentas solucionar tú mismo/a. 🛠️', score: 100 },
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
          { id: 'opinion', text: 'Das tu opinión, aunque no estés seguro/a. 💬', score: 100 },
          { id: 'preguntar', text: 'Preguntas antes a tus compañeros/as. 👥', score: 50 },
          { id: 'no-opinar', text: 'Prefieres no opinar hasta tener más información. 📖', score: 20 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Bravo!',
        description: 'Hoy has demostrado tu capacidad para tomar decisiones en situaciones reales de trabajo. Cada forma de decidir suma valor.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
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
          { id: 'interrogacion', text: 'Sigues adelante sin revisar, porque no tienes claro qué hacer. ❓', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Te dan instrucciones poco claras para un trabajo.',
        type: 'choice',
        options: [
          { id: 'pregunta', text: 'Pides aclaraciones hasta entenderlo. ❔', score: 100 },
          { id: 'ojo', text: 'Haces lo que crees que piden aunque no estés seguro/a. 👁️', score: 20 },
          { id: 'grupo', text: 'Esperas a ver qué hacen otros/as para copiar. 👥', score: 50 }
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
          { id: 'colores', text: 'Agrupas por colores o tamaño, aunque no sea lo más útil. 🎨', score: 20 },
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
          { id: 'balanza', text: 'Comparas ventajas e inconvenientes de cada opción. ⚖️', score: 100 },
          { id: 'dedo', text: 'Eliges la que te suena mejor. ☝️', score: 20 },
          { id: 'responsable', text: 'Pides la opinión del responsable antes de decidir. 👔', score: 50 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Genial!',
        description: '¡Genial! Has puesto en práctica tu pensamiento analítico para encontrar soluciones. ¡Sigue observando y razonando con detalle!',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Resolución de problemas. ¡Bien hecho!',
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
          { id: 'bombilla', text: 'Propones una idea original para resolverlo. 💡', score: 100 },
          { id: 'check', text: 'Aplicas una solución que ya se ha hecho antes. ✔️', score: 50 },
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
          { id: 'pincel', text: 'Propones algo diferente y creativo. 🖌️', score: 100 },
          { id: 'repeticion', text: 'Repites la decoración de siempre. 🔁', score: 20 },
          { id: 'grupo', text: 'Pides ideas a tus compañeros/as. 👥', score: 50 }
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
          { id: 'fiesta', text: 'Propones una actividad distinta y divertida. 🎉', score: 100 },
          { id: 'ok', text: 'Dices que está bien como está. 👍', score: 20 },
          { id: 'bocadillo', text: 'Preguntas qué le gustaría a los demás. 💬', score: 50 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Muy bien!',
        description: '¡Muy bien! Has demostrado que tu creatividad puede marcar la diferencia en el trabajo diario. No dejes de aportar nuevas ideas.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Creatividad. ¡Bien hecho!',
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
        description: 'Un compañero/a está desmotivado/a.',
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
          { id: 'documento', text: 'Lo explicas de forma breve y sin insistir. 📄', score: 50 },
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
          { id: 'puno', text: 'Te mantienes en tu posición y no cedes. ✊', score: 20 },
          { id: 'corbata', text: 'Preguntas a una persona responsable para que decida. 👔', score: 50 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Debes pedir ayuda a alguien ocupado/a.',
        type: 'choice',
        options: [
          { id: 'bocadillo', text: 'Explicas claramente por qué necesitas ayuda. 💬', score: 100 },
          { id: 'reloj', text: 'Esperas a que esté libre aunque tardes más. ⏰', score: 50 },
          { id: 'solo', text: 'No lo pides y sigues solo/a. 🧑‍🦰', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Tienes una buena idea y quieres que te apoyen.',
        type: 'choice',
        options: [
          { id: 'grupo-estrella', text: 'Buscas aliados/as y explicas los beneficios para el equipo. 🌟', score: 100 },
          { id: 'puerta', text: 'Esperas a que surja la oportunidad. 🚪', score: 20 },
          { id: 'susurro', text: 'Se lo cuentas solo a una persona de confianza. 🤫', score: 50 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Enhorabuena!',
        description: '¡Enhorabuena! Has puesto en práctica tu capacidad de influencia social y tu forma de comunicar en el entorno laboral.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Influencia Social. ¡Bien hecho!',
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
          { id: 'libro-abierto', text: 'Aceptas y te apuntas enseguida. 📖', score: 100 },
          { id: 'agenda-cerrada', text: 'Prefieres no apuntarte, ya que tienes otras cosas. 📔', score: 20 },
          { id: 'grupo', text: 'Preguntas a tus compañeros/as antes de decidir. 👥', score: 50 }
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
          { id: 'libros-cerrados', text: 'Usas solo lo que ya sabes bien. 📚', score: 20 },
          { id: 'grupo', text: 'Preguntas a otros cómo lo harían. 👥', score: 50 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Te dan feedback sobre cómo haces una tarea.',
        type: 'choice',
        options: [
          { id: 'pulgar-arriba', text: 'Lo agradeces y preguntas cómo mejorar. 👍', score: 100 },
          { id: 'cara-neutra', text: 'Lo aceptas pero no cambias nada. 😐', score: 50 },
          { id: 'cruz', text: 'Te molesta y te cierras al comentario. ❌', score: 20 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Excelente!',
        description: '¡Excelente! Tu curiosidad y tus ganas de aprender son clave para avanzar en cualquier trabajo. Sigue buscando nuevas oportunidades para crecer.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Curiosidad y Aprendizaje. ¡Bien hecho!',
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
          { id: 'flecha-circulo', text: 'Te adaptas, revisas lo hecho y lo modificas sin problema. 🔄', score: 100 },
          { id: 'interrogacion', text: 'Preguntas por qué han hecho el cambio y te cuesta aceptarlo. ❓', score: 50 },
          { id: 'cara-triste', text: 'Te frustras y prefieres que lo haga otra persona. 😞', score: 20 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Cometes un error y lo detectas tú mismo/a.',
        type: 'choice',
        options: [
          { id: 'mano-levantada', text: 'Lo reconoces, buscas cómo solucionarlo y avisas. ✋', score: 100 },
          { id: 'telefono', text: 'Lo avisas pero dejas que lo corrija otro/a. ☎️', score: 50 },
          { id: 'manos-cara', text: 'Intentas ocultarlo o te bloqueas. 🙈', score: 20 }
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
          { id: 'lista-check', text: 'Priorizar, organizar y mantener la calma. ✅', score: 100 },
          { id: 'mano-levantada', text: 'Haces lo que puedes y pides ayuda si te desbordas. ✋', score: 50 },
          { id: 'exclamacion', text: 'Te agobias y no sabes por dónde empezar. ❗', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'El plan del día cambia varias veces por causas externas.',
        type: 'choice',
        options: [
          { id: 'puente', text: 'Te adaptas y buscas soluciones alternativas. 🌉', score: 100 },
          { id: 'cara-neutra', text: 'Te adaptas, aunque te molesta. 😐', score: 50 },
          { id: 'pausa', text: 'Te bloqueas y necesitas parar. ⏸️', score: 20 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Estupendo!',
        description: '¡Estupendo! Has demostrado resiliencia y flexibilidad ante los cambios. Estas cualidades te ayudarán a afrontar cualquier reto laboral.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Resiliencia y Flexibilidad. ¡Bien hecho!',
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
          { id: 'mano-levantada', text: 'Reconoces que necesitas ayuda y la pides. ✋', score: 100 },
          { id: 'persona-sola', text: 'Insistes en hacerlo tú solo/a aunque tardes mucho. 🧑‍🦰', score: 50 },
          { id: 'cruz', text: 'Lo dejas sin hacer y no avisas. ❌', score: 20 }
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
          { id: 'mano-moviendo', text: 'Le quitas importancia ("no es para tanto"). 👋', score: 50 },
          { id: 'cara-avergonzada', text: 'Te incomoda y no sabes qué decir. 😳', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Sientes que te estás estresando.',
        type: 'choice',
        options: [
          { id: 'taza-cafe', text: 'Te das cuenta y tomas un descanso corto. ☕', score: 100 },
          { id: 'reloj', text: 'Sigues trabajando aunque te cueste concentrarte. ⏰', score: 50 },
          { id: 'cara-cansada', text: 'Ignoras el malestar y te bloqueas. 😩', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Notas que una tarea te motiva especialmente.',
        type: 'choice',
        options: [
          { id: 'lupa-corazon', text: 'Analizas por qué te motiva y pides más de ese tipo. 🔍❤️', score: 100 },
          { id: 'cara-sonriente', text: 'Te alegras, pero no lo comunicas. 🙂', score: 50 },
          { id: 'cara-neutra', text: 'No prestas atención a cómo te sientes. 😐', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Te equivocas en algo delante de otras personas.',
        type: 'choice',
        options: [
          { id: 'bocadillo-ups', text: 'Reconoces el error con naturalidad. 💬', score: 100 },
          { id: 'dedo-senalando', text: 'Te justificas o echas la culpa a otra cosa. 👉', score: 50 },
          { id: 'cara-sonrojada', text: 'Te avergüenzas y no vuelves a hablar en público. 😳', score: 20 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Muy bien!',
        description: '¡Muy bien! Tener autoconciencia te permite trabajar mejor contigo mismo/a y con el equipo. Un gran paso hacia el éxito.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ]
      }
    ]
  },
  {
    id: 'empathy',
    title: 'Empatía',
    subtitle: 'Día 8',
    description: 'Hoy tus compañeros/as te cuentan situaciones personales y profesionales. ¿Cómo respondes?',
    softSkill: 'Empatía',
    day: 'Miércoles',
    scenario: 'Octavo día en IntegraPro. Escuchas y apoyas a tus compañeros/as.',
    icon: '💞',
    color: '#F2A6A6',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'prueba-1',
        title: 'Prueba 1',
        description: 'Un compañero/a se muestra preocupado/a por un familiar enfermo.',
        type: 'choice',
        options: [
          { id: 'oido-corazon', text: 'Le escuchas y te interesas sinceramente. 👂❤️', score: 100 },
          { id: 'pulgar-arriba', text: 'Le animas, pero cambias de tema. 👍', score: 50 },
          { id: 'cara-seria', text: 'Dices que "todos tenemos problemas" y sigues a lo tuyo. 😐', score: 20 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Una persona del equipo está sobrecargada de trabajo.',
        type: 'choice',
        options: [
          { id: 'manos-ayuda', text: 'Te ofreces a ayudar si puedes. 🤲', score: 100 },
          { id: 'bocadillo', text: 'Le das ánimos, pero no cambias tu rutina. 💬', score: 50 },
          { id: 'cara-neutra', text: 'Ignoras la situación, no es tu problema. 😐', score: 20 }
        ],
        nextSceneId: 'prueba-3'
      },
      {
        id: 'prueba-3',
        title: 'Prueba 3',
        description: 'Un/a compañero/a comete un error y se siente mal.',
        type: 'choice',
        options: [
          { id: 'manos-hombro', text: 'Le apoyas y le cuentas que tú también te equivocas a veces. 🤝', score: 100 },
          { id: 'pulgar-arriba', text: 'Le dices que no pasa nada y cambias de tema. 👍', score: 50 },
          { id: 'carcajada', text: 'Te ríes o haces un comentario sarcástico. 😂', score: 20 }
        ],
        nextSceneId: 'prueba-4'
      },
      {
        id: 'prueba-4',
        title: 'Prueba 4',
        description: 'Alguien del equipo se muestra callado/a y distante.',
        type: 'choice',
        options: [
          { id: 'mano-hombro', text: 'Te acercas y le preguntas si necesita algo. 🤲', score: 100 },
          { id: 'cara-amable', text: 'Respetas su silencio pero estás disponible. 🙂', score: 50 },
          { id: 'cara-otro-lado', text: 'No te das cuenta o prefieres no intervenir. 🙄', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Un cliente se queja por un error leve.',
        type: 'choice',
        options: [
          { id: 'oido-bocadillo', text: 'Escuchas su queja y reconoces su molestia. 👂💬', score: 100 },
          { id: 'bocadillo', text: 'Le explicas que no es grave y que tenga paciencia. 💬', score: 50 },
          { id: 'cruz', text: 'Le dices que no tienes la culpa y te molestas. ❌', score: 20 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Enhorabuena!',
        description: '¡Enhorabuena! Tu empatía ayuda a crear un ambiente laboral sano y colaborativo. Sigue cuidando las relaciones en tu entorno.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Empatía. ¡Bien hecho!',
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
          { id: 'eliges-rapido', text: 'Eliges el que te parece más convincente sin profundizar. ⚡', score: 50 },
          { id: 'ignoras', text: 'Ignoras la contradicción y sigues como si nada. 🙈', score: 20 }
        ],
        nextSceneId: 'prueba-2'
      },
      {
        id: 'prueba-2',
        title: 'Prueba 2',
        description: 'Un compañero/a propone una solución poco habitual.',
        type: 'choice',
        options: [
          { id: 'escuchas', text: 'Escuchas y evalúas objetivamente la propuesta. 👂', score: 100 },
          { id: 'dudas', text: 'Dudas porque es diferente, pero no investigas más. 🤔', score: 50 },
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
          { id: 'decides-intuicion', text: 'Decides por intuición, sin buscar más información. 🎲', score: 50 },
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
          { id: 'verificas', text: 'Verificas la información antes de reaccionar. ✅', score: 100 },
          { id: 'difundes', text: 'Comentas el rumor sin comprobarlo. 🗣️', score: 50 },
          { id: 'ignoras', text: 'Ignoras el tema y no te informas. 🙈', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Debes elegir entre dos proveedores con ventajas y desventajas.',
        type: 'choice',
        options: [
          { id: 'comparacion', text: 'Haces una tabla comparativa y decides objetivamente. 📊', score: 100 },
          { id: 'elige-rapido', text: 'Eliges el más barato sin analizar más. 💸', score: 50 },
          { id: 'amigo', text: 'Eliges al que te cae mejor. 🤝', score: 20 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Enhorabuena!',
        description: '¡Enhorabuena! Tu pensamiento crítico te permite tomar decisiones informadas y responsables. Sigue cuestionando y analizando.',
        type: 'choice',
        options: [
          { id: 'continuar', text: 'Continuar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Pensamiento Crítico. ¡Bien hecho!',
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
          { id: 'motivas', text: 'Motivas al equipo y reconoces sus logros. 💪', score: 100 },
          { id: 'presionas', text: 'Presionas para que trabajen más rápido. ⏩', score: 50 },
          { id: 'ignoras', text: 'Ignoras el ánimo del equipo. 🙈', score: 20 }
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
          { id: 'medias', text: 'Medias y facilitas el diálogo. 🤝', score: 100 },
          { id: 'ignoras', text: 'Ignoras el conflicto esperando que se resuelva solo. 🙈', score: 50 },
          { id: 'tomas-parte', text: 'Tomas partido por uno de ellos. ⚖️', score: 20 }
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
          { id: 'te-apropias', text: 'Te atribuyes el mérito solo tú. 🧍', score: 20 }
        ],
        nextSceneId: 'prueba-5'
      },
      {
        id: 'prueba-5',
        title: 'Prueba 5',
        description: 'Debes tomar una decisión difícil para el grupo.',
        type: 'choice',
        options: [
          { id: 'escuchas', text: 'Escuchas las opiniones del equipo antes de decidir. 👂', score: 100 },
          { id: 'decides-solo', text: 'Decides sin consultar a nadie. 🗣️', score: 50 },
          { id: 'evitas', text: 'Evitas decidir y dejas el problema sin resolver. ⏸️', score: 20 }
        ],
        nextSceneId: 'feedback-final'
      },
      {
        id: 'feedback-final',
        title: '¡Enhorabuena!',
        description: '¡Enhorabuena! Has demostrado habilidades de liderazgo, motivando y guiando a tu equipo hacia el éxito. Sigue desarrollando tu capacidad de inspirar a otros.',
        type: 'choice',
        options: [
          { id: 'finalizar', text: 'Finalizar', score: 0 }
        ],
        nextSceneId: 'game-complete'
      },
      {
        id: 'game-complete',
        title: 'Minijuego Completado',
        description: 'Has completado exitosamente el minijuego de Liderazgo. ¡Bien hecho!',
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