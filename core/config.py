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

# Practicas disponibles (SIN ICONOS - Minimalismo Radical)
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
    }
}
