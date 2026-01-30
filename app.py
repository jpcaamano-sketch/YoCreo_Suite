"""
YoCreo Suite - Aplicacion Principal
Protocolo Estandar v3.0
"""

import streamlit as st
import base64
from pathlib import Path

# Configuracion de pagina
st.set_page_config(
    page_title="YoCreo Suite",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Importar modulos core
from core.styles import apply_styles
from core.config import PRACTICAS, CATEGORIAS, APP_INFO
from core.ai_client import init_ai
from core.auth import (
    mostrar_login,
    verificar_autenticacion,
    obtener_usuario_actual,
    cerrar_sesion
)

# Aplicar estilos
apply_styles(st)


def get_logo_base64():
    """Obtiene el logo en base64 para mostrar en sidebar"""
    logo_path = Path(__file__).parent / "assets" / "logo_blanco.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def get_initial_page():
    """Obtiene la pagina inicial desde query params o default"""
    params = st.query_params
    if "p" in params:
        page = params["p"]
        if page in PRACTICAS:
            return page
    return "introduccion"


# ==================== VERIFICAR AUTENTICACION ====================

if not verificar_autenticacion():
    mostrar_login()
    st.stop()


# ==================== USUARIO AUTENTICADO ====================

# Inicializar IA
ai_ready = init_ai()

# Inicializar estado con query params
if 'practica_sel' not in st.session_state:
    st.session_state.practica_sel = get_initial_page()


def seleccionar(key):
    """Selecciona una practica y actualiza URL"""
    st.session_state.practica_sel = key
    st.query_params["p"] = key


def render_menu_item(practica_key):
    """Renderiza un item del menu"""
    label = PRACTICAS[practica_key]['titulo']

    if st.button(label, key=f"b_{practica_key}", use_container_width=True):
        seleccionar(practica_key)
        st.rerun()


# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo
    logo_b64 = get_logo_base64()
    if logo_b64:
        st.markdown(
            f'''<div class="sidebar-logo">
                <img src="data:image/png;base64,{logo_b64}" alt="YoCreo">
            </div>''',
            unsafe_allow_html=True
        )

    # ===== ADMINISTRACIÓN =====
    st.markdown("<p class='cat-title'>Administración</p>", unsafe_allow_html=True)

    # Bienvenido a la plataforma
    if st.button("Bienvenido a la plataforma", key="b_introduccion", use_container_width=True):
        seleccionar("introduccion")
        st.rerun()

    # Administrar Cuenta (solo para admin de empresa)
    user_role = st.session_state.get('user_role', {})
    if user_role.get('tipo') == 'empresa_admin':
        if st.button("Administrar Cuenta", key="b_admin_panel", use_container_width=True):
            seleccionar("admin_panel")
            st.rerun()

    # Cerrar sesión
    if st.button("Cerrar sesión", key="b_logout", use_container_width=True):
        cerrar_sesion()
        st.rerun()


    # ===== AUTOGESTIÓN Y FOCO =====
    st.markdown("<p class='cat-title'>Autogestión y Foco</p>", unsafe_allow_html=True)
    for p in CATEGORIAS["autogestion"]["practicas"]:
        render_menu_item(p)

    # ===== COORDINACIÓN IMPECABLE =====
    st.markdown("<p class='cat-title'>Coordinación Impecable</p>", unsafe_allow_html=True)
    for p in CATEGORIAS["coordinacion"]["practicas"]:
        render_menu_item(p)

    # ===== DESARROLLO DE OTROS =====
    st.markdown("<p class='cat-title'>Desarrollo de Otros</p>", unsafe_allow_html=True)
    for p in CATEGORIAS["desarrollo"]["practicas"]:
        render_menu_item(p)

    # ===== ESTRATEGIA Y RELACIONES =====
    st.markdown("<p class='cat-title'>Estrategia y Relaciones</p>", unsafe_allow_html=True)
    for p in CATEGORIAS["estrategia"]["practicas"]:
        render_menu_item(p)


# ==================== CONTENIDO PRINCIPAL ====================

if not ai_ready:
    st.stop()

practica_seleccionada = st.session_state.practica_sel

# Importar y mostrar la practica seleccionada
if practica_seleccionada == "introduccion":
    from practicas.introduccion import render
    render()
elif practica_seleccionada == "priorizador_tareas":
    from practicas.priorizador_tareas import render
    render()
elif practica_seleccionada == "planificador_reuniones":
    from practicas.planificador_reuniones import render
    render()
elif practica_seleccionada == "pedidos_impecables":
    from practicas.pedidos_impecables import render
    render()
elif practica_seleccionada == "delegacion_situacional":
    from practicas.delegacion_situacional import render
    render()
elif practica_seleccionada == "correos_diplomaticos":
    from practicas.correos_diplomaticos import render
    render()
elif practica_seleccionada == "seguimiento_compromisos":
    from practicas.seguimiento_compromisos import render
    render()
elif practica_seleccionada == "escucha_activa":
    from practicas.escucha_activa import render
    render()
elif practica_seleccionada == "feedback_constructivo":
    from practicas.feedback_constructivo import render
    render()
elif practica_seleccionada == "evaluacion_desempeno":
    from practicas.evaluacion_desempeno import render
    render()
elif practica_seleccionada == "negociador_harvard":
    from practicas.negociador_harvard import render
    render()
elif practica_seleccionada == "presentacion_inspiradora":
    from practicas.presentacion_inspiradora import render
    render()
elif practica_seleccionada == "preguntas_desafiantes":
    from practicas.preguntas_desafiantes import render
    render()
elif practica_seleccionada == "definicion_objetivos":
    from practicas.definicion_objetivos import render
    render()
elif practica_seleccionada == "disculpas_efectivas":
    from practicas.disculpas_efectivas import render
    render()
elif practica_seleccionada == "admin_panel":
    from practicas.admin_panel import render
    render()
else:
    st.markdown('<div class="custom-warning">Practica no disponible</div>', unsafe_allow_html=True)
