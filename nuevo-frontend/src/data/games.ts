import { Game } from '../types/game';

export const games: Game[] = [
  {
    id: 'decision-making',
    title: 'Primera llamada del día',
    subtitle: 'Toma de decisiones',
    description: 'Hoy es tu primer día en la empresa. Vas a estar en el área de apoyo. Te irás encontrando con situaciones reales. No hay respuestas correctas o incorrectas. Solo actúa como lo harías en la vida real.',
    softSkill: 'Toma de decisiones',
    day: 'Lunes',
    scenario: 'Primer día en un puesto de apoyo en una empresa de logística',
    icon: '📞',
    color: '#F2D680',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Bienvenido a tu primer día',
        description: 'Hoy es tu primer día en la empresa. Vas a estar en el área de apoyo. Te irás encontrando con situaciones reales. No hay respuestas correctas o incorrectas. Solo actúa como lo harías en la vida real.',
        type: 'choice',
        options: [
          {
            id: 'start',
            text: 'Empezar el día',
            score: 0,
            nextSceneId: 'phone-call'
          }
        ]
      },
      {
        id: 'phone-call',
        title: 'La primera llamada',
        description: 'Suena el teléfono. Una persona pregunta por tu compañer@, que no está disponible.',
        type: 'choice',
        options: [
          {
            id: 'take-note',
            text: 'Tomas nota del recado y se lo pasas después',
            score: 80,
            feedback: 'Buena decisión. Tomar nota es una práctica profesional.',
            nextSceneId: 'multiple-tasks'
          },
          {
            id: 'try-help',
            text: 'Intentas ayudar aunque no entiendes bien lo que necesita',
            score: 60,
            feedback: 'Iniciativa positiva, pero asegúrate de entender bien antes de actuar.',
            nextSceneId: 'multiple-tasks'
          },
          {
            id: 'call-later',
            text: 'Le dices que llame más tarde porque estás ocupad@',
            score: 40,
            feedback: 'Es importante ser honesto sobre tu disponibilidad.',
            nextSceneId: 'multiple-tasks'
          }
        ]
      },
      {
        id: 'multiple-tasks',
        title: 'Demasiadas tareas',
        description: 'Te han dado cuatro tareas para esta mañana. Una persona del equipo te dice que una de ellas es urgente.',
        type: 'drag-drop',
        dragDropConfig: {
          items: [
            { id: 'task1', text: 'Revisar inventario', category: 'urgent' },
            { id: 'task2', text: 'Preparar documentación', category: 'normal' },
            { id: 'task3', text: 'Responder emails', category: 'normal' },
            { id: 'task4', text: 'Organizar archivos', category: 'low' }
          ],
          targetZones: [
            { id: 'priority1', title: 'Prioridad Alta', accepts: ['urgent'] },
            { id: 'priority2', title: 'Prioridad Media', accepts: ['normal'] },
            { id: 'priority3', title: 'Prioridad Baja', accepts: ['low'] }
          ],
          correctOrder: ['task1', 'task2', 'task3', 'task4']
        },
        nextSceneId: 'technical-problem'
      },
      {
        id: 'technical-problem',
        title: 'Problema técnico',
        description: 'El sistema informático se congela mientras estás introduciendo datos.',
        type: 'choice',
        options: [
          {
            id: 'wait',
            text: 'Esperas unos minutos a ver si vuelve',
            score: 70,
            feedback: 'Paciencia es una virtud, pero no esperes demasiado.',
            nextSceneId: 'tension'
          },
          {
            id: 'call-support',
            text: 'Llamas a soporte técnico',
            score: 90,
            feedback: 'Excelente decisión. Pedir ayuda cuando es necesario es profesional.',
            nextSceneId: 'tension'
          },
          {
            id: 'restart',
            text: 'Reinicias el equipo por tu cuenta',
            score: 50,
            feedback: 'Iniciativa, pero asegúrate de que es seguro hacerlo.',
            nextSceneId: 'tension'
          }
        ]
      },
      {
        id: 'tension',
        title: 'Tensión inesperada',
        description: 'Un cliente entra a la oficina nervioso y empieza a levantar la voz.',
        type: 'choice',
        options: [
          {
            id: 'call-experienced',
            text: 'Llamas a alguien con más experiencia',
            score: 85,
            feedback: 'Buena decisión. Reconocer cuándo necesitas apoyo es importante.',
            nextSceneId: 'final-evaluation'
          },
          {
            id: 'calm-client',
            text: 'Intentas calmarlo y ver qué necesita',
            score: 75,
            feedback: 'Valiente intento, pero asegúrate de que es seguro.',
            nextSceneId: 'final-evaluation'
          },
          {
            id: 'walk-away',
            text: 'Te alejas discretamente',
            score: 60,
            feedback: 'A veces es mejor evitar conflictos.',
            nextSceneId: 'final-evaluation'
          }
        ]
      },
      {
        id: 'final-evaluation',
        title: 'Evaluación final del día',
        description: 'Tu coordinador/a te pide feedback sobre cómo te has sentido.',
        type: 'choice',
        options: [
          {
            id: 'curious',
            text: 'Curios@, con ganas de aprender',
            score: 90,
            feedback: '¡Excelente actitud! La curiosidad es clave para el aprendizaje.',
            nextSceneId: 'completion'
          },
          {
            id: 'lost-but-interested',
            text: 'Un poco perdid@ pero con interés',
            score: 75,
            feedback: 'Es normal sentirse perdido el primer día. El interés es lo importante.',
            nextSceneId: 'completion'
          },
          {
            id: 'stressed',
            text: 'Estresad@, necesito más tiempo',
            score: 60,
            feedback: 'Es válido pedir más tiempo. La honestidad es importante.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Buen trabajo!',
        description: '¡Buen trabajo! Hoy has resuelto situaciones reales que pueden pasar en muchos trabajos. No importa lo que hayas elegido: lo que cuenta es cómo te enfrentas a lo que sucede. Has completado tu primer día. Mañana te espera un nuevo reto.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Toma de decisiones!'
          }
        ]
      }
    ]
  },
  {
    id: 'problem-solving',
    title: 'Algo no cuadra',
    subtitle: 'Resolución de problemas',
    description: 'Hoy te han asignado la tarea de revisar varios pedidos antes de que salgan de la empresa. Algo no encaja… y necesitas descubrir qué es. ¿Preparad@?',
    softSkill: 'Resolución de problemas',
    day: 'Martes',
    scenario: 'Segundo día en la empresa de logística. Hoy te asignan una tarea concreta en el área de control y revisión de pedidos.',
    icon: '🧩',
    color: '#374BA6',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Revisión de pedidos',
        description: 'Hoy te han asignado la tarea de revisar varios pedidos antes de que salgan de la empresa. Algo no encaja… y necesitas descubrir qué es. ¿Preparad@?',
        type: 'choice',
        options: [
          {
            id: 'start',
            text: 'Empezar revisión',
            score: 0,
            nextSceneId: 'incomplete-order'
          }
        ]
      },
      {
        id: 'incomplete-order',
        title: 'El pedido incompleto',
        description: 'Te llega una lista con tres pedidos. Uno de ellos está incompleto.',
        type: 'visual-exploration',
        visualConfig: {
          imageUrl: '/api/scenes/1.json',
          interactiveAreas: [
            { id: 'order1', x: 50, y: 100, width: 200, height: 80, action: 'click' },
            { id: 'order2', x: 300, y: 100, width: 200, height: 80, action: 'click' },
            { id: 'order3', x: 550, y: 100, width: 200, height: 80, action: 'click' }
          ],
          explorationMode: true
        },
        nextSceneId: 'paper-mixed'
      },
      {
        id: 'paper-mixed',
        title: 'El papel cambiado',
        description: 'Te das cuenta de que uno de los albaranes no corresponde con el pedido al que está asignado.',
        type: 'drag-drop',
        dragDropConfig: {
          items: [
            { id: 'albaran1', text: 'Albarán A-001', category: 'order1' },
            { id: 'albaran2', text: 'Albarán A-002', category: 'order2' },
            { id: 'albaran3', text: 'Albarán A-003', category: 'order3' }
          ],
          targetZones: [
            { id: 'order1', title: 'Pedido 1', accepts: ['order1'] },
            { id: 'order2', title: 'Pedido 2', accepts: ['order2'] },
            { id: 'order3', title: 'Pedido 3', accepts: ['order3'] }
          ]
        },
        nextSceneId: 'time-pressure'
      },
      {
        id: 'time-pressure',
        title: 'Revisión contra reloj',
        description: 'Te indican que el camión sale en 10 minutos y hay un pedido con tres discrepancias.',
        type: 'choice',
        options: [
          {
            id: 'solve-alone',
            text: 'Intentas solucionarlo tú sol@ aunque tardes un poco más',
            score: 70,
            feedback: 'Iniciativa positiva, pero considera el tiempo disponible.',
            nextSceneId: 'hidden-error'
          },
          {
            id: 'ask-help',
            text: 'Pides ayuda al momento',
            score: 85,
            feedback: 'Buena decisión. Saber cuándo pedir ayuda es importante.',
            nextSceneId: 'hidden-error'
          },
          {
            id: 'send-as-is',
            text: 'Envíalo como está para no retrasar el camión',
            score: 40,
            feedback: 'Considera las consecuencias de enviar un pedido incorrecto.',
            nextSceneId: 'hidden-error'
          }
        ]
      },
      {
        id: 'hidden-error',
        title: 'El fallo oculto',
        description: 'Todos los papeles parecen estar bien, pero sientes que algo no encaja. ¿Qué haces?',
        type: 'visual-exploration',
        visualConfig: {
          imageUrl: '/api/scenes/2.json',
          interactiveAreas: [
            { id: 'box1', x: 100, y: 150, width: 100, height: 100, action: 'click' },
            { id: 'box2', x: 250, y: 150, width: 100, height: 100, action: 'click' },
            { id: 'box3', x: 400, y: 150, width: 100, height: 100, action: 'click' }
          ],
          explorationMode: true
        },
        nextSceneId: 'improvement-report'
      },
      {
        id: 'improvement-report',
        title: 'Informe de mejoras',
        description: 'Te piden que completes un informe de mejora rápida.',
        type: 'choice',
        options: [
          {
            id: 'details',
            text: 'He aprendido a fijarme mejor en los detalles',
            score: 80,
            feedback: 'Excelente observación. Los detalles son importantes.',
            nextSceneId: 'completion'
          },
          {
            id: 'help-timing',
            text: 'Pedir ayuda en el momento adecuado evita errores',
            score: 85,
            feedback: 'Muy buena reflexión. El timing es clave.',
            nextSceneId: 'completion'
          },
          {
            id: 'think-first',
            text: 'A veces hay que parar y pensar antes de actuar',
            score: 90,
            feedback: '¡Excelente! La reflexión es fundamental.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Buen trabajo!',
        description: '¡Buen trabajo! Detectar errores no es fácil, y hoy lo has hecho de maravilla. Resolver problemas requiere lógica, pero también intuición. Has desbloqueado una nueva habilidad: Resolución de problemas. Nos vemos mañana para un nuevo reto.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Resolución de problemas!'
          }
        ]
      }
    ]
  },
  {
    id: 'teamwork',
    title: 'El envío urgente',
    subtitle: 'Trabajo en equipo',
    description: 'Hoy vas a trabajar con dos compañer@s. Juntos tenéis que preparar un envío especial. Habrá momentos de coordinación, confusión y decisiones compartidas. ¿List@ para colaborar?',
    softSkill: 'Trabajo en equipo',
    day: 'Miércoles',
    scenario: 'Hoy formas parte de un pequeño equipo encargado de preparar un envío que debe salir antes de las 14:00.',
    icon: '🤝',
    color: '#4CAF50',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Trabajo en equipo',
        description: 'Hoy vas a trabajar con dos compañer@s. Juntos tenéis que preparar un envío especial. Habrá momentos de coordinación, confusión y decisiones compartidas. ¿List@ para colaborar?',
        type: 'choice',
        options: [
          {
            id: 'start',
            text: 'Comenzar trabajo en equipo',
            score: 0,
            nextSceneId: 'task-distribution'
          }
        ]
      },
      {
        id: 'task-distribution',
        title: 'Reparto de tareas',
        description: 'Tu supervisor te presenta a tus compañer@s: Alex y Carmen. Te dan una lista con 3 tareas y os dicen que os las repartáis. Alex prefiere el ordenador. Carmen tiene experiencia empaquetando. Tú eliges primero.',
        type: 'drag-drop',
        dragDropConfig: {
          items: [
            { id: 'computer-task', text: 'Introducir datos en el sistema', category: 'alex' },
            { id: 'packaging-task', text: 'Empaquetar productos', category: 'carmen' },
            { id: 'coordination-task', text: 'Coordinar el proceso', category: 'me' }
          ],
          targetZones: [
            { id: 'alex', title: 'Alex (ordenador)', accepts: ['alex'] },
            { id: 'carmen', title: 'Carmen (empaquetado)', accepts: ['carmen'] },
            { id: 'me', title: 'Tú', accepts: ['me'] }
          ]
        },
        nextSceneId: 'carmen-needs-help'
      },
      {
        id: 'carmen-needs-help',
        title: 'Carmen necesita ayuda',
        description: 'Carmen está teniendo problemas para cerrar las cajas y pide ayuda.',
        type: 'choice',
        options: [
          {
            id: 'help-directly',
            text: 'Le ayudas directamente, aunque dejas tu tarea a medias',
            score: 85,
            feedback: 'Excelente espíritu de equipo. La colaboración es importante.',
            nextSceneId: 'alex-mistake'
          },
          {
            id: 'help-later',
            text: 'Le ofreces ayuda solo cuando termines tu parte',
            score: 70,
            feedback: 'Buena planificación, pero considera la urgencia.',
            nextSceneId: 'alex-mistake'
          },
          {
            id: 'ignore',
            text: 'Le dices que lo intente otra vez, que tú también estás ocupad@',
            score: 40,
            feedback: 'Recuerda que el trabajo en equipo requiere apoyo mutuo.',
            nextSceneId: 'alex-mistake'
          }
        ]
      },
      {
        id: 'alex-mistake',
        title: 'Alex comete un error',
        description: 'Alex introduce mal una dirección en el sistema, y no se da cuenta. Tú lo ves desde tu pantalla.',
        type: 'choice',
        options: [
          {
            id: 'correct-respectfully',
            text: 'Le corriges con respeto',
            score: 90,
            feedback: 'Excelente comunicación. La corrección respetuosa es clave.',
            nextSceneId: 'time-limit'
          },
          {
            id: 'ignore-mistake',
            text: 'No dices nada porque no es tu trabajo',
            score: 50,
            feedback: 'Considera que el éxito del equipo depende de todos.',
            nextSceneId: 'time-limit'
          },
          {
            id: 'report-supervisor',
            text: 'Informas al supervisor directamente',
            score: 60,
            feedback: 'A veces es mejor intentar resolver entre compañeros primero.',
            nextSceneId: 'time-limit'
          }
        ]
      },
      {
        id: 'time-limit',
        title: 'Tiempo límite',
        description: 'Faltan 10 minutos y aún queda por cerrar el paquete final.',
        type: 'drag-drop',
        dragDropConfig: {
          items: [
            { id: 'final-package', text: 'Cerrar paquete final', category: 'urgent' },
            { id: 'check-system', text: 'Verificar sistema', category: 'important' },
            { id: 'clean-area', text: 'Limpiar área', category: 'low' }
          ],
          targetZones: [
            { id: 'alex', title: 'Alex', accepts: ['important'] },
            { id: 'carmen', title: 'Carmen', accepts: ['urgent'] },
            { id: 'me', title: 'Tú', accepts: ['low'] }
          ]
        },
        nextSceneId: 'final-conversation'
      },
      {
        id: 'final-conversation',
        title: 'Conversación final',
        description: 'Alex dice que le costó el trabajo en grupo. Carmen dice que se sintió valorada.',
        type: 'choice',
        options: [
          {
            id: 'positive-collaboration',
            text: 'Me gustó que nos ayudamos cuando fue necesario',
            score: 90,
            feedback: 'Excelente reflexión. El apoyo mutuo es fundamental.',
            nextSceneId: 'completion'
          },
          {
            id: 'prefer-solo',
            text: 'Prefiero trabajar sol@, fue un poco caótico',
            score: 60,
            feedback: 'Es válido tener preferencias, pero el trabajo en equipo es una habilidad valiosa.',
            nextSceneId: 'completion'
          },
          {
            id: 'could-improve',
            text: 'Estuvo bien, pero creo que podríamos organizarnos mejor',
            score: 80,
            feedback: 'Buena observación. La mejora continua es importante.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Gran trabajo en equipo!',
        description: '¡Gran trabajo en equipo! A veces colaborar no es fácil, pero encontrar la forma de hacerlo es una habilidad muy valiosa. Hoy has demostrado cómo aportar sin perder tu lugar. Has desbloqueado una nueva habilidad: Trabajo en equipo.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Trabajo en equipo!'
          }
        ]
      }
    ]
  },
  {
    id: 'emotional-management',
    title: 'Día de tensiones',
    subtitle: 'Gestión emocional',
    description: 'Hoy todo parece que va a ir mal. Personas nerviosas, tareas cambiantes, imprevistos… Pero tú puedes con esto. No se trata de hacerlo perfecto, sino de cómo lo vives.',
    softSkill: 'Gestión emocional',
    day: 'Jueves',
    scenario: 'Una jornada con imprevistos, personas nerviosas, tareas que cambian, y un poco de presión… como en la vida real.',
    icon: '😤',
    color: '#FF9800',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Día de tensiones',
        description: 'Hoy todo parece que va a ir mal. Personas nerviosas, tareas cambiantes, imprevistos… Pero tú puedes con esto. No se trata de hacerlo perfecto, sino de cómo lo vives.',
        type: 'choice',
        options: [
          {
            id: 'start',
            text: 'Enfrentar el día',
            score: 0,
            nextSceneId: 'plan-change'
          }
        ]
      },
      {
        id: 'plan-change',
        title: 'Cambio de planes',
        description: 'Al llegar, te informan de que vas a hacer una tarea diferente a la que te habían dicho ayer.',
        type: 'choice',
        options: [
          {
            id: 'accept-silently',
            text: 'Aceptas el cambio sin decir nada',
            score: 60,
            feedback: 'Es importante expresar tus sentimientos de forma constructiva.',
            nextSceneId: 'noisy-environment'
          },
          {
            id: 'ask-reason',
            text: 'Preguntas si hay una razón para el cambio',
            score: 80,
            feedback: 'Buena comunicación. Preguntar ayuda a entender.',
            nextSceneId: 'noisy-environment'
          },
          {
            id: 'protest-slowly',
            text: 'Te molesta y decides ir más despacio como forma de protesta',
            score: 40,
            feedback: 'La comunicación directa es mejor que la resistencia pasiva.',
            nextSceneId: 'noisy-environment'
          }
        ]
      },
      {
        id: 'noisy-environment',
        title: 'Ambiente ruidoso',
        description: 'Hay mucho ruido en el almacén hoy. Te cuesta concentrarte.',
        type: 'choice',
        options: [
          {
            id: 'use-headphones',
            text: 'Te pones cascos con cancelación de ruido (si tienes)',
            score: 85,
            feedback: 'Excelente solución. Buscar adaptaciones es importante.',
            nextSceneId: 'unpleasant-comment'
          },
          {
            id: 'ask-change-place',
            text: 'Pides cambiar de sitio',
            score: 75,
            feedback: 'Buena iniciativa. Pedir lo que necesitas es válido.',
            nextSceneId: 'unpleasant-comment'
          },
          {
            id: 'endure-errors',
            text: 'Aguantas, pero empiezas a cometer errores',
            score: 50,
            feedback: 'Es importante buscar soluciones antes de que afecte tu trabajo.',
            nextSceneId: 'unpleasant-comment'
          }
        ]
      },
      {
        id: 'unpleasant-comment',
        title: 'Comentario desagradable',
        description: 'Un compañero hace una broma sobre cómo haces las cosas. No parece con mala intención, pero te incomoda.',
        type: 'choice',
        options: [
          {
            id: 'ignore',
            text: 'Ignoras el comentario y sigues',
            score: 60,
            feedback: 'A veces ignorar es una estrategia válida.',
            nextSceneId: 'own-mistake'
          },
          {
            id: 'express-respectfully',
            text: 'Le dices que no te ha hecho gracia, con respeto',
            score: 90,
            feedback: 'Excelente asertividad. La comunicación respetuosa es clave.',
            nextSceneId: 'own-mistake'
          },
          {
            id: 'walk-away',
            text: 'Te vas un rato sin decir nada',
            score: 70,
            feedback: 'Tomar un respiro puede ser útil, pero considera comunicar.',
            nextSceneId: 'own-mistake'
          }
        ]
      },
      {
        id: 'own-mistake',
        title: 'Error propio',
        description: 'Cometes un error y lo ve tu coordinador. No te dice nada, pero tú lo has notado.',
        type: 'choice',
        options: [
          {
            id: 'recognize-correct',
            text: 'Lo reconoces y lo corriges',
            score: 90,
            feedback: 'Excelente responsabilidad. Reconocer errores es madurez.',
            nextSceneId: 'emotional-evaluation'
          },
          {
            id: 'correct-silently',
            text: 'Lo corriges sin decir nada',
            score: 75,
            feedback: 'Bien por corregir, pero la comunicación es importante.',
            nextSceneId: 'emotional-evaluation'
          },
          {
            id: 'freeze',
            text: 'Te bloqueas y dejas de hacer la tarea',
            score: 40,
            feedback: 'Es normal sentirse mal, pero intenta no paralizarte.',
            nextSceneId: 'emotional-evaluation'
          }
        ]
      },
      {
        id: 'emotional-evaluation',
        title: 'Autoevaluación emocional',
        description: 'Al final del día, te preguntan cómo te sentiste.',
        type: 'choice',
        options: [
          {
            id: 'managed-well',
            text: 'Me sentí incómod@, pero lo gestioné',
            score: 85,
            feedback: 'Excelente autoconciencia. Gestionar las emociones es una habilidad.',
            nextSceneId: 'completion'
          },
          {
            id: 'difficult-adapt',
            text: 'Fue difícil adaptarme hoy',
            score: 70,
            feedback: 'Es válido reconocer las dificultades.',
            nextSceneId: 'completion'
          },
          {
            id: 'could-pause',
            text: 'Pude parar y respirar cuando lo necesité',
            score: 90,
            feedback: '¡Excelente! La autorregulación es fundamental.',
            nextSceneId: 'completion'
          },
          {
            id: 'didnt-know-how',
            text: 'No supe cómo manejar algunas cosas',
            score: 60,
            feedback: 'Es normal no saberlo todo. El aprendizaje es continuo.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Gran avance!',
        description: 'Sentir cosas no es un problema. Gestionarlas de forma saludable es una habilidad que mejora con el tiempo. Hoy has enfrentado situaciones reales y has sabido responder desde ti mism@. ¡Gran avance! Has desbloqueado una nueva habilidad: Gestión emocional.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Gestión emocional!'
          }
        ]
      }
    ]
  },
  {
    id: 'communication',
    title: 'Reunión sorpresa',
    subtitle: 'Comunicación',
    description: 'Hoy no esperabas una reunión, pero te han invitado a participar en una breve puesta en común. No es un examen. Solo quieren saber cómo fue tu semana. ¿Te animas a participar?',
    softSkill: 'Comunicación',
    day: 'Viernes',
    scenario: 'Un coordinador ha convocado una reunión informal para repasar la semana. No esperabas tener que hablar en grupo, pero tu voz también importa.',
    icon: '🗣️',
    color: '#9C27B0',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Reunión sorpresa',
        description: 'Hoy no esperabas una reunión, pero te han invitado a participar en una breve puesta en común. No es un examen. Solo quieren saber cómo fue tu semana. ¿Te animas a participar?',
        type: 'choice',
        options: [
          {
            id: 'start',
            text: 'Entrar a la reunión',
            score: 0,
            nextSceneId: 'listening-turn'
          }
        ]
      },
      {
        id: 'listening-turn',
        title: 'Turno de escucha',
        description: 'Escuchas a tus dos compañer@s hablar de su experiencia. Te hacen una pregunta de comprensión: ¿Qué dijo Carmen que le costó más esta semana?',
        type: 'audio',
        audioConfig: {
          audioUrl: '/api/audio/carmen-experience.mp3',
          transcript: 'Carmen: "Esta semana me costó mucho el ruido en el almacén. Me distraía y me hacía cometer errores. Pero aprendí a pedir ayuda cuando lo necesitaba."',
          questions: [
            {
              id: 'carmen-difficulty',
              question: '¿Qué dijo Carmen que le costó más esta semana?',
              options: [
                { id: 'noise', text: 'El ruido', score: 100 },
                { id: 'computer', text: 'El ordenador', score: 0 },
                { id: 'nothing', text: 'No lo dijo', score: 0 }
              ]
            }
          ]
        },
        nextSceneId: 'speaking-turn'
      },
      {
        id: 'speaking-turn',
        title: 'Tu turno para hablar',
        description: 'El coordinador te pregunta directamente cómo te has sentido esta semana.',
        type: 'choice',
        options: [
          {
            id: 'brief-response',
            text: 'Bien, ha sido interesante',
            score: 60,
            feedback: 'Respuesta válida, pero podrías ser más específico.',
            nextSceneId: 'interruption'
          },
          {
            id: 'detailed-response',
            text: 'Me costó adaptarme el primer día, pero cada vez mejor',
            score: 85,
            feedback: 'Excelente comunicación. Específico y honesto.',
            nextSceneId: 'interruption'
          },
          {
            id: 'learning-response',
            text: 'He aprendido mucho, aunque aún tengo dudas',
            score: 80,
            feedback: 'Buena reflexión. Mostrar vulnerabilidad es valiente.',
            nextSceneId: 'interruption'
          }
        ]
      },
      {
        id: 'interruption',
        title: 'Momento de interrupción',
        description: 'Alex interrumpe mientras estás hablando.',
        type: 'choice',
        options: [
          {
            id: 'stop-let-talk',
            text: 'Te detienes y le dejas hablar',
            score: 70,
            feedback: 'Buena cortesía, pero puedes ser asertivo.',
            nextSceneId: 'explanation'
          },
          {
            id: 'assertive-response',
            text: 'Le dices amablemente que estabas hablando tú',
            score: 90,
            feedback: 'Excelente asertividad. La comunicación respetuosa es clave.',
            nextSceneId: 'explanation'
          },
          {
            id: 'stop-talking',
            text: 'No reaccionas, pero ya no quieres seguir hablando',
            score: 50,
            feedback: 'Es importante mantener tu voz en la conversación.',
            nextSceneId: 'explanation'
          }
        ]
      },
      {
        id: 'explanation',
        title: 'Explicación práctica',
        description: 'Te piden que expliques cómo hiciste una tarea esta semana.',
        type: 'choice',
        options: [
          {
            id: 'step-by-step',
            text: 'Primero recogí los materiales, luego preparé las cajas y finalmente las etiqueté',
            score: 90,
            feedback: 'Excelente explicación estructurada. Muy clara.',
            nextSceneId: 'closing-message'
          },
          {
            id: 'vague-explanation',
            text: 'Lo hice como me explicaron el primer día, más o menos',
            score: 60,
            feedback: 'Podrías ser más específico en tu explicación.',
            nextSceneId: 'closing-message'
          },
          {
            id: 'unsure-explanation',
            text: 'No estoy segur@ de cómo explicarlo',
            score: 50,
            feedback: 'Es válido no estar seguro, pero intenta explicar lo que recuerdes.',
            nextSceneId: 'closing-message'
          }
        ]
      },
      {
        id: 'closing-message',
        title: 'Mensaje de cierre',
        description: 'Antes de salir, debes escribir (o seleccionar) un mensaje para dejar constancia de cómo te sientes al terminar tu primera semana.',
        type: 'choice',
        options: [
          {
            id: 'gratitude',
            text: 'Gracias por el apoyo. He aprendido mucho',
            score: 85,
            feedback: 'Excelente mensaje. Agradecer es importante.',
            nextSceneId: 'completion'
          },
          {
            id: 'progress',
            text: 'Todavía tengo dudas, pero me siento mejor que el lunes',
            score: 80,
            feedback: 'Buena reflexión sobre el progreso.',
            nextSceneId: 'completion'
          },
          {
            id: 'intense-week',
            text: 'Ha sido una semana intensa. Me gustaría seguir mejorando',
            score: 90,
            feedback: 'Excelente actitud de mejora continua.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Enhorabuena!',
        description: 'Hablar, escuchar, explicar, preguntar… Todo eso forma parte del trabajo. Y lo has hecho a tu manera, con tu ritmo y tus palabras. Hoy has demostrado tu capacidad para comunicar. ¡Enhorabuena! Has desbloqueado una nueva habilidad: Comunicación.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Fin de la semana laboral',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Comunicación!'
          }
        ]
      }
    ]
  }
];

// Los otros 5 minijuegos se pueden agregar siguiendo el mismo patrón
// Minijuego 6: Curiosidad y aprendizaje continuo - "¿Y esto para qué sirve?"
// Minijuego 7: Resiliencia y flexibilidad - "No todo va como esperabas"
// Minijuego 8: Autoconciencia - "¿Cómo me siento hoy?"
// Minijuego 9: Empatía - "Ponte en sus zapatos"
// Minijuego 10: Gestión del tiempo - "Tiempo al tiempo"

export const getGameById = (id: string): Game | undefined => {
  return games.find(game => game.id === id);
};

export const getNextGame = (currentGameId: string): Game | undefined => {
  const currentIndex = games.findIndex(game => game.id === currentGameId);
  return games[currentIndex + 1];
};

export const getGameProgress = (completedGames: string[]): any => {
  return {
    totalGames: games.length,
    completedGames: completedGames.length,
    currentGame: completedGames.length < games.length ? games[completedGames.length]?.id : undefined
  };
}; 