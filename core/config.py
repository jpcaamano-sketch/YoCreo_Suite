"""
Configuracion global de YoCreo Suite
Protocolo Estandar v2.0
"""

# Colores corporativos estrictos
COLORS = {
    "naranja": "#FF6B4E",      # Boton accion
    "purpura": "#4E32AD",      # Boton descarga
    "blanco": "#FFFFFF",       # Fondo general
    "negro": "#000000",        # Bordes
    "gris_texto": "#333333"
}

# Configuracion de IA
AI_CONFIG = {
    "model": "gemini-2.5-flash",
    "max_tokens": 8192
}

# Informacion de la app
APP_INFO = {
    "nombre": "YoCreo - Suite Liderazgo Consciente",
    "subtitulo": "Transformación Consciente",
    "version": "2.0.0"
}

# Categorias de practicas
CATEGORIAS = {
    "inicio": {
        "nombre": "Suite Liderazgo Consciente",
        "practicas": ["introduccion"]
    },
    "autogestion": {
        "nombre": "Autogestión y Foco",
        "practicas": ["priorizador_tareas", "presentacion_inspiradora"]
    },
    "coordinacion": {
        "nombre": "Coordinación Impecable",
        "practicas": ["pedidos_impecables", "delegacion_situacional", "correos_diplomaticos", "seguimiento_compromisos"]
    },
    "desarrollo": {
        "nombre": "Desarrollo de Otros",
        "practicas": ["escucha_activa", "preguntas_desafiantes", "feedback_constructivo", "evaluacion_desempeno"]
    },
    "estrategia": {
        "nombre": "Estrategia y Relaciones",
        "practicas": ["definicion_objetivos", "planificador_reuniones", "negociador_harvard", "disculpas_efectivas"]
    }
}

# Iconos SVG naranja para cada práctica
ICONOS_SVG = {
    "introduccion": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "priorizador_tareas": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    "presentacion_inspiradora": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    "pedidos_impecables": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "delegacion_situacional": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "correos_diplomaticos": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
    "seguimiento_compromisos": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "escucha_activa": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>',
    "preguntas_desafiantes": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "feedback_constructivo": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "evaluacion_desempeno": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "definicion_objetivos": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "planificador_reuniones": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "negociador_harvard": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
    "disculpas_efectivas": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>',
    "admin_panel": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#E67E22" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
}

# Practicas disponibles
PRACTICAS = {
    "introduccion": {
        "titulo": "Bienvenido a la Suite",
        "descripcion": "Descubre el camino del Líder Consciente."
    },
    "priorizador_tareas": {
        "titulo": "Priorizador de Tareas",
        "descripcion": "Prioriza tus tareas usando la Matriz de Eisenhower."
    },
    "presentacion_inspiradora": {
        "titulo": "Presentación Inspiradora",
        "descripcion": "Convierte datos fríos en historias inspiradoras."
    },
    "pedidos_impecables": {
        "titulo": "Pedidos Impecables",
        "descripcion": "Evita pérdidas de tiempo, recursos y reprocesos."
    },
    "delegacion_situacional": {
        "titulo": "Delegación Situacional",
        "descripcion": "Delega tareas según la competencia y motivación de cada persona."
    },
    "correos_diplomaticos": {
        "titulo": "Mensajes Diplomáticos",
        "descripcion": "Responde a tiempo y de manera asertiva."
    },
    "seguimiento_compromisos": {
        "titulo": "Seguimiento de Compromisos",
        "descripcion": "Haz valer los compromisos acordados."
    },
    "escucha_activa": {
        "titulo": "Escucha Activa",
        "descripcion": "Simulador de Escucha Activa."
    },
    "preguntas_desafiantes": {
        "titulo": "Preguntas Desafiantes",
        "descripcion": "Formula preguntas poderosas que generen reflexión."
    },
    "feedback_constructivo": {
        "titulo": "Feedback Constructivo",
        "descripcion": "Convierte tus quejas en feedback profesional."
    },
    "evaluacion_desempeno": {
        "titulo": "Evaluación de Desempeño",
        "descripcion": "Evalúa el desempeño de tu equipo de manera objetiva."
    },
    "definicion_objetivos": {
        "titulo": "Definición de Objetivos e Indicadores",
        "descripcion": "Define objetivos claros y alcanzables."
    },
    "planificador_reuniones": {
        "titulo": "Planificador de Reuniones",
        "descripcion": "Crea agendas que hagan tus reuniones mas productivas."
    },
    "negociador_harvard": {
        "titulo": "Negociador estilo Harvard",
        "descripcion": "Estrategia de negociación basada en intereses."
    },
    "disculpas_efectivas": {
        "titulo": "Disculpas Efectivas",
        "descripcion": "Repara vínculos con disculpas genuinas."
    },
    "admin_panel": {
        "titulo": "Panel de Administración",
        "descripcion": "Gestiona los miembros de tu organización."
    }
}
