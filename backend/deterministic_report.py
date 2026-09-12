#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
deterministic_report.py

Generador de informes de empleabilidad SIN IA generativa: construye el mismo
contrato de datos que el pipeline de Gemini (ver `backend/new_report_schema.py`
-- Chunk1Base + Chunk2Competencias + Chunk3Accion) usando únicamente:

- Heurísticas deterministas sobre el CV (`backend/cv_structure_analyzer.py`:
  regex + puntuación por reglas, sin LLM).
- Los resultados estructurados de los minijuegos (`softSkills`).
- Las preferencias laborales indicadas por el candidato.

Es el motor usado cuando `ENABLE_AI_REPORT` está desactivado (por defecto) o
cuando el intento de IA falla, para garantizar que el informe SIEMPRE se
genera, al instante, sin depender de cuotas ni disponibilidad de terceros.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any, Dict, List

try:
    from backend.cv_structure_analyzer import (
        analyze_cv_structure_from_bytes,
        extract_contact_info,
        SECTION_PATTERNS,
    )
except ImportError:
    from cv_structure_analyzer import (
        analyze_cv_structure_from_bytes,
        extract_contact_info,
        SECTION_PATTERNS,
    )

_ANY_SECTION_HEADER_RE = re.compile(
    "|".join(f"(?:{pat})" for pat in SECTION_PATTERNS.values()), re.IGNORECASE
)

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "español": "Español", "castellano": "Español",
    "inglés": "Inglés", "ingles": "Inglés",
    "francés": "Francés", "frances": "Francés",
    "alemán": "Alemán", "aleman": "Alemán",
    "portugués": "Portugués", "portugues": "Portugués",
    "italiano": "Italiano",
    "catalán": "Catalán", "catalan": "Catalán",
    "euskera": "Euskera", "gallego": "Gallego",
    "chino": "Chino", "mandarín": "Chino", "mandarin": "Chino",
    "árabe": "Árabe", "arabe": "Árabe",
}

LEVEL_PATTERN = re.compile(
    r"\b(nativ[oa]|c2|c1|b2|b1|a2|a1|fluid[oa]|avanzad[oa]|intermedi[oa]|básic[oa]|basic[oa]|alto|medio|bajo)\b",
    re.IGNORECASE,
)

TOOL_KEYWORDS = [
    "Excel", "Word", "PowerPoint", "Outlook", "Access", "Google Sheets", "Google Docs",
    "Photoshop", "Illustrator", "InDesign", "Premiere", "After Effects", "Figma", "Canva",
    "AutoCAD", "SolidWorks", "SAP", "Salesforce", "CRM", "WordPress", "Shopify",
    "Python", "Java", "JavaScript", "SQL", "HTML", "CSS", "React",
    "Power BI", "Tableau", "QuickBooks", "Contaplus", "Sage",
    "Zendesk", "HubSpot", "Mailchimp", "SEO", "Google Analytics", "Google Ads",
    "TPV", "PRL", "Manipulador de alimentos", "Carnet de conducir", "Carretilla elevadora",
]

# Erratas frecuentes en nombres de software/herramientas -- citarlas de forma
# textual y concreta ("'InDesing' por InDesign") aporta mucho más valor real
# que un aviso genérico de "cuida la ortografía", y es justo el tipo de
# hallazgo específico que hace que un informe se sienta escrito a medida.
TYPO_FIXES = {
    "indesing": "InDesign", "ilustrator": "Illustrator",
    "fotoshop": "Photoshop", "photosop": "Photoshop", "power point": "PowerPoint",
    "exel": "Excel", "excell": "Excel", "wordpres": "WordPress",
    "javascrip": "JavaScript", "java script": "JavaScript",
}


def _detect_typos(text: str) -> List[str]:
    if not text:
        return []
    lower = text.lower()
    found = []
    for wrong, right in TYPO_FIXES.items():
        if wrong == right.lower():
            continue
        if re.search(rf"\b{re.escape(wrong)}\b", lower):
            found.append(f"'{wrong.title()}' en vez de '{right}'")
    return found[:3]


WORK_MODE_TEXT = {
    "remoto": "entornos 100% remotos, con buena conexión a internet y autonomía para organizar el propio tiempo",
    "presencial": "entornos presenciales, con contacto directo con el equipo y rutinas estructuradas",
    "híbrido": "un esquema híbrido que combine trabajo presencial y remoto según la tarea",
    "hibrido": "un esquema híbrido que combine trabajo presencial y remoto según la tarea",
}

# Oficios/áreas que por su propia naturaleza requieren presencia física (trato
# directo con personas, manipulación de materiales/herramientas, uso de
# instalaciones concretas) -- si el candidato pide "remoto" para uno de estos,
# el informe debe señalar la incoherencia en vez de repetirla sin más. Lista
# no exhaustiva centrada en los sectores habituales de los candidatos de
# Teamworkz (no pretende cubrir cualquier profesión posible).
ON_SITE_ONLY_KEYWORDS = [
    "maquilla", "peluquer", "estetic", "manicur", "pedicur", "barber", "masaj",
    "fisioterap", "enfermer", "auxiliar de enfermer", "medicin", "odontolog",
    "farmac", "cocin", "camarer", "hosteler", "limpieza", "conductor",
    "conduccion", "transporte", "repart", "logistic", "almacen", "mozo de almacen",
    "construccion", "electricist", "fontaner", "mecanic", "jardiner",
    "seguridad", "vigilante", "dependient", "comercio", "cajer",
    "cuidado de personas", "cuidador", "geriatr", "peluqueria canina",
    "restauracion", "panader", "carnicer", "peix", "reposicion",
]


def _requires_on_site_presence(area: str) -> bool:
    a = area.lower()
    return any(kw in a for kw in ON_SITE_ONLY_KEYWORDS)


# Cuando el oficio elegido no es compatible con "remoto", un aviso genérico
# ("no es viable") aporta poco. Mucho más valioso es proponer 2 alternativas
# de pivote CONCRETAS y específicas del sector -- exactamente lo que hacía el
# informe de referencia generado con IA para "maquilladora" (Consultora de
# Belleza Virtual, Customer Experience en e-commerce de belleza...). Se
# agrupan los ON_SITE_ONLY_KEYWORDS en familias de sector con su propio set
# de roles remotos y herramientas relevantes.
PIVOT_FAMILIES: List[Dict[str, Any]] = [
    {
        "match": ["maquilla", "peluquer", "estetic", "manicur", "pedicur", "barber", "masaj", "peluqueria canina"],
        "roles": [
            ("Consultor/a de Belleza y Estética Virtual (Beauty Advisor Online)",
             "combinando tu empatía y tu experiencia de trato directo con clientes para asesorar sobre productos y rutinas de belleza a distancia, en vez de aplicar el servicio de forma física."),
            ("Customer Experience Specialist en E-Commerce de Cosmética/Estética",
             "capitalizando tu experiencia de atención al público para optimizar el soporte técnico y comercial de una tienda online del sector."),
        ],
        "tools": [
            ("Perfect Corp / YouCam (realidad aumentada)", "Plataforma de probadores virtuales de maquillaje y cosmética para asesorar a clientes sobre tonos y acabados a distancia."),
            ("Zendesk / Freshdesk", "Software de atención al cliente omnicanal, habitual en e-commerce de belleza y cosmética."),
        ],
    },
    {
        "match": ["fisioterap", "enfermer", "auxiliar de enfermer", "medicin", "odontolog", "farmac",
                  "cuidado de personas", "cuidador", "geriatr"],
        "roles": [
            ("Teleoperador/a de Asesoramiento en Salud y Bienestar",
             "aprovechando tus conocimientos del sector sanitario/asistencial para orientar a pacientes o familias por teléfono o chat, sin ejecutar el cuidado físico directo."),
            ("Gestor/a de Citas y Atención al Paciente (Centro Sanitario)",
             "aplicando tu conocimiento del sector para coordinar agendas, resolver dudas y dar soporte administrativo a pacientes de forma remota."),
        ],
        "tools": [
            ("Doctoralia / software de gestión de citas médicas", "Herramienta habitual para coordinar agendas y comunicación con pacientes en remoto."),
            ("Zendesk / Freshdesk", "Software de atención al cliente para resolver dudas de pacientes o familiares por chat, email o teléfono."),
        ],
    },
    {
        "match": ["cocin", "camarer", "hosteler", "panader", "carnicer", "peix", "restauracion"],
        "roles": [
            ("Gestor/a de Reservas y Atención al Cliente Online (Hostelería)",
             "aplicando tu experiencia de trato directo con clientes a la gestión de reservas, reseñas y atención por redes/chat de un negocio de hostelería."),
            ("Community Manager / Gestor/a de Pedidos Online para Restauración",
             "aprovechando el conocimiento real del sector para gestionar redes sociales, pedidos a domicilio y reputación online de un negocio de hostelería."),
        ],
        "tools": [
            ("TheFork / Zenchef / Glovo-Uber Eats (panel de gestión)", "Plataformas de gestión de reservas y pedidos online habituales en hostelería."),
            ("Instagram/Facebook Business Suite", "Gestión de redes sociales y atención al cliente online para negocios de restauración."),
        ],
    },
    {
        "match": ["limpieza"],
        "roles": [
            ("Coordinador/a de Equipos de Limpieza (gestión remota de turnos)",
             "aplicando tu conocimiento real del oficio para planificar turnos, controlar incidencias y coordinar equipos desde una oficina o en remoto, sin ejecutar el servicio tú misma/o."),
            ("Atención al Cliente en Empresa de Servicios de Limpieza",
             "resolviendo incidencias, presupuestos y reclamaciones de clientes por teléfono o chat, apoyándote en el conocimiento directo del servicio."),
        ],
        "tools": [
            ("Software de gestión de turnos (When I Work, Deputy)", "Herramientas para planificar y coordinar equipos de limpieza a distancia."),
            ("Zendesk / Freshdesk", "Software de atención al cliente para gestionar incidencias y reclamaciones del servicio."),
        ],
    },
    {
        "match": ["conductor", "conduccion", "transporte", "repart", "logistic", "almacen",
                  "mozo de almacen", "reposicion"],
        "roles": [
            ("Coordinador/a de Operaciones y Atención al Cliente en Logística",
             "aplicando tu conocimiento real de la operativa de almacén/reparto para coordinar rutas, incidencias y comunicación con clientes desde una posición de gestión, no de ejecución física."),
            ("Gestor/a de Inventario y Soporte de E-Commerce",
             "aprovechando la experiencia práctica en almacén para dar soporte remoto a la gestión de stock, pedidos e incidencias de una tienda online."),
        ],
        "tools": [
            ("SAP / Odoo (gestión de inventario)", "Software de gestión logística y de stock habitual en empresas con operativa de almacén."),
            ("Zendesk / Freshdesk", "Software de atención al cliente para gestionar incidencias de pedidos y envíos."),
        ],
    },
    {
        "match": ["construccion", "electricist", "fontaner", "mecanic", "jardiner"],
        "roles": [
            ("Asesor/a Técnico de Atención al Cliente (sector reformas/instalaciones)",
             "aplicando el conocimiento técnico del oficio para atender presupuestos, dudas técnicas e incidencias de clientes por teléfono o chat."),
            ("Gestor/a de Presupuestos y Seguimiento de Obra Online",
             "aprovechando la experiencia práctica en el oficio para elaborar y hacer seguimiento remoto de presupuestos y pedidos de material."),
        ],
        "tools": [
            ("Software de presupuestos (Cype, Presto)", "Herramientas habituales para elaborar y gestionar presupuestos de obra o instalaciones a distancia."),
            ("WhatsApp Business / Zendesk", "Canales de atención al cliente para resolver dudas técnicas o de seguimiento de obra en remoto."),
        ],
    },
    {
        "match": ["seguridad", "vigilante", "dependient", "comercio", "cajer"],
        "roles": [
            ("Teleoperador/a de Atención al Cliente y Ventas",
             "trasladando la experiencia de trato directo con el público en tienda a un canal de atención telefónica, chat o email."),
            ("Gestor/a de Tienda Online (E-Commerce)",
             "aplicando el conocimiento del punto de venta físico a la gestión de un catálogo, pedidos y atención al cliente de una tienda online."),
        ],
        "tools": [
            ("Shopify / WooCommerce", "Plataformas de tienda online donde aplicar la experiencia de venta y atención al cliente presencial."),
            ("Zendesk / Freshdesk", "Software de atención al cliente omnicanal para resolver consultas y reclamaciones a distancia."),
        ],
    },
]


def _pivot_family(area: str) -> Dict[str, Any]:
    a = area.lower()
    for family in PIVOT_FAMILIES:
        if any(kw in a for kw in family["match"]):
            return family
    # Familia genérica de respaldo si el área choca con ON_SITE_ONLY_KEYWORDS
    # pero no encaja en ninguna familia concreta (lista no exhaustiva).
    return {
        "roles": [
            ("Teleoperador/a de Atención al Cliente",
             "trasladando la experiencia práctica del oficio a un canal de atención telefónica, chat o email, sin necesitar presencia física."),
            ("Gestor/a Administrativo/a Online",
             "aplicando el conocimiento del sector a tareas de gestión, seguimiento y coordinación que sí pueden realizarse en remoto."),
        ],
        "tools": [
            ("Zendesk / Freshdesk", "Software de atención al cliente omnicanal, útil en la mayoría de pivotes hacia el trabajo remoto."),
            ("LinkedIn", "Visibilidad profesional y acceso a ofertas remotas relacionadas con el sector de origen."),
        ],
    }


def _normalize_key(text: str) -> str:
    """minúsculas + sin acentos, para casar nombres de habilidad/área contra
    los diccionarios de contenido aunque vengan con capitalización distinta
    (los minijuegos no son consistentes: 'Pensamiento Analítico' vs
    'Pensamiento analítico')."""
    nfkd = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# Banco de contenido para las 10 competencias fijas que evalúan los minijuegos
# (backend/../nuevo-frontend/src/data/games.ts: softSkill de cada juego). Al
# ser un conjunto cerrado y conocido, se puede escribir contenido específico
# y de calidad "consultora" para cada una en vez de una plantilla genérica --
# esto es lo que de verdad separa un informe con valor real de uno que "solo
# rellena campos" (feedback real de una usuaria de prueba, Ester/Teamworkz).
# Si algún día se añade un minijuego nuevo con un nombre no listado aquí, el
# código cae a una plantilla genérica (ver _generic_competency_content) en
# vez de fallar.
# ---------------------------------------------------------------------------
COMPETENCY_CONTENT: Dict[str, Dict[str, Any]] = {
    "toma de decisiones": {
        "que_mide": "Capacidad para seleccionar la mejor alternativa posible ante escenarios con información incompleta y tiempo limitado.",
        "alto": {
            "explicacion": "Muestra agilidad real para decidir bajo presión sin caer en la parálisis por análisis, sopesando riesgo y beneficio con criterio propio. En el día a día esto se traduce en autonomía genuina: puede resolver imprevistos operativos sin necesitar validación constante de un superior.",
            "entrevista": "Puede argumentar este resultado describiendo una situación real en la que decidió rápido con información limitada y el desenlace fue positivo para el equipo o el cliente.",
            "fortaleza": "aporta autonomía real en la resolución de imprevistos, un activo que reduce la carga de supervisión de cualquier equipo.",
        },
        "medio": {
            "explicacion": "Equilibrio funcional entre velocidad y prudencia: tiende a recabar información suficiente antes de decidir, lo que reduce errores pero puede ralentizar la resolución cuando la incertidumbre es alta. Es un perfil fiable para decidir dentro de protocolos ya establecidos.",
            "entrevista": "Puede explicar cómo prioriza opciones cuando el tiempo o los recursos son limitados, mostrando el criterio concreto que aplica antes de decidir.",
        },
        "bajo": {
            "explicacion": "Dificultad para decidir con autonomía cuando la información es ambigua o incompleta, con tendencia a posponer la decisión o a buscar validación externa antes de actuar. Sin trabajo activo, esto puede generar cuellos de botella en tareas que exigen resolución rápida sin supervisión constante.",
            "entrevista": "Puede preparar respuestas mostrando qué está haciendo activamente para agilizar su criterio propio, con un ejemplo reciente de mejora.",
            "porque_afecta": "puede generar dependencia de la supervisión directa y ralentizar procesos en entornos que exigen autonomía operativa real.",
            "acciones": [
                "Practicar la regla de 'decisión en 2 minutos' en situaciones cotidianas de bajo riesgo, para entrenar la agilidad de criterio.",
                "Anotar 3 decisiones recientes señalando qué información faltó y en qué momento se podría haber decidido antes.",
                "Pedir feedback inmediato a un mentor o responsable tras cada decisión relevante, para calibrar el propio criterio con datos reales.",
            ],
        },
    },
    "pensamiento analitico": {
        "que_mide": "Capacidad para descomponer información compleja en partes manejables y detectar patrones o inconsistencias.",
        "alto": {
            "explicacion": "Descompone con solidez problemas complejos en componentes manejables y procesa datos estructurados con precisión. En el trabajo diario esto se traduce en evaluaciones rigurosas y control de calidad fiable, aportando criterio lógico al analizar requisitos y optimizar procesos.",
            "entrevista": "Puede argumentar este resultado explicando su método para auditar información o detectar errores en un proceso concreto.",
            "fortaleza": "es una de las bases más sólidas del perfil: aporta rigor metodológico en cualquier tarea de análisis, control de calidad o estructuración de procesos.",
        },
        "medio": {
            "explicacion": "Nivel funcional para categorizar datos y detectar inconsistencias evidentes, aunque en escenarios muy ambiguos puede necesitar apoyo o más tiempo para llegar a conclusiones sólidas. Es suficiente para tareas de revisión y control dentro de procesos ya definidos.",
            "entrevista": "Puede explicar un caso en el que detectó un error o inconsistencia siguiendo un proceso paso a paso.",
        },
        "bajo": {
            "explicacion": "Le cuesta descomponer información compleja o detectar patrones no evidentes, lo que puede traducirse en errores de interpretación en tareas que exigen análisis fino de datos. Sin refuerzo, esto limita su autonomía en procesos que requieren auditar o estructurar información compleja.",
            "entrevista": "Puede mostrar madurez señalando qué método está incorporando (checklists, plantillas) para reforzar el análisis sistemático.",
            "porque_afecta": "puede generar errores de interpretación en tareas que exigen procesar información compleja o detectar inconsistencias con rigor.",
            "acciones": [
                "Usar checklists o plantillas estructuradas al analizar cualquier información compleja, en vez de fiarse solo de la primera lectura.",
                "Practicar con ejercicios cortos de lógica o análisis de datos (gratuitos online) durante 15-20 minutos varias veces por semana.",
                "Pedir a un compañero que revise el mismo análisis por separado y comparar conclusiones para detectar puntos ciegos propios.",
            ],
        },
    },
    "creatividad": {
        "que_mide": "Capacidad para generar ideas novedosas, enfoques divergentes o soluciones no evidentes ante un mismo problema.",
        "alto": {
            "explicacion": "Genera con naturalidad ideas y enfoques que se salen de lo convencional, aportando soluciones diferenciadas ante problemas repetidos. En el trabajo esto se traduce en propuestas visuales o de proceso que aportan valor diferencial frente a soluciones estándar.",
            "entrevista": "Puede mostrar un ejemplo concreto de una idea o solución propia que se salió de lo habitual y funcionó.",
            "fortaleza": "aporta un enfoque diferenciador allí donde otros perfiles se limitan a soluciones estándar.",
        },
        "medio": {
            "explicacion": "Capacidad funcional para proponer soluciones dentro de marcos ya conocidos, con un enfoque más pragmático que disruptivo. Aporta valor práctico y entregables ajustados a lo solicitado, aunque con menor diferenciación estética o conceptual.",
            "entrevista": "Puede explicar cómo adapta herramientas o formatos ya conocidos para dar forma práctica y atractiva a un encargo concreto.",
        },
        "bajo": {
            "explicacion": "Tiende a apoyarse en soluciones ya conocidas y puede tener dificultad para proponer alternativas cuando el enfoque habitual no funciona. Esto no es un problema en tareas de ejecución, pero puede limitar su aportación en roles que exigen innovar de forma frecuente.",
            "entrevista": "Puede señalar que se apoya en referencias e inspiración externa como método consciente de trabajo, más que en la improvisación.",
            "porque_afecta": "puede limitar su aportación en roles donde se espera innovar o diferenciarse de la competencia de forma frecuente.",
            "acciones": [
                "Dedicar 15 minutos semanales a revisar referencias e inspiración fuera del propio sector para ampliar el repertorio de ideas.",
                "Practicar la técnica de 'lista de 10 ideas' ante cualquier problema, aunque las primeras sean obvias, para forzar la divergencia.",
                "Pedir feedback específico sobre creatividad tras entregar un trabajo, para calibrar qué se considera una idea diferenciadora en el sector.",
            ],
        },
    },
    "influencia social": {
        "que_mide": "Capacidad para persuadir, orientar o movilizar a otras personas hacia un objetivo o punto de vista concreto.",
        "alto": {
            "explicacion": "Persuade con naturalidad basándose en relaciones de confianza más que en la imposición, adaptando el mensaje a las preocupaciones reales del interlocutor. Es un activo directo para roles de venta consultiva, negociación o fidelización de clientes.",
            "entrevista": "Puede argumentar este resultado con un ejemplo real de cómo convenció a alguien combinando escucha y argumentos adaptados.",
            "fortaleza": "es un activo directo para cualquier rol que implique venta consultiva, negociación o fidelización de clientes.",
        },
        "medio": {
            "explicacion": "Capacidad equilibrada para comunicar y orientar decisiones ajenas con claridad, aunque puede resultarle más costoso sostener una postura en escenarios de alta fricción o negociación dura. Funciona bien en contextos de asesoramiento y recomendación.",
            "entrevista": "Puede explicar cómo adapta su comunicación según la persona que tiene delante para lograr que su mensaje cale.",
        },
        "bajo": {
            "explicacion": "Le cuesta influir en las decisiones de terceros o sostener su punto de vista ante objeciones, lo que puede limitar su eficacia en tareas de venta, negociación o gestión de equipos. Trabajar la asertividad y la argumentación estructurada revertiría esta limitación.",
            "entrevista": "Puede mostrar que está trabajando activamente la asertividad, citando una situación reciente en la que lo intentó.",
            "porque_afecta": "puede limitar su eficacia en tareas que exigen persuadir, negociar o movilizar a otras personas hacia un objetivo.",
            "acciones": [
                "Practicar la técnica de argumentación en 3 pasos (hecho, beneficio, llamada a la acción) en conversaciones cotidianas de bajo riesgo.",
                "Grabarse (audio) explicando una propuesta y revisar el tono y la estructura del mensaje para detectar mejoras.",
                "Pedir feedback directo tras cada intento de persuasión relevante, preguntando qué argumento convenció más y cuál no funcionó.",
            ],
        },
    },
    "curiosidad y aprendizaje": {
        "que_mide": "Disposición para buscar nuevas experiencias, adquirir conocimiento de forma proactiva y adaptarse a cambios tecnológicos o de sector.",
        "alto": {
            "explicacion": "Muestra una disposición proactiva real hacia la autoformación y la actualización constante, lo que reduce el riesgo de quedar desfasado en sectores que cambian rápido. Es un perfil que se adapta con naturalidad a nuevas herramientas y tendencias.",
            "entrevista": "Puede citar una formación o herramienta nueva que haya aprendido por iniciativa propia en los últimos meses.",
            "fortaleza": "reduce de forma directa el riesgo de obsolescencia técnica, algo especialmente valioso en sectores que cambian rápido.",
        },
        "medio": {
            "explicacion": "Nivel funcional de curiosidad: aprende lo necesario cuando la tarea lo exige, aunque sin una rutina proactiva de actualización constante. Es suficiente para mantenerse al día si el entorno de trabajo ofrece formación estructurada.",
            "entrevista": "Puede explicar qué formación reciente ha completado y cómo la aplicó en la práctica.",
        },
        "bajo": {
            "explicacion": "Muestra una preferencia marcada por rutinas y métodos ya conocidos, con resistencia pasiva a incorporar herramientas o enfoques nuevos. En sectores que evolucionan rápido, esto supone un riesgo real de quedar desactualizado si no se corrige de forma activa.",
            "entrevista": "Puede mostrar madurez explicando qué plan concreto de actualización ha empezado a seguir para revertir esta tendencia.",
            "porque_afecta": "supone un riesgo de obsolescencia técnica en sectores que evolucionan rápido, sobre todo si el objetivo profesional exige manejar herramientas digitales nuevas.",
            "acciones": [
                "Fijar una rutina semanal de 2 horas para leer noticias o tendencias del sector de interés (newsletters, blogs especializados).",
                "Completar una micro-formación gratuita (1-3 horas) al mes en una plataforma como YouTube, Coursera o LinkedIn Learning.",
                "Unirse a una comunidad online (foro, grupo de LinkedIn) del sector objetivo para exponerse a tendencias de forma pasiva y constante.",
            ],
        },
    },
    "resiliencia y flexibilidad": {
        "que_mide": "Capacidad para recuperarse de la adversidad y adaptarse a entornos, instrucciones o modalidades de trabajo cambiantes.",
        "alto": {
            "explicacion": "Mantiene el rendimiento y el ánimo ante contratiempos e imprevistos, adaptando sus rutinas con rapidez cuando cambian las circunstancias. Es un perfil especialmente valioso en entornos con cambios frecuentes de prioridades o de modalidad de trabajo.",
            "entrevista": "Puede citar un cambio significativo (de sector, de modalidad de trabajo, de equipo) al que se adaptó con éxito.",
            "fortaleza": "aporta estabilidad operativa justo en los momentos en que un equipo más lo necesita: durante el cambio.",
        },
        "medio": {
            "explicacion": "Tolerancia adecuada a la frustración y a los cambios habituales, manteniendo el rendimiento en tareas repetitivas o ante ajustes moderados de la modalidad de trabajo. Se adapta cuando el cambio es explícito y razonablemente gradual.",
            "entrevista": "Puede describir cómo gestionó un cambio de tarea o de prioridades sin que afectara a su rendimiento.",
        },
        "bajo": {
            "explicacion": "Le cuesta mantener el rendimiento cuando cambian las condiciones de trabajo de forma brusca o poco planificada, con tendencia a la frustración ante la incertidumbre. Sin trabajo activo, esto puede ser un obstáculo en entornos con cambios frecuentes.",
            "entrevista": "Puede mostrar qué estrategia concreta está usando para gestionar mejor el cambio o la incertidumbre.",
            "porque_afecta": "puede ser un obstáculo real en entornos con cambios frecuentes de prioridades, herramientas o modalidad de trabajo.",
            "acciones": [
                "Practicar una técnica breve de gestión del estrés (respiración, pausa de 2 minutos) ante cualquier imprevisto antes de reaccionar.",
                "Anticipar por escrito 2-3 escenarios de cambio posibles en el puesto objetivo y cómo se actuaría en cada uno.",
                "Buscar apoyo (mentor, grupo de apoyo, Teamworkz) para procesar cambios significativos en vez de afrontarlos en solitario.",
            ],
        },
    },
    "autoconciencia": {
        "que_mide": "Reconocimiento objetivo de las propias emociones, fortalezas, limitaciones y su impacto real en el desempeño.",
        "alto": {
            "explicacion": "Reconoce con precisión sus propias fortalezas y limitaciones, y ajusta sus objetivos profesionales a la realidad del mercado con criterio propio. Esto reduce el riesgo de frustración por expectativas desalineadas y facilita el feedback.",
            "entrevista": "Puede mostrar autoconocimiento citando una limitación propia que ha identificado y qué está haciendo al respecto.",
            "fortaleza": "reduce el riesgo de frustración por expectativas desalineadas y facilita recibir y aplicar feedback.",
        },
        "medio": {
            "explicacion": "Cierto grado de autoevaluación, aunque puede costarle detectar sesgos propios en situaciones concretas o áreas poco trabajadas. Se beneficia de feedback externo periódico para calibrar mejor sus propias fortalezas y límites.",
            "entrevista": "Puede explicar una vez en la que un feedback externo le hizo ver algo que no había notado por sí mismo.",
        },
        "bajo": {
            "explicacion": "Presenta dificultad real para reconocer la distancia entre sus objetivos profesionales y su perfil actual, con tendencia a sobreestimar capacidades no consolidadas o a atribuir dificultades a factores externos. Esto genera puntos ciegos que conviene trabajar de forma activa antes de tomar decisiones de carrera importantes.",
            "entrevista": "Puede demostrar madurez señalando explícitamente, sin necesidad de que se lo pregunten, qué áreas está trabajando a partir de una evaluación como esta.",
            "porque_afecta": "genera puntos ciegos que pueden llevar a fijar objetivos profesionales poco realistas y a resistir el feedback necesario para corregirlos.",
            "acciones": [
                "Pedir feedback específico (no genérico) a 2-3 personas de confianza sobre una fortaleza y una limitación propias concretas.",
                "Llevar un registro semanal breve de aciertos y errores reales en el trabajo, sin juzgarlos, solo para tener datos objetivos.",
                "Comparar la autopercepción de este informe con la opinión de alguien cercano y anotar las diferencias más llamativas.",
            ],
        },
    },
    "empatia": {
        "que_mide": "Capacidad para reconocer, comprender y responder a los estados emocionales y necesidades de otras personas.",
        "alto": {
            "explicacion": "Presenta una sensibilidad interpersonal destacada: capta con facilidad señales no verbales y necesidades implícitas del interlocutor. Es el activo central de cualquier rol centrado en la atención, el asesoramiento o la experiencia de cliente.",
            "entrevista": "Puede describir una situación de atención al público en la que su empatía convirtió una queja o problema en una experiencia positiva.",
            "fortaleza": "es probablemente el activo más transferible del perfil: genera confianza inmediata en cualquier interacción con clientes o compañeros.",
        },
        "medio": {
            "explicacion": "Nivel funcional de sensibilidad interpersonal: percibe las necesidades explícitas del otro, aunque puede pasar por alto señales más sutiles o implícitas. Es suficiente para una atención al cliente correcta y profesional.",
            "entrevista": "Puede explicar cómo identifica lo que necesita un cliente o compañero cuando no lo dice de forma directa.",
        },
        "bajo": {
            "explicacion": "Le cuesta anticipar necesidades no expresadas explícitamente por otras personas, lo que puede generar fricciones en tareas de atención directa al público. Trabajar la escucha activa mejoraría notablemente su desempeño en roles de cara al cliente.",
            "entrevista": "Puede mostrar que está trabajando la escucha activa de forma consciente, con un ejemplo reciente de mejora.",
            "porque_afecta": "puede generar fricciones en tareas de atención directa al público si no se detectan a tiempo las necesidades no expresadas del interlocutor.",
            "acciones": [
                "Practicar la escucha activa (repetir o parafrasear lo que dice el otro antes de responder) en conversaciones cotidianas.",
                "Observar conscientemente el lenguaje no verbal en 2-3 interacciones al día y anotar qué reveló que las palabras no decían.",
                "Pedir feedback directo a compañeros o clientes sobre cómo se sintieron atendidos, más allá de si el problema se resolvió.",
            ],
        },
    },
    "pensamiento critico": {
        "que_mide": "Capacidad para evaluar la validez de argumentos, identificar sesgos y verificar hechos antes de actuar.",
        "alto": {
            "explicacion": "Cuestiona con solidez las suposiciones y verifica la consistencia de la información antes de actuar, aportando objetividad real en la evaluación de propuestas o recomendaciones. Es un activo directo para tareas de control de calidad o auditoría.",
            "entrevista": "Puede describir una situación en la que detectó una inconsistencia o un error que otros habían pasado por alto.",
            "fortaleza": "aporta objetividad y rigor allí donde otros perfiles aceptarían la información sin cuestionarla.",
        },
        "medio": {
            "explicacion": "Mantiene un grado de escepticismo saludable ante la información recibida, aunque en escenarios ambiguos puede necesitar pautas explícitas para emitir un juicio firme. Favorece el control de calidad en tareas ya estructuradas.",
            "entrevista": "Puede explicar un caso en el que verificó una información antes de darla por buena.",
        },
        "bajo": {
            "explicacion": "Tiende a aceptar información o instrucciones sin cuestionarlas lo suficiente, lo que puede traducirse en errores que se arrastran por falta de verificación previa. Desarrollar el hábito de contrastar antes de actuar reduciría este riesgo de forma directa.",
            "entrevista": "Puede mostrar que está incorporando el hábito de verificar antes de actuar, con un ejemplo concreto reciente.",
            "porque_afecta": "puede traducirse en errores que se arrastran por falta de verificación previa de datos o instrucciones.",
            "acciones": [
                "Antes de dar por buena una información importante, buscar una segunda fuente o confirmación explícita.",
                "Practicar el hábito de preguntarse '¿qué evidencia respalda esto?' ante cualquier afirmación relevante en el trabajo.",
                "Revisar con una checklist propia los puntos críticos de cualquier tarea antes de darla por terminada.",
            ],
        },
    },
    "liderazgo": {
        "que_mide": "Capacidad para guiar, organizar y motivar a otras personas o iniciativas hacia la consecución de un objetivo común.",
        "alto": {
            "explicacion": "Coordina con solvencia personas y tareas hacia un objetivo común, combinando organización con capacidad real para motivar al equipo. Es un perfil con potencial claro para roles de coordinación o gestión de equipos pequeños.",
            "entrevista": "Puede describir una situación en la que coordinó a otras personas para lograr un objetivo concreto.",
            "fortaleza": "muestra potencial real para asumir responsabilidad sobre equipos o proyectos, más allá de la ejecución individual.",
        },
        "medio": {
            "explicacion": "Competencia funcional para coordinar tareas y auto-gestionarse en proyectos de tamaño reducido, con un enfoque más facilitador que estratégico. Prefiere asegurar que el proceso funcione antes que asumir un liderazgo de alta visibilidad.",
            "entrevista": "Puede describir cómo organizó una tarea o evento pequeño asegurando que todo el mundo tuviera claro su papel.",
        },
        "bajo": {
            "explicacion": "Prefiere un rol de ejecución antes que de coordinación, y puede sentirse incómodo/a asumiendo responsabilidad sobre el trabajo de otras personas. Esto no es un problema para la mayoría de puestos operativos, pero conviene tenerlo en cuenta si el objetivo profesional incluye gestionar equipos.",
            "entrevista": "Puede ser honesto/a sobre esta preferencia y enfocar la conversación en su fortaleza real como perfil ejecutor y fiable.",
            "porque_afecta": "puede limitar el acceso a roles que exigen coordinar o responsabilizarse del trabajo de otras personas, si ese es el objetivo profesional.",
            "acciones": [
                "Ofrecerse voluntario/a para coordinar una tarea pequeña y de bajo riesgo dentro del equipo actual, aunque sea informal.",
                "Observar a un responsable o coordinador admirado y anotar 2-3 comportamientos concretos que se podrían imitar.",
                "Leer o ver contenido breve (no un curso completo) sobre liderazgo situacional para tener un marco conceptual básico.",
            ],
        },
    },
}

# Categoría psicométrica de cada competencia (mismo agrupamiento que usan los
# informes generados con IA: Cognitivas / Interpersonales-Sociales /
# Intrapersonales-Adaptativas), para que "Perfil de Competencias" se lea como
# un informe de consultoría real en vez de una lista plana.
SKILL_CATEGORY = {
    "toma de decisiones": "Competencias Cognitivas",
    "pensamiento analitico": "Competencias Cognitivas",
    "creatividad": "Competencias Cognitivas",
    "pensamiento critico": "Competencias Cognitivas",
    "influencia social": "Competencias Interpersonales y Sociales",
    "empatia": "Competencias Interpersonales y Sociales",
    "liderazgo": "Competencias Interpersonales y Sociales",
    "curiosidad y aprendizaje": "Competencias Intrapersonales y Adaptativas",
    "resiliencia y flexibilidad": "Competencias Intrapersonales y Adaptativas",
    "autoconciencia": "Competencias Intrapersonales y Adaptativas",
}

CATEGORY_ORDER = [
    "Competencias Cognitivas",
    "Competencias Interpersonales y Sociales",
    "Competencias Intrapersonales y Adaptativas",
    "Otras Competencias Evaluadas",
]


def _tier_key(score: int) -> str:
    if score >= 70:
        return "alto"
    if score >= 40:
        return "medio"
    return "bajo"


def _detect_languages(text: str) -> List[str]:
    if not text:
        return []
    found: Dict[str, str] = {}
    for alias, canon in LANGUAGE_NAMES.items():
        if canon in found:
            continue
        m = re.search(rf"\b{re.escape(alias)}\b", text, re.IGNORECASE)
        if not m:
            continue
        # El nivel suele ir DESPUÉS del idioma dentro del mismo fragmento
        # ("Inglés B2", "Francés básico") -- se acota al mismo trozo (hasta
        # la siguiente coma/salto de línea/punto) para no capturar el nivel
        # de un idioma distinto mencionado justo antes en la misma frase.
        tail = text[m.end(): m.end() + 40]
        stop = re.search(r"[,\n;.]", tail)
        forward_window = tail[: stop.start()] if stop else tail
        level_m = LEVEL_PATTERN.search(forward_window)
        found[canon] = f"{canon} ({level_m.group(0).capitalize()})" if level_m else canon
    return list(found.values())[:6]


def _detect_tools(text: str) -> List[str]:
    if not text:
        return []
    found = []
    for tool in TOOL_KEYWORDS:
        if re.search(rf"\b{re.escape(tool)}\b", text, re.IGNORECASE):
            found.append(tool)
    return found[:12]


def _lines_from_section(sections: Dict[str, Any], key: str, limit: int = 6) -> List[str]:
    block = sections.get(key)
    if not block:
        return []
    raw_lines = str(block).splitlines()
    # Descarta la primera línea si es solo el encabezado de la sección (p.ej. "EXPERIENCIA")
    if raw_lines and len(raw_lines[0].split()) <= 3:
        raw_lines = raw_lines[1:]

    lines: List[str] = []
    for ln in raw_lines:
        clean = ln.strip(" \t•-·")
        if len(clean) <= 3:
            continue
        # El bloque se extrae hasta el siguiente salto doble; si el PDF no
        # separa secciones con línea en blanco, cortar en cuanto aparezca
        # el encabezado de OTRA sección para no arrastrar su contenido.
        if _ANY_SECTION_HEADER_RE.match(clean):
            break
        lines.append(clean)
    return lines[:limit]


def _tier_label(score: int) -> str:
    if score >= 80:
        return "Alto"
    if score >= 55:
        return "Medio"
    return "Bajo"


def _build_analisis_cv(review: Dict[str, Any], text: str, sections: Dict[str, Any]) -> Dict[str, Any]:
    scores = review.get("scores", {}) or {}
    fmt = scores.get("format", {}) or {}
    cla = scores.get("clarity", {}) or {}
    coh = scores.get("coherence", {}) or {}
    key = scores.get("key_information", {}) or {}
    spe = scores.get("spelling", {}) or {}

    valoraciones = {
        "formato": int(fmt.get("stars", 3) or 3),
        "claridad": int(cla.get("stars", 3) or 3),
        "coherencia": int(coh.get("stars", 3) or 3),
        "info_clave": int(key.get("stars", 3) or 3),
        "ortografia": int(spe.get("stars", 3) or 3),
    }

    dim_labels = {
        "formato": ("estructura y formato", fmt),
        "claridad": ("claridad de redacción", cla),
        "coherencia": ("coherencia cronológica", coh),
        "info_clave": ("información clave aportada", key),
        "ortografia": ("ortografía y estilo", spe),
    }

    puntos_fuertes: List[str] = []
    aspectos_mejorar: List[str] = []
    for dim, (label, data) in dim_labels.items():
        stars = valoraciones[dim]
        expl = str(data.get("explanation") or "").strip()
        if stars >= 4:
            puntos_fuertes.append(f"Buen nivel de {label}. {expl}".strip())
        elif stars <= 2:
            aspectos_mejorar.append(f"Necesita reforzar {label}. {expl}".strip())

    typos = _detect_typos(text)
    if typos:
        aspectos_mejorar.append(
            "Erratas tipográficas detectadas en nombres de herramientas o software: " + "; ".join(typos) + "."
        )

    if not puntos_fuertes:
        puntos_fuertes.append(
            "El CV cubre la información básica esperada para un primer diagnóstico automático."
        )
    if not aspectos_mejorar:
        aspectos_mejorar.append(
            "No se han detectado carencias críticas en el análisis automático; aun así, una revisión manual siempre suma."
        )

    experiencia = _lines_from_section(sections, "experience") or [
        "No se detectó una sección de experiencia claramente encabezada en el documento."
    ]
    formacion = _lines_from_section(sections, "education") or [
        "No se detectó una sección de formación claramente encabezada en el documento."
    ]
    idiomas = _detect_languages(text) or ["No se especifican idiomas en el documento."]
    software = _detect_tools(text) or ["No se detectaron herramientas o software específicos mencionados textualmente."]

    ats_score = int(round((fmt.get("score", 60) or 60) * 0.4 + (key.get("score", 60) or 60) * 0.6))
    ats_score = max(0, min(100, ats_score))
    email_found = bool(re.search(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", text or ""))
    ats_explicacion = (
        "Compatibilidad estimada con lectores automáticos (ATS) a partir de la cobertura de secciones "
        f"({'contacto detectado en el documento' if email_found else 'sin contacto claro detectado en el documento'}) "
        "y del formato general. Es una estimación heurística basada en reglas, no una lectura semántica del contenido."
    )

    return {
        "resumen": (
            "Análisis automático (sin IA) generado a partir de la estructura del documento: "
            f"formato {valoraciones['formato']}/5, claridad {valoraciones['claridad']}/5, "
            f"coherencia {valoraciones['coherencia']}/5, información clave {valoraciones['info_clave']}/5 "
            f"y ortografía {valoraciones['ortografia']}/5."
        ),
        "experiencia": experiencia,
        "formacion": formacion,
        "idiomas": idiomas,
        "software": software,
        "valoraciones": valoraciones,
        "puntos_fuertes": puntos_fuertes,
        "aspectos_mejorar": aspectos_mejorar,
        "ats_compatibilidad": ats_score,
        "ats_explicacion": ats_explicacion,
    }


def _generic_competency_content(nombre: str, tier: str) -> Dict[str, Any]:
    """Respaldo para una habilidad que no está en COMPETENCY_CONTENT (p.ej. un
    minijuego nuevo que aún no se ha documentado aquí)."""
    low = nombre.lower()
    base = {
        "alto": f"Obtiene un resultado destacado en {low}, un indicador fiable de que esta competencia está consolidada y puede aportar valor real en el puesto de trabajo.",
        "medio": f"Obtiene un resultado funcional en {low}: suficiente para el desempeño habitual, con margen de consolidación si el puesto la exige de forma intensiva.",
        "bajo": f"Obtiene un resultado bajo en {low}, lo que indica una oportunidad de mejora concreta a trabajar de forma activa antes de que se convierta en un obstáculo real.",
    }[tier]
    return {
        "explicacion": base,
        "entrevista": f"Puede preparar un ejemplo concreto de su experiencia que ilustre cómo aplica {low} en la práctica.",
        "fortaleza": f"es un punto fuerte real que conviene mencionar activamente en procesos de selección.",
        "porque_afecta": f"puede limitar el desempeño en tareas donde {low} se pone a prueba de forma frecuente.",
        "acciones": [
            f"Buscar un curso corto o recurso gratuito centrado específicamente en {low}.",
            "Practicar la competencia en situaciones reales o simuladas al menos una vez por semana.",
            "Pedir feedback explícito sobre esta competencia a un mentor, formador o responsable de Teamworkz.",
        ],
    }


def _build_competencias(soft_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    competencias = []
    for s in soft_skills:
        nombre = str(s.get("skill") or "Competencia").strip()
        key = _normalize_key(nombre)
        try:
            score = int(round(float(s.get("score", 0) or 0)))
        except (TypeError, ValueError):
            score = 0
        score = max(0, min(100, score))
        nivel = str(s.get("level") or _tier_label(score)).capitalize()
        tier = _tier_key(score)
        content = COMPETENCY_CONTENT.get(key)
        tier_content = (content or {}).get(tier) or _generic_competency_content(nombre, tier)
        que_mide = (content or {}).get("que_mide") or f"Capacidad evaluada mediante escenarios simulados dentro de EvalúaTE relacionados con {nombre.lower()}."
        categoria = SKILL_CATEGORY.get(key, "Otras Competencias Evaluadas")
        competencias.append({
            "nombre": nombre,
            "puntuacion": score,
            "nivel": nivel,
            "explicacion": tier_content["explicacion"],
            "_categoria": categoria,
            "_que_mide": que_mide,
            "_entrevista": tier_content.get("entrevista", ""),
            "_fortaleza": tier_content.get("fortaleza", ""),
            "_porque_afecta": tier_content.get("porque_afecta", ""),
            "_acciones": tier_content.get("acciones") or [],
        })

    # Agrupar por categoría psicométrica (Cognitivas / Interpersonales /
    # Intrapersonales), respetando CATEGORY_ORDER, igual que un informe de
    # consultoría real -- una lista plana de 10 competencias sin agrupar es
    # mucho más difícil de leer y se siente menos "profesional".
    by_category: Dict[str, list] = {}
    for c in competencias:
        by_category.setdefault(c["_categoria"], []).append(c)

    def _strip_internal(c: dict) -> dict:
        return {"nombre": c["nombre"], "puntuacion": c["puntuacion"], "nivel": c["nivel"], "explicacion": c["explicacion"]}

    perfil_competencias = [
        {"categoria": cat, "competencias": [_strip_internal(c) for c in by_category[cat]]}
        for cat in CATEGORY_ORDER if cat in by_category
    ]

    ranked = sorted(competencias, key=lambda c: c["puntuacion"], reverse=True)
    fuertes = [c for c in ranked if c["puntuacion"] >= 70][:2] or ranked[:1]
    debiles = [c for c in ranked if c["puntuacion"] < 60][-2:] or ranked[-1:]

    fortalezas_principales = [
        {
            "nombre": f"{c['nombre'].upper()} SOBRESALIENTE" if c["puntuacion"] >= 85 else c["nombre"].upper(),
            "explicacion_practica": (
                f"La evaluación revela un resultado destacado ({c['puntuacion']}/100) en {c['nombre'].lower()}, "
                f"lo cual valida que {c['_fortaleza'] or 'es un punto fuerte real del perfil'}"
            ),
        }
        for c in fuertes
    ]

    areas_mejora = [
        {
            "nombre": c["nombre"].upper(),
            "porque_afecta": (
                f"La puntuación de {c['puntuacion']}/100 en {c['nombre'].lower()} "
                f"{(c['_porque_afecta'] or 'indica un margen de mejora real que conviene trabajar de forma activa').rstrip('.')}."
            ),
            "como_mejorar": "PLAN DE CAPACITACIÓN INMEDIATA:",
            "acciones_concretas": c["_acciones"] or [
                f"Buscar un curso corto o recurso gratuito centrado específicamente en {c['nombre'].lower()}.",
                "Practicar la competencia en situaciones reales o simuladas al menos una vez por semana.",
                "Pedir feedback explícito sobre esta competencia a un mentor, formador o responsable de Teamworkz.",
            ],
        }
        for c in debiles
    ]

    resultados_juegos = [
        {
            "juego": c["nombre"],
            "que_mide": f"DIMENSIÓN: {c['_que_mide']}",
            "resultado": f"{c['puntuacion']}/100 ({c['nivel']})",
            "interpretacion": f"Mapeo Psicométrico: {c['explicacion']}",
            "aplicacion_entrevista": f"Transferencia a Entrevista: {c['_entrevista'] or 'puede argumentar este resultado citando ejemplos concretos de su experiencia.'}",
        }
        for c in competencias
    ]

    return {
        "perfil_competencias": perfil_competencias,
        "fortalezas_principales": fortalezas_principales,
        "areas_mejora": areas_mejora,
        "resultados_juegos": resultados_juegos,
    }


def _build_accion(job_prefs: Dict[str, Any], puntuacion_global: int, top_fortalezas: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    top_fortalezas = top_fortalezas or []
    areas = [a for a in (job_prefs.get("areas") or []) if isinstance(a, str) and a.strip()] or ["su área profesional de interés"]
    needs = [n for n in (job_prefs.get("needs") or []) if isinstance(n, str) and n.strip()]
    work_mode = str(job_prefs.get("workMode") or job_prefs.get("work_mode") or "").lower()

    # Detecta si el candidato ha pedido "remoto" para un oficio que, por su
    # propia naturaleza, no se puede ejercer en remoto (ver ON_SITE_ONLY_KEYWORDS).
    # El informe debe SEÑALAR esa incoherencia en vez de repetirla sin más --
    # es exactamente el tipo de error que hace que un informe automático
    # parezca que "no se entera" de lo que ha dicho el candidato.
    wants_remote = work_mode.startswith("remot")
    conflict_areas = [a for a in areas if wants_remote and _requires_on_site_presence(a)]
    coherencia_notas: List[str] = []

    entornos_ideales: List[str] = []
    if conflict_areas:
        area_txt = " y ".join(conflict_areas)
        aviso = (
            f"Aviso: {area_txt} es un oficio que requiere presencia física (trato directo con clientes o "
            "pacientes, manipulación de materiales o herramientas, uso de instalaciones concretas). El "
            "teletrabajo al 100% no es viable en la inmensa mayoría de sus puestos, aunque se haya indicado "
            "como preferencia -- se ajusta la modalidad a presencial (o híbrida solo para tareas administrativas) "
            "para que el resto del informe sea realista."
        )
        entornos_ideales.append(aviso)
        entornos_ideales.append(f"Puestos presenciales dentro de {areas[0]}, en un centro de trabajo físico.")
        coherencia_notas.append(aviso)
    else:
        entornos_ideales.append(f"Puestos dentro de {areas[0]}, alineados con el interés declarado por el candidato.")
        entornos_ideales.append(
            WORK_MODE_TEXT.get(work_mode, "un entorno de trabajo flexible que se pueda adaptar según necesidad").capitalize()
        )
    if needs:
        entornos_ideales.append("Entornos que contemplen: " + "; ".join(needs[:3]) + ".")
    entornos_ideales.append(
        "Equipos con procesos claros, feedback frecuente y acompañamiento durante la incorporación."
    )

    roles_recomendados = []
    for area in areas[:2]:
        on_site_only = wants_remote and _requires_on_site_presence(area)
        demanda = "ALTA" if puntuacion_global >= 70 else "MEDIA"
        modalidad = "Presencial" if on_site_only else (work_mode.capitalize() if work_mode else "A definir según la oferta")
        por_que_encaja = (
            f"Justificación de encaje temporal: el candidato ha mostrado interés explícito en {area} y una "
            f"puntuación global de empleabilidad de {puntuacion_global}/100 en la evaluación de EvalúaTE, "
            "un punto de partida razonable para posiciones de entrada en este ámbito."
        )
        if on_site_only:
            por_que_encaja += (
                f" Se indicó preferencia por trabajo remoto, pero {area.lower()} requiere presencia física en la "
                "mayoría de sus puestos; la modalidad se ajusta a presencial para reflejar la realidad del sector."
            )
        roles_recomendados.append({
            "titulo": f"Perfil junior/operativo en {area}",
            "nivel": "Junior" if puntuacion_global < 70 else "Mid-level",
            "modalidad": modalidad,
            "por_que_encaja": por_que_encaja,
            "demanda_laboral": demanda,
        })

    pivot: Dict[str, Any] | None = None
    if conflict_areas:
        pivot_area = conflict_areas[0]
        pivot = _pivot_family(pivot_area)
        for titulo, motivo in pivot["roles"]:
            roles_recomendados.append({
                "titulo": titulo,
                "nivel": "Mid-level" if puntuacion_global >= 60 else "Junior",
                "modalidad": "Remoto",
                "por_que_encaja": (
                    "Justificación de encaje temporal: dado que el trabajo 100% remoto en "
                    f"{pivot_area.lower()} no es viable de forma presencial, este pivote permite mantener el objetivo "
                    f"de trabajar en remoto {motivo}"
                ),
                "demanda_laboral": "MEDIA-ALTA" if puntuacion_global >= 60 else "MEDIA",
            })

    dias_30 = [
        "Actualizar y pulir el CV incorporando los puntos fuertes detectados en este informe.",
        f"Enviar activamente candidaturas a ofertas relacionadas con {areas[0]}, al menos 3-5 por semana.",
        "Preparar un guion breve de 2-3 minutos para presentarse en entrevistas, apoyado en los resultados de este informe.",
    ]
    dias_60 = [
        "Completar una formación corta o certificación gratuita relacionada con las áreas de mejora detectadas.",
        "Actualizar el perfil de LinkedIn (o portfolio, según el sector) con la experiencia y competencias reales.",
        "Contactar activamente con la red de Teamworkz y otras entidades de intermediación laboral especializadas.",
    ]
    dias_90 = [
        "Realizar al menos una simulación de entrevista con feedback de un tercero.",
        "Revisar y ajustar la estrategia de búsqueda según los resultados obtenidos hasta el momento.",
        "Consolidar los aprendizajes del proceso en un documento de seguimiento personal.",
    ]

    estrategia_busqueda = [
        f"Priorizar portales y empresas especializadas en {areas[0]} y en empleo inclusivo/con apoyo.",
        "Activar la red de contactos personal y profesional explicando de forma clara el objetivo laboral.",
        "Hacer seguimiento de cada candidatura enviada (fecha, empresa, estado) para no perder oportunidades.",
        "Adaptar el CV y la carta de presentación a cada oferta relevante, destacando las competencias mejor puntuadas.",
        "Participar en ferias de empleo, jornadas de intermediación laboral o eventos del sector de interés.",
    ]

    herramientas_recomendadas = [
        {"nombre": "LinkedIn", "para_que_sirve": "Visibilidad profesional, red de contactos y acceso a ofertas del sector."},
        {"nombre": "Portales de empleo especializados", "para_que_sirve": "Búsqueda activa y postulación a ofertas relacionadas con el área de interés."},
        {"nombre": "Canva", "para_que_sirve": "Diseñar un CV visualmente claro y profesional sin necesidad de conocimientos de diseño."},
    ]
    if pivot:
        herramientas_recomendadas = [
            {"nombre": nombre, "para_que_sirve": desc} for nombre, desc in pivot["tools"]
        ] + herramientas_recomendadas

    recomendaciones_personalizadas = [
        f"Enfocar la búsqueda inicial en {areas[0]}, donde el candidato ha mostrado mayor interés.",
        "Apoyarse en las fortalezas detectadas en la evaluación al preparar entrevistas.",
        "Trabajar de forma activa, aunque progresiva, las áreas de mejora señaladas en este informe.",
        "Mantener actualizado el CV con logros concretos y medibles a medida que se generen.",
        "Pedir apoyo a Teamworkz u otras entidades de intermediación si el proceso se estanca más de 4-6 semanas.",
    ]
    if conflict_areas:
        recomendaciones_personalizadas.insert(
            0,
            f"Revisar la preferencia de trabajo remoto para {conflict_areas[0]}: en la práctica casi todos los "
            "puestos de este sector exigen presencia física, así que conviene abrirse a presencial o híbrido "
            "para no descartar oportunidades reales por esta condición.",
        )

    recursos_adicionales = [
        {
            "nombre": f"Formación online gratuita relacionada con {areas[0]}",
            "tipo": "FORMACIÓN HABILITANTE",
            "descripcion": f"Refuerza la empleabilidad en {areas[0]}, el área de mayor interés declarada por el candidato.",
        },
        {
            "nombre": "Curso corto de preparación de entrevistas de trabajo",
            "tipo": "DESARROLLO DE HABILIDAD ESPECÍFICA",
            "descripcion": "Ayuda a transformar los resultados de este informe en argumentos sólidos durante un proceso de selección.",
        },
    ]

    if puntuacion_global >= 70:
        nivel_txt = "un nivel de empleabilidad sólido"
    elif puntuacion_global >= 45:
        nivel_txt = "un nivel de empleabilidad en desarrollo"
    else:
        nivel_txt = "un punto de partida que requiere trabajo constante"

    fortaleza_txt = ""
    if top_fortalezas:
        top = top_fortalezas[0]
        fortaleza_txt = f" Apalancando tu resultado en {top['nombre'].lower()} ({top['puntuacion']}/100), "
    else:
        fortaleza_txt = " Apoyándote en las fortalezas detectadas en la evaluación, "

    if pivot:
        mensaje_final = (
            f"El objetivo inicial de ejercer {conflict_areas[0].lower()} en modalidad 100% remota presenta una "
            "incompatibilidad real con la forma en que se ejerce ese oficio hoy. Sin embargo, tu perfil tiene una "
            f"vía de pivote concreta:{fortaleza_txt}puedes posicionarte en roles de asesoramiento, atención al "
            f"cliente o gestión online dentro del mismo sector, en vez de en la ejecución física del oficio. "
            f"Con una puntuación global de {puntuacion_global}/100, el perfil evaluado muestra {nivel_txt}. "
            "Este informe se ha generado de forma 100% automática, sin intervención de un modelo de IA generativa, "
            "a partir de tus respuestas, tus resultados en los minijuegos y un análisis heurístico de tu CV."
        )
    else:
        mensaje_final = (
            f"Con una puntuación global de {puntuacion_global}/100, el perfil evaluado muestra {nivel_txt}."
            f"{fortaleza_txt}usa las fortalezas señaladas como argumento en tus candidaturas y trabaja las áreas "
            "de mejora de forma constante: la empleabilidad es un proceso, no un veredicto único. Este informe se "
            "ha generado de forma 100% automática, sin intervención de un modelo de IA generativa, a partir de tus "
            "respuestas, tus resultados en los minijuegos y un análisis heurístico de tu CV."
        )

    return {
        "entornos_ideales": entornos_ideales[:5],
        "roles_recomendados": roles_recomendados,
        "plan_accion": {"dias_30": dias_30, "dias_60": dias_60, "dias_90": dias_90},
        "estrategia_busqueda": estrategia_busqueda,
        "herramientas_recomendadas": herramientas_recomendadas,
        "recomendaciones_personalizadas": recomendaciones_personalizadas,
        "recursos_adicionales": recursos_adicionales,
        "mensaje_final": mensaje_final,
        "coherencia_notas": coherencia_notas,
    }


def generate_deterministic_report(
    pdf_bytes: bytes,
    games_data: Dict[str, Any],
    prefs_data: Dict[str, Any],
    employability_score: int,
    candidate_name: str = "Candidato",
) -> Dict[str, Any]:
    """Genera el informe completo SIN IA: heurísticas deterministas sobre el
    CV (regex + puntuación por reglas) + datos estructurados de los
    minijuegos y las preferencias. Nunca lanza excepción, nunca depende de
    una API externa, y siempre devuelve una estructura completa."""
    try:
        cv_result = analyze_cv_structure_from_bytes(pdf_bytes or b"")
    except Exception as e:
        logger.warning(f"Fallo heurístico analizando el CV, se usa revisión neutra: {e}")
        cv_result = {"review": {"scores": {}}, "text": "", "sections": {}}

    review = cv_result.get("review") or {}
    text = cv_result.get("text") or ""
    sections = cv_result.get("sections") or {}

    contacto = extract_contact_info(text) if text else {}

    job_prefs = prefs_data if isinstance(prefs_data, dict) else {}

    soft_skills_raw = games_data.get("softSkills") if isinstance(games_data, dict) else None
    soft_skills = [s for s in (soft_skills_raw or []) if isinstance(s, dict) and s.get("skill")]
    if not soft_skills:
        soft_skills = [{"skill": "Adaptabilidad", "score": 60, "level": "Medio"}]

    datos_personales = {
        "Nombre": str(candidate_name or contacto.get("nombre") or "Candidato/a"),
        "Ubicacion": str(job_prefs.get("location") or "No especificada"),
        "Email": str(job_prefs.get("email") or contacto.get("email") or "No especificado"),
        "Telefono": str(job_prefs.get("whatsapp") or job_prefs.get("phone") or contacto.get("telefono") or "No especificado"),
        "LinkedIn": str(contacto.get("linkedin") or "No especificado"),
    }

    analisis_cv = _build_analisis_cv(review, text, sections)
    competencias_info = _build_competencias(soft_skills)

    try:
        puntuacion_global = int(employability_score)
    except (TypeError, ValueError):
        puntuacion_global = 60
    puntuacion_global = max(0, min(100, puntuacion_global))

    interpretacion_global = (
        f"Puntuación global de {puntuacion_global}/100, calculada a partir del promedio de las competencias "
        "evaluadas en los minijuegos (ver detalle en 'Resultados de las Evaluaciones'). Es un indicador "
        "orientativo, no un veredicto definitivo sobre la empleabilidad del candidato."
    )
    resumen_ejecutivo = (
        f"Informe generado automáticamente (sin IA generativa) para {datos_personales['Nombre']}. "
        "Combina el análisis heurístico del CV aportado con los resultados de los minijuegos de EvalúaTE "
        "y las preferencias laborales indicadas, para ofrecer una fotografía objetiva y reproducible del "
        "perfil evaluado, sin depender de servicios externos de inteligencia artificial."
    )
    detected_tools = [t for t in analisis_cv.get("software", []) if "No se detectaron" not in t]
    ranked_skills = sorted(
        (
            {"nombre": str(s.get("skill") or "").strip(), "puntuacion": int(round(float(s.get("score", 0) or 0)))}
            for s in soft_skills if s.get("skill")
        ),
        key=lambda c: c["puntuacion"], reverse=True,
    )
    top_skill = ranked_skills[0] if ranked_skills else None
    extra_bits = []
    if detected_tools:
        extra_bits.append(f"en el CV se identificaron herramientas como {', '.join(detected_tools[:3])}")
    if top_skill:
        extra_bits.append(
            f"en los minijuegos destaca especialmente {top_skill['nombre'].lower()} ({top_skill['puntuacion']}/100)"
        )
    if extra_bits:
        joined = " y ".join(extra_bits)
        resumen_ejecutivo += " " + joined[:1].upper() + joined[1:] + "."

    accion = _build_accion(job_prefs, puntuacion_global, top_fortalezas=ranked_skills[:2])
    coherencia_notas = accion.pop("coherencia_notas", [])
    if coherencia_notas:
        resumen_ejecutivo += " " + " ".join(coherencia_notas)

    report = {
        "datos_personales": datos_personales,
        "resumen_ejecutivo": resumen_ejecutivo,
        "puntuacion_global": puntuacion_global,
        "interpretacion_global": interpretacion_global,
        "analisis_cv": analisis_cv,
        "perfil_competencias": competencias_info["perfil_competencias"],
        "fortalezas_principales": competencias_info["fortalezas_principales"],
        "areas_mejora": competencias_info["areas_mejora"],
        "resultados_juegos": competencias_info["resultados_juegos"],
        **accion,
        "generado_sin_ia": True,
    }
    return report
