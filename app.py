"""
YoCreo Suite - Aplicación Principal
Transformación Consciente
"""

import streamlit as st

# Configuración de página (DEBE ser lo primero)
st.set_page_config(
    page_title="YoCreo Suite",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Importar módulos core
from core.styles import apply_styles, get_css
from core.config import PRACTICAS, APP_INFO, COLORS
from core.ai_client import init_ai

# Aplicar estilos
apply_styles(st)

# Inicializar IA (guardar estado)
ai_ready = init_ai()

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo centrado y reducido
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/logo.png", width=100)
    st.markdown("---")
    st.markdown("### Prácticas de Coaching")

    # Menú de navegación
    practica_seleccionada = st.radio(
        "Selecciona una práctica:",
        options=list(PRACTICAS.keys()),
        format_func=lambda x: f"{PRACTICAS[x]['icono']} {PRACTICAS[x]['titulo']}",
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("Desarrollado por Juan Pablo Caamaño Valdés")
    st.caption(f"v{APP_INFO['version']}")

# ==================== CONTENIDO PRINCIPAL ====================

# Verificar que IA esté lista antes de cargar prácticas
if not ai_ready:
    st.stop()

# Importar y mostrar la práctica seleccionada
if practica_seleccionada == "correos_diplomaticos":
    from practicas.correos_diplomaticos import render
    render()

elif practica_seleccionada == "delegacion_situacional":
    from practicas.delegacion_situacional import render
    render()

elif practica_seleccionada == "negociador_harvard":
    from practicas.negociador_harvard import render
    render()

elif practica_seleccionada == "pedidos_impecables":
    from practicas.pedidos_impecables import render
    render()

elif practica_seleccionada == "planificador_reuniones":
    from practicas.planificador_reuniones import render
    render()

elif practica_seleccionada == "priorizador_tareas":
    from practicas.priorizador_tareas import render
    render()

elif practica_seleccionada == "seguimiento_compromisos":
    from practicas.seguimiento_compromisos import render
    render()

elif practica_seleccionada == "escucha_activa":
    from practicas.escucha_activa import render
    render()

elif practica_seleccionada == "evaluacion_desempeno":
    from practicas.evaluacion_desempeno import render
    render()

elif practica_seleccionada == "feedback_constructivo":
    from practicas.feedback_constructivo import render
    render()

elif practica_seleccionada == "presentacion_inspiradora":
    from practicas.presentacion_inspiradora import render
    render()

else:
    st.warning("Práctica no disponible")
