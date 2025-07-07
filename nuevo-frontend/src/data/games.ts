import { Game, GameProgress } from '../types/game';

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
        title: 'Bienvenida a tu primer día',
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
        description: 'Suena el teléfono. Una persona pregunta por tu persona compañera, que no está disponible.',
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
            text: 'Le dices que llame más tarde porque estás ocupado u ocupada',
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
        description: 'Tu coordinador te pide feedback sobre cómo te has sentido.',
        type: 'choice',
        options: [
          {
            id: 'curious',
            text: 'Persona curiosa, con ganas de aprender',
            score: 90,
            feedback: '¡Excelente actitud! La curiosidad es clave para el aprendizaje.',
            nextSceneId: 'completion'
          },
          {
            id: 'lost-but-interested',
            text: 'Un poco perdido o perdida pero con interés',
            score: 75,
            feedback: 'Es normal sentirse perdido el primer día. El interés es lo importante.',
            nextSceneId: 'completion'
          },
          {
            id: 'stressed',
            text: 'Estresado o estresada, necesito más tiempo',
            score: 60,
            feedback: 'Es válido pedir más tiempo. La honestidad es importante.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Buen trabajo!',
        description: 'Hoy has resuelto situaciones reales que pueden pasar en muchos trabajos. No importa lo que hayas elegido: lo que cuenta es cómo te enfrentas a lo que sucede. Has completado tu primer día. Mañana te espera un nuevo reto.',
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
            text: 'Le dices que lo intente otra vez, que tú también estás ocupada o ocupada',
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
  },
  {
    id: 'curiosity-learning',
    title: '¿Y esto para qué sirve?',
    subtitle: 'Curiosidad y aprendizaje continuo',
    description: 'Hoy te han asignado una tarea nueva que nunca habías hecho. En lugar de seguir las instrucciones al pie de la letra, decides explorar y entender por qué se hace así.',
    softSkill: 'Curiosidad y aprendizaje continuo',
    day: 'Lunes (Semana 2)',
    scenario: 'Nueva tarea en el área de inventario. Te dan una lista de productos para contar, pero decides investigar más.',
    icon: '🔍',
    color: '#FF6B6B',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Nueva tarea desconocida',
        description: 'Te han dado una lista de productos para contar en el almacén. Es una tarea nueva para ti. ¿Qué haces?',
        type: 'choice',
        options: [
          {
            id: 'start-counting',
            text: 'Empiezas a contar directamente',
            score: 60,
            feedback: 'Eficiente, pero podrías aprender más sobre el proceso.',
            nextSceneId: 'discovery'
          },
          {
            id: 'ask-questions',
            text: 'Preguntas por qué se hace así y si hay otras formas',
            score: 90,
            feedback: '¡Excelente curiosidad! Preguntar es la base del aprendizaje.',
            nextSceneId: 'discovery'
          },
          {
            id: 'observe-first',
            text: 'Observas cómo lo hacen otros antes de empezar',
            score: 80,
            feedback: 'Buena estrategia. Observar es una forma de aprender.',
            nextSceneId: 'discovery'
          }
        ]
      },
      {
        id: 'discovery',
        title: 'Descubriendo el proceso',
        description: 'Tu supervisor te explica que el conteo sirve para detectar discrepancias entre el inventario real y el registrado. ¿Qué más quieres saber?',
        type: 'choice',
        options: [
          {
            id: 'ask-why-discrepancies',
            text: '¿Por qué hay discrepancias?',
            score: 85,
            feedback: 'Excelente pregunta. Entender las causas es fundamental.',
            nextSceneId: 'investigation'
          },
          {
            id: 'ask-frequency',
            text: '¿Con qué frecuencia se hace esto?',
            score: 75,
            feedback: 'Buena pregunta sobre la periodicidad del proceso.',
            nextSceneId: 'investigation'
          },
          {
            id: 'ask-consequences',
            text: '¿Qué pasa si no se hace bien?',
            score: 80,
            feedback: 'Importante considerar las consecuencias.',
            nextSceneId: 'investigation'
          }
        ]
      },
      {
        id: 'investigation',
        title: 'Investigación activa',
        description: 'Mientras cuentas, notas que algunos productos están mal organizados. ¿Qué haces?',
        type: 'choice',
        options: [
          {
            id: 'just-count',
            text: 'Solo cuentas, no es tu problema',
            score: 50,
            feedback: 'Cumples tu tarea, pero podrías contribuir más.',
            nextSceneId: 'improvement'
          },
          {
            id: 'suggest-improvement',
            text: 'Sugieres una mejor organización',
            score: 90,
            feedback: '¡Excelente iniciativa! Proponer mejoras es valioso.',
            nextSceneId: 'improvement'
          },
          {
            id: 'reorganize-while-counting',
            text: 'Reorganizas mientras cuentas',
            score: 85,
            feedback: 'Buena iniciativa, pero asegúrate de que es apropiado.',
            nextSceneId: 'improvement'
          }
        ]
      },
      {
        id: 'improvement',
        title: 'Mejora del proceso',
        description: 'Tu supervisor está impresionado con tu curiosidad. Te pregunta si tienes ideas para mejorar el proceso.',
        type: 'choice',
        options: [
          {
            id: 'digital-suggestion',
            text: 'Sugieres un sistema digital',
            score: 90,
            feedback: 'Excelente visión de futuro. La digitalización es clave.',
            nextSceneId: 'learning-reflection'
          },
          {
            id: 'training-suggestion',
            text: 'Propones más entrenamiento',
            score: 80,
            feedback: 'Buena idea. El conocimiento es poder.',
            nextSceneId: 'learning-reflection'
          },
          {
            id: 'no-ideas',
            text: 'No se te ocurre nada',
            score: 60,
            feedback: 'Es normal no tener ideas inmediatas.',
            nextSceneId: 'learning-reflection'
          }
        ]
      },
      {
        id: 'learning-reflection',
        title: 'Reflexión sobre el aprendizaje',
        description: 'Al final del día, reflexionas sobre lo que has aprendido.',
        type: 'choice',
        options: [
          {
            id: 'process-understanding',
            text: 'Ahora entiendo mejor el proceso completo',
            score: 85,
            feedback: 'Excelente comprensión holística.',
            nextSceneId: 'completion'
          },
          {
            id: 'question-importance',
            text: 'Preguntar es más importante de lo que pensaba',
            score: 90,
            feedback: '¡Exacto! La curiosidad es la base del aprendizaje.',
            nextSceneId: 'completion'
          },
          {
            id: 'improvement-value',
            text: 'Siempre hay espacio para mejorar',
            score: 85,
            feedback: 'Excelente mentalidad de mejora continua.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Curiosidad satisfecha!',
        description: '¡Excelente trabajo! Has demostrado que la curiosidad no es solo hacer preguntas, sino buscar entender el "por qué" detrás de todo. Esta actitud te llevará lejos en cualquier trabajo. Has desbloqueado una nueva habilidad: Curiosidad y aprendizaje continuo.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Curiosidad y aprendizaje continuo!'
          }
        ]
      }
    ]
  },
  {
    id: 'resilience-flexibility',
    title: 'No todo va como esperabas',
    subtitle: 'Resiliencia y flexibilidad',
    description: 'Hoy todo parece que va a salir mal. Los planes cambian, las cosas no funcionan como esperabas, pero tú mantienes la calma y te adaptas.',
    softSkill: 'Resiliencia y flexibilidad',
    day: 'Martes (Semana 2)',
    scenario: 'Día lleno de imprevistos en el almacén. El sistema falla, los compañeros están ausentes, pero sigues adelante.',
    icon: '🔄',
    color: '#4ECDC4',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Plan A falla',
        description: 'Llegas al trabajo y te enteras de que el sistema informático está caído. Tu plan del día se va al traste. ¿Cómo reaccionas?',
        type: 'choice',
        options: [
          {
            id: 'frustrated',
            text: 'Te frustras y esperas a que se arregle',
            score: 40,
            feedback: 'Es normal frustrarse, pero intenta buscar alternativas.',
            nextSceneId: 'adaptation'
          },
          {
            id: 'find-alternatives',
            text: 'Buscas otras tareas que puedas hacer sin el sistema',
            score: 90,
            feedback: '¡Excelente flexibilidad! Adaptarte es una habilidad valiosa.',
            nextSceneId: 'adaptation'
          },
          {
            id: 'help-others',
            text: 'Ofreces ayuda a otros mientras esperas',
            score: 85,
            feedback: 'Buena iniciativa. Ayudar a otros es siempre positivo.',
            nextSceneId: 'adaptation'
          }
        ]
      },
      {
        id: 'adaptation',
        title: 'Adaptándose a la situación',
        description: 'Decides trabajar manualmente. Pero luego te enteras de que dos compañeros están ausentes por enfermedad.',
        type: 'choice',
        options: [
          {
            id: 'overwhelmed',
            text: 'Te sientes abrumad@ con tanto trabajo',
            score: 50,
            feedback: 'Es normal sentirse así, pero intenta mantener la calma.',
            nextSceneId: 'prioritization'
          },
          {
            id: 'prioritize-tasks',
            text: 'Priorizas las tareas más importantes',
            score: 90,
            feedback: '¡Excelente! Priorizar es clave en situaciones difíciles.',
            nextSceneId: 'prioritization'
          },
          {
            id: 'ask-for-help',
            text: 'Pides ayuda a otros departamentos',
            score: 85,
            feedback: 'Buena iniciativa. Pedir ayuda es una fortaleza.',
            nextSceneId: 'prioritization'
          }
        ]
      },
      {
        id: 'prioritization',
        title: 'Priorización inteligente',
        description: 'Tienes que decidir qué tareas hacer primero con recursos limitados.',
        type: 'drag-drop',
        dragDropConfig: {
          items: [
            { id: 'urgent1', text: 'Envío urgente de cliente VIP', category: 'critical' },
            { id: 'urgent2', text: 'Inventario semanal', category: 'important' },
            { id: 'urgent3', text: 'Limpieza del área', category: 'low' },
            { id: 'urgent4', text: 'Preparar reporte mensual', category: 'important' }
          ],
          targetZones: [
            { id: 'morning', title: 'Mañana (Crítico)', accepts: ['critical'] },
            { id: 'afternoon', title: 'Tarde (Importante)', accepts: ['important'] },
            { id: 'end-day', title: 'Final del día (Bajo)', accepts: ['low'] }
          ]
        },
        nextSceneId: 'unexpected-challenge'
      },
      {
        id: 'unexpected-challenge',
        title: 'Desafío inesperado',
        description: 'Un cliente llama furioso porque su pedido no llegó. El sistema está caído y no puedes verificar el estado.',
        type: 'choice',
        options: [
          {
            id: 'apologize-explain',
            text: 'Te disculpas y explicas la situación',
            score: 85,
            feedback: 'Buena comunicación. La honestidad es importante.',
            nextSceneId: 'creative-solution'
          },
          {
            id: 'promise-immediate',
            text: 'Le prometes resolverlo inmediatamente',
            score: 60,
            feedback: 'Cuidado con promesas que no puedes cumplir.',
            nextSceneId: 'creative-solution'
          },
          {
            id: 'transfer-supervisor',
            text: 'Lo transfieres a tu supervisor',
            score: 70,
            feedback: 'A veces es necesario escalar, pero intenta primero.',
            nextSceneId: 'creative-solution'
          }
        ]
      },
      {
        id: 'creative-solution',
        title: 'Solución creativa',
        description: 'Decides llamar al almacén manualmente para verificar el pedido. ¿Qué más haces?',
        type: 'choice',
        options: [
          {
            id: 'just-check',
            text: 'Solo verificas el pedido',
            score: 70,
            feedback: 'Cumples tu deber, pero podrías ir más allá.',
            nextSceneId: 'recovery'
          },
          {
            id: 'offer-alternative',
            text: 'Ofreces una alternativa si no está disponible',
            score: 95,
            feedback: '¡Excelente servicio al cliente!',
            nextSceneId: 'recovery'
          },
          {
            id: 'follow-up-plan',
            text: 'Creas un plan de seguimiento',
            score: 90,
            feedback: 'Buena planificación. La proactividad es valiosa.',
            nextSceneId: 'recovery'
          }
        ]
      },
      {
        id: 'recovery',
        title: 'Recuperación del día',
        description: 'Al final del día, el sistema vuelve a funcionar. ¿Cómo manejas el trabajo acumulado?',
        type: 'choice',
        options: [
          {
            id: 'work-overtime',
            text: 'Te quedas más tiempo para ponerte al día',
            score: 80,
            feedback: 'Buena dedicación, pero cuida tu bienestar.',
            nextSceneId: 'reflection'
          },
          {
            id: 'plan-tomorrow',
            text: 'Planificas mejor para mañana',
            score: 90,
            feedback: 'Excelente. Aprender de las dificultades es clave.',
            nextSceneId: 'reflection'
          },
          {
            id: 'delegate-tasks',
            text: 'Delegas algunas tareas',
            score: 85,
            feedback: 'Buena gestión. Saber delegar es importante.',
            nextSceneId: 'reflection'
          }
        ]
      },
      {
        id: 'reflection',
        title: 'Reflexión sobre la resiliencia',
        description: 'Reflexionas sobre cómo manejaste un día tan difícil.',
        type: 'choice',
        options: [
          {
            id: 'stayed-calm',
            text: 'Mantuve la calma y busqué soluciones',
            score: 90,
            feedback: '¡Excelente! La resiliencia es una habilidad valiosa.',
            nextSceneId: 'completion'
          },
          {
            id: 'learned-adapt',
            text: 'Aprendí a adaptarme mejor',
            score: 85,
            feedback: 'El aprendizaje es parte del crecimiento.',
            nextSceneId: 'completion'
          },
          {
            id: 'team-support',
            text: 'El apoyo del equipo fue fundamental',
            score: 80,
            feedback: 'Reconocer el valor del trabajo en equipo es importante.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Resiliencia demostrada!',
        description: '¡Increíble trabajo! Has demostrado que la resiliencia no es solo aguantar, sino adaptarse, buscar soluciones y mantener la calma ante la adversidad. Esta habilidad es invaluable en cualquier trabajo. Has desbloqueado una nueva habilidad: Resiliencia y flexibilidad.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Resiliencia y flexibilidad!'
          }
        ]
      }
    ]
  },
  {
    id: 'self-awareness',
    title: '¿Cómo me siento hoy?',
    subtitle: 'Autoconciencia',
    description: 'Hoy es un día para reflexionar sobre cómo te sientes, qué te motiva y cómo puedes mejorar. No hay respuestas correctas, solo honestidad contigo mism@.',
    softSkill: 'Autoconciencia',
    day: 'Miércoles (Semana 2)',
    scenario: 'Día de autoevaluación y reflexión personal en el trabajo.',
    icon: '🧘',
    color: '#A8E6CF',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Momento de reflexión',
        description: 'Tu supervisor te pide que reflexiones sobre tu experiencia hasta ahora. ¿Cómo te sientes realmente?',
        type: 'choice',
        options: [
          {
            id: 'confident',
            text: 'Me siento confiad@ y cómod@ con las tareas',
            score: 85,
            feedback: 'Es genial que te sientas seguro. ¿Qué te ha ayudado a llegar aquí?',
            nextSceneId: 'strengths'
          },
          {
            id: 'uncertain',
            text: 'A veces me siento insegur@, pero estoy aprendiendo',
            score: 90,
            feedback: 'La honestidad sobre las dudas es muy valiosa. Es parte del crecimiento.',
            nextSceneId: 'strengths'
          },
          {
            id: 'overwhelmed',
            text: 'Me siento un poco abrumad@ con todo lo nuevo',
            score: 75,
            feedback: 'Es normal sentirse así. ¿Qué te ayudaría a sentirte mejor?',
            nextSceneId: 'strengths'
          }
        ]
      },
      {
        id: 'strengths',
        title: 'Identificando fortalezas',
        description: 'Tu supervisor te pregunta: "¿En qué crees que eres bueno/a en este trabajo?"',
        type: 'choice',
        options: [
          {
            id: 'organization',
            text: 'Soy organizad@ y metódic@',
            score: 85,
            feedback: 'Excelente autoconocimiento. La organización es muy valiosa.',
            nextSceneId: 'challenges'
          },
          {
            id: 'communication',
            text: 'Me comunico bien con otros',
            score: 80,
            feedback: 'Buena autoevaluación. La comunicación es fundamental.',
            nextSceneId: 'challenges'
          },
          {
            id: 'learning',
            text: 'Aprendo rápido las cosas nuevas',
            score: 90,
            feedback: '¡Excelente! El aprendizaje rápido es muy valorado.',
            nextSceneId: 'challenges'
          }
        ]
      },
      {
        id: 'challenges',
        title: 'Reconociendo desafíos',
        description: 'Ahora te pregunta: "¿Qué te resulta más difícil o te gustaría mejorar?"',
        type: 'choice',
        options: [
          {
            id: 'time-management',
            text: 'Gestionar mi tiempo eficientemente',
            score: 85,
            feedback: 'Reconocer áreas de mejora es muy maduro.',
            nextSceneId: 'motivation'
          },
          {
            id: 'confidence',
            text: 'Tener más confianza en mis decisiones',
            score: 90,
            feedback: 'La autoconciencia sobre la confianza es valiosa.',
            nextSceneId: 'motivation'
          },
          {
            id: 'technical-skills',
            text: 'Algunas habilidades técnicas',
            score: 80,
            feedback: 'Es normal querer mejorar habilidades técnicas.',
            nextSceneId: 'motivation'
          }
        ]
      },
      {
        id: 'motivation',
        title: '¿Qué te motiva?',
        description: 'Te preguntan qué te motiva más en el trabajo.',
        type: 'choice',
        options: [
          {
            id: 'helping-others',
            text: 'Ayudar a otros y trabajar en equipo',
            score: 90,
            feedback: 'Excelente motivación. El trabajo en equipo es fundamental.',
            nextSceneId: 'emotional-awareness'
          },
          {
            id: 'learning-growth',
            text: 'Aprender cosas nuevas y crecer',
            score: 95,
            feedback: '¡Perfecto! La motivación por aprender es muy valiosa.',
            nextSceneId: 'emotional-awareness'
          },
          {
            id: 'achievement',
            text: 'Completar tareas y ver resultados',
            score: 85,
            feedback: 'Buena motivación. Los logros son importantes.',
            nextSceneId: 'emotional-awareness'
          }
        ]
      },
      {
        id: 'emotional-awareness',
        title: 'Conciencia emocional',
        description: 'Durante el día, te sientes frustrad@ por un error que cometiste. ¿Cómo manejas esta emoción?',
        type: 'choice',
        options: [
          {
            id: 'acknowledge-feel',
            text: 'Reconozco que me siento frustrad@ y busco aprender',
            score: 95,
            feedback: '¡Excelente! Reconocer emociones es autoconciencia pura.',
            nextSceneId: 'growth-mindset'
          },
          {
            id: 'ignore-feeling',
            text: 'Intento ignorar la frustración y seguir trabajando',
            score: 60,
            feedback: 'Es importante reconocer las emociones para manejarlas.',
            nextSceneId: 'growth-mindset'
          },
          {
            id: 'blame-others',
            text: 'Me enfado y busco a quién culpar',
            score: 40,
            feedback: 'La responsabilidad personal es parte del crecimiento.',
            nextSceneId: 'growth-mindset'
          }
        ]
      },
      {
        id: 'growth-mindset',
        title: 'Mentalidad de crecimiento',
        description: 'Tu supervisor te dice que todos cometemos errores. ¿Cómo respondes?',
        type: 'choice',
        options: [
          {
            id: 'learn-from-mistake',
            text: 'Agradezco el feedback y pienso en cómo mejorar',
            score: 95,
            feedback: '¡Excelente mentalidad de crecimiento!',
            nextSceneId: 'self-improvement'
          },
          {
            id: 'defensive',
            text: 'Me pongo a la defensiva y justifico el error',
            score: 50,
            feedback: 'Es normal, pero la apertura al feedback es importante.',
            nextSceneId: 'self-improvement'
          },
          {
            id: 'apologize-excessively',
            text: 'Me disculpo repetidamente',
            score: 70,
            feedback: 'La responsabilidad es buena, pero no te castigues.',
            nextSceneId: 'self-improvement'
          }
        ]
      },
      {
        id: 'self-improvement',
        title: 'Plan de mejora personal',
        description: 'Basándote en esta reflexión, ¿qué te gustaría trabajar más?',
        type: 'choice',
        options: [
          {
            id: 'communication-skills',
            text: 'Mejorar mis habilidades de comunicación',
            score: 85,
            feedback: 'Excelente elección. La comunicación es clave.',
            nextSceneId: 'completion'
          },
          {
            id: 'technical-skills',
            text: 'Desarrollar más habilidades técnicas',
            score: 80,
            feedback: 'Buena decisión. El desarrollo técnico es valioso.',
            nextSceneId: 'completion'
          },
          {
            id: 'emotional-intelligence',
            text: 'Trabajar en mi inteligencia emocional',
            score: 90,
            feedback: '¡Excelente! La IE es fundamental en el trabajo.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Autoconciencia desarrollada!',
        description: '¡Fantástico trabajo! Has demostrado que la autoconciencia no es solo conocerse, sino ser honesto con uno mismo, reconocer fortalezas y áreas de mejora, y tener la voluntad de crecer. Esta habilidad es la base de todo desarrollo personal y profesional. Has desbloqueado una nueva habilidad: Autoconciencia.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Autoconciencia!'
          }
        ]
      }
    ]
  },
  {
    id: 'empathy',
    title: 'Ponte en sus zapatos',
    subtitle: 'Empatía',
    description: 'Hoy vas a encontrarte con situaciones donde necesitarás entender cómo se sienten otras personas. La empatía es clave para trabajar bien en equipo.',
    softSkill: 'Empatía',
    day: 'Jueves (Semana 2)',
    scenario: 'Diferentes situaciones donde debes mostrar comprensión hacia compañeros y clientes.',
    icon: '❤️',
    color: '#FF8A80',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Compañero estresado',
        description: 'Tu compañero Alex llega tarde y parece muy estresado. Te dice que ha tenido problemas personales. ¿Qué haces?',
        type: 'choice',
        options: [
          {
            id: 'ignore',
            text: 'Sigues con tu trabajo sin decir nada',
            score: 40,
            feedback: 'Considera que un pequeño gesto puede ayudar mucho.',
            nextSceneId: 'understanding'
          },
          {
            id: 'offer-help',
            text: 'Le ofreces ayuda con sus tareas',
            score: 90,
            feedback: '¡Excelente empatía! Ofrecer ayuda es muy valioso.',
            nextSceneId: 'understanding'
          },
          {
            id: 'listen',
            text: 'Le preguntas si quiere hablar sobre ello',
            score: 85,
            feedback: 'Buena iniciativa. A veces solo necesitamos ser escuchados.',
            nextSceneId: 'understanding'
          }
        ]
      },
      {
        id: 'understanding',
        title: 'Entendiendo perspectivas',
        description: 'Alex te cuenta que su madre está enferma y tiene que cuidarla. ¿Cómo respondes?',
        type: 'choice',
        options: [
          {
            id: 'express-concern',
            text: 'Expresas tu preocupación y comprensión',
            score: 95,
            feedback: '¡Perfecto! Mostrar preocupación genuina es empatía pura.',
            nextSceneId: 'practical-support'
          },
          {
            id: 'give-advice',
            text: 'Le das consejos sobre cómo manejar la situación',
            score: 70,
            feedback: 'Es bienintencionado, pero a veces solo necesitamos comprensión.',
            nextSceneId: 'practical-support'
          },
          {
            id: 'change-subject',
            text: 'Cambias de tema para distraerlo',
            score: 50,
            feedback: 'Evitar el tema puede hacer que se sienta peor.',
            nextSceneId: 'practical-support'
          }
        ]
      },
      {
        id: 'practical-support',
        title: 'Apoyo práctico',
        description: 'Alex parece más tranquilo después de hablar. ¿Qué más puedes hacer?',
        type: 'choice',
        options: [
          {
            id: 'flexible-schedule',
            text: 'Te ofreces a ser más flexible con horarios',
            score: 90,
            feedback: '¡Excelente! El apoyo práctico es muy valioso.',
            nextSceneId: 'client-empathy'
          },
          {
            id: 'emotional-support',
            text: 'Le dices que puede contar contigo',
            score: 85,
            feedback: 'Buena oferta de apoyo emocional.',
            nextSceneId: 'client-empathy'
          },
          {
            id: 'professional-distance',
            text: 'Mantienes distancia profesional',
            score: 60,
            feedback: 'Es importante mantener límites, pero el apoyo es valioso.',
            nextSceneId: 'client-empathy'
          }
        ]
      },
      {
        id: 'client-empathy',
        title: 'Empatía con clientes',
        description: 'Más tarde, un cliente llama muy molesto porque su pedido llegó tarde. ¿Cómo manejas la situación?',
        type: 'choice',
        options: [
          {
            id: 'acknowledge-feeling',
            text: 'Reconoces su frustración y te disculpas',
            score: 90,
            feedback: '¡Excelente! Reconocer emociones es clave.',
            nextSceneId: 'perspective-taking'
          },
          {
            id: 'explain-reasons',
            text: 'Le explicas por qué se retrasó',
            score: 75,
            feedback: 'La explicación es importante, pero primero reconoce la emoción.',
            nextSceneId: 'perspective-taking'
          },
          {
            id: 'defend-company',
            text: 'Defiendes a la empresa',
            score: 40,
            feedback: 'Defender no resuelve la frustración del cliente.',
            nextSceneId: 'perspective-taking'
          }
        ]
      },
      {
        id: 'perspective-taking',
        title: 'Tomar perspectiva',
        description: 'Piensas en por qué el cliente está tan molesto. ¿Qué consideras?',
        type: 'choice',
        options: [
          {
            id: 'business-impact',
            text: 'El retraso puede haber afectado su negocio',
            score: 95,
            feedback: '¡Excelente! Considerar el impacto en otros es empatía avanzada.',
            nextSceneId: 'emotional-regulation'
          },
          {
            id: 'personal-stress',
            text: 'Puede estar pasando por un momento difícil',
            score: 85,
            feedback: 'Buena consideración de factores personales.',
            nextSceneId: 'emotional-regulation'
          },
          {
            id: 'expectations',
            text: 'Tenía expectativas altas del servicio',
            score: 80,
            feedback: 'Entender expectativas es importante.',
            nextSceneId: 'emotional-regulation'
          }
        ]
      },
      {
        id: 'emotional-regulation',
        title: 'Regulación emocional',
        description: 'El cliente sigue molesto y te habla de manera grosera. ¿Cómo manejas tu propia emoción?',
        type: 'choice',
        options: [
          {
            id: 'stay-calm',
            text: 'Mantienes la calma y sigues siendo empático',
            score: 95,
            feedback: '¡Perfecto! La regulación emocional es fundamental.',
            nextSceneId: 'team-empathy'
          },
          {
            id: 'get-defensive',
            text: 'Te pones a la defensiva',
            score: 40,
            feedback: 'La defensividad no ayuda a resolver conflictos.',
            nextSceneId: 'team-empathy'
          },
          {
            id: 'transfer-call',
            text: 'Transfieres la llamada a tu supervisor',
            score: 70,
            feedback: 'A veces es necesario, pero intenta primero.',
            nextSceneId: 'team-empathy'
          }
        ]
      },
      {
        id: 'team-empathy',
        title: 'Empatía en equipo',
        description: 'Al final del día, tu equipo está cansado. ¿Cómo contribuyes al ambiente?',
        type: 'choice',
        options: [
          {
            id: 'positive-energy',
            text: 'Traes energía positiva y motivación',
            score: 90,
            feedback: '¡Excelente! La empatía también es levantar el ánimo.',
            nextSceneId: 'completion'
          },
          {
            id: 'acknowledge-effort',
            text: 'Reconoces el esfuerzo de todos',
            score: 85,
            feedback: 'Buena manera de mostrar aprecio.',
            nextSceneId: 'completion'
          },
          {
            id: 'focus-work',
            text: 'Te enfocas solo en terminar el trabajo',
            score: 60,
            feedback: 'El trabajo es importante, pero el equipo también.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Empatía desarrollada!',
        description: '¡Fantástico trabajo! Has demostrado que la empatía no es solo sentir pena por otros, sino entender sus perspectivas, mostrar compasión genuina y ofrecer apoyo tanto emocional como práctico. Esta habilidad es fundamental para crear relaciones laborales saludables y un ambiente de trabajo positivo. Has desbloqueado una nueva habilidad: Empatía.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Empatía!'
          }
        ]
      }
    ]
  },
  {
    id: 'time-management',
    title: 'Tiempo al tiempo',
    subtitle: 'Gestión del tiempo',
    description: 'Hoy tienes muchas tareas y poco tiempo. Necesitarás priorizar, organizarte y ser eficiente. ¿Puedes manejar la presión?',
    softSkill: 'Gestión del tiempo',
    day: 'Viernes (Semana 2)',
    scenario: 'Día con múltiples tareas urgentes y tiempo limitado para completarlas.',
    icon: '⏰',
    color: '#6C5CE7',
    completed: false,
    logs: [],
    scenes: [
      {
        id: 'intro',
        title: 'Muchas tareas, poco tiempo',
        description: 'Te han dado 5 tareas para completar antes de las 5 de la tarde. Son las 9 de la mañana. ¿Cómo te organizas?',
        type: 'drag-drop',
        dragDropConfig: {
          items: [
            { id: 'task1', text: 'Revisar inventario urgente', category: 'high' },
            { id: 'task2', text: 'Preparar informe semanal', category: 'medium' },
            { id: 'task3', text: 'Responder emails pendientes', category: 'medium' },
            { id: 'task4', text: 'Organizar archivos', category: 'low' },
            { id: 'task5', text: 'Reunión de equipo', category: 'high' }
          ],
          targetZones: [
            { id: 'morning', title: 'Mañana (9-12)', accepts: ['high'] },
            { id: 'afternoon', title: 'Tarde (12-5)', accepts: ['medium', 'low'] }
          ]
        },
        nextSceneId: 'interruption'
      },
      {
        id: 'interruption',
        title: 'Interrupción inesperada',
        description: 'A las 10:30, tu supervisor te pide que atiendas una emergencia. ¿Qué haces con tu plan?',
        type: 'choice',
        options: [
          {
            id: 'adapt-plan',
            text: 'Adaptas tu plan para incluir la emergencia',
            score: 90,
            feedback: '¡Excelente! La flexibilidad es clave en la gestión del tiempo.',
            nextSceneId: 'efficiency'
          },
          {
            id: 'refuse-emergency',
            text: 'Le dices que estás muy ocupada o ocupada',
            score: 40,
            feedback: 'Las emergencias son prioritarias. Aprende a adaptarte.',
            nextSceneId: 'efficiency'
          },
          {
            id: 'panic',
            text: 'Te estresas y no sabes qué hacer',
            score: 50,
            feedback: 'Mantén la calma y reorganiza tus prioridades.',
            nextSceneId: 'efficiency'
          }
        ]
      },
      {
        id: 'efficiency',
        title: 'Trabajando eficientemente',
        description: 'Para ser más eficiente, ¿qué estrategia usas?',
        type: 'choice',
        options: [
          {
            id: 'time-blocks',
            text: 'Trabajas en bloques de tiempo concentrado',
            score: 95,
            feedback: '¡Excelente! Los bloques de tiempo aumentan la productividad.',
            nextSceneId: 'delegation'
          },
          {
            id: 'multitask',
            text: 'Intentas hacer varias cosas a la vez',
            score: 60,
            feedback: 'El multitasking puede reducir la calidad del trabajo.',
            nextSceneId: 'delegation'
          },
          {
            id: 'take-breaks',
            text: 'Tomas descansos regulares para mantener energía',
            score: 85,
            feedback: 'Buena estrategia. Los descansos mejoran la productividad.',
            nextSceneId: 'delegation'
          }
        ]
      },
      {
        id: 'delegation',
        title: 'Delegación inteligente',
        description: 'Te das cuenta de que no vas a poder completar todo. ¿Qué haces?',
        type: 'choice',
        options: [
          {
            id: 'ask-help',
            text: 'Pides ayuda a compañeros',
            score: 90,
            feedback: '¡Excelente! Saber pedir ayuda es una fortaleza.',
            nextSceneId: 'deadline-pressure'
          },
          {
            id: 'work-overtime',
            text: 'Te quedas más tiempo para completar todo',
            score: 70,
            feedback: 'A veces es necesario, pero no debe ser la norma.',
            nextSceneId: 'deadline-pressure'
          },
          {
            id: 'prioritize-again',
            text: 'Reevalúas y dejas algunas tareas para mañana',
            score: 85,
            feedback: 'Buena decisión. Es mejor hacer bien lo prioritario.',
            nextSceneId: 'deadline-pressure'
          }
        ]
      },
      {
        id: 'deadline-pressure',
        title: 'Presión de deadline',
        description: 'Son las 4:30 y aún tienes 2 tareas pendientes. ¿Cómo manejas la presión?',
        type: 'choice',
        options: [
          {
            id: 'stay-focused',
            text: 'Mantienes la calma y te enfocas en completar lo posible',
            score: 95,
            feedback: '¡Perfecto! Mantener la calma bajo presión es invaluable.',
            nextSceneId: 'quality-vs-speed'
          },
          {
            id: 'rush-work',
            text: 'Trabajas muy rápido sacrificando calidad',
            score: 60,
            feedback: 'La calidad es importante. Busca un balance.',
            nextSceneId: 'quality-vs-speed'
          },
          {
            id: 'communicate-delay',
            text: 'Comunicas el retraso y pides más tiempo',
            score: 80,
            feedback: 'Buena comunicación. Es mejor ser honesto.',
            nextSceneId: 'quality-vs-speed'
          }
        ]
      },
      {
        id: 'quality-vs-speed',
        title: 'Calidad vs velocidad',
        description: 'Tu supervisor te pregunta si prefieres entregar todo a tiempo o con mejor calidad. ¿Qué respondes?',
        type: 'choice',
        options: [
          {
            id: 'quality-first',
            text: 'Prefiero calidad sobre velocidad',
            score: 85,
            feedback: 'Buena priorización. La calidad es importante.',
            nextSceneId: 'reflection'
          },
          {
            id: 'balance-approach',
            text: 'Busco un balance entre calidad y velocidad',
            score: 95,
            feedback: '¡Excelente! El balance es la clave del éxito.',
            nextSceneId: 'reflection'
          },
          {
            id: 'speed-first',
            text: 'Prefiero velocidad para cumplir deadlines',
            score: 70,
            feedback: 'Los deadlines son importantes, pero la calidad también.',
            nextSceneId: 'reflection'
          }
        ]
      },
      {
        id: 'reflection',
        title: 'Reflexión sobre el tiempo',
        description: 'Al final del día, reflexionas sobre tu gestión del tiempo. ¿Qué aprendiste?',
        type: 'choice',
        options: [
          {
            id: 'planning-importance',
            text: 'La planificación es fundamental',
            score: 90,
            feedback: '¡Exacto! La planificación es la base de la gestión del tiempo.',
            nextSceneId: 'completion'
          },
          {
            id: 'flexibility-value',
            text: 'La flexibilidad es tan importante como la planificación',
            score: 95,
            feedback: '¡Perfecto! El balance entre planificación y flexibilidad es clave.',
            nextSceneId: 'completion'
          },
          {
            id: 'teamwork-helps',
            text: 'El trabajo en equipo ayuda a gestionar mejor el tiempo',
            score: 85,
            feedback: 'Excelente observación. La colaboración es valiosa.',
            nextSceneId: 'completion'
          }
        ]
      },
      {
        id: 'completion',
        title: '¡Gestión del tiempo dominada!',
        description: '¡Increíble trabajo! Has demostrado que la gestión del tiempo no es solo hacer listas, sino priorizar inteligentemente, adaptarse a cambios, trabajar eficientemente y mantener la calma bajo presión. Esta habilidad es fundamental para el éxito en cualquier trabajo. Has desbloqueado una nueva habilidad: Gestión del tiempo.',
        type: 'choice',
        options: [
          {
            id: 'continue',
            text: 'Continuar al siguiente día',
            score: 100,
            feedback: '¡Has desbloqueado la habilidad: Gestión del tiempo!'
          }
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