"""
Mi Historial - YoCreo Suite
Muestra las últimas 10 generaciones del usuario.
"""

import streamlit as st
from core.historial import obtener_historial, PRACTICA_NOMBRES
from core.auth import obtener_usuario_actual
from core.export import copy_button_component


def render():
    """Renderiza la página Mi Historial."""
    user = obtener_usuario_actual()
    if not user:
        return

    email = user['email']

    with st.container(border=True):
        st.markdown("## Mi Historial")
        st.markdown(
            "<p style='color:#6c757d;font-size:14px;'>"
            "Tus últimas 10 generaciones guardadas en la plataforma.</p>",
            unsafe_allow_html=True,
        )

    registros = obtener_historial(email, limit=10)

    if not registros:
        st.info("Aún no tienes generaciones guardadas. Usa cualquier práctica para comenzar tu historial.")
        return

    for i, reg in enumerate(registros):
        practica_nombre = PRACTICA_NOMBRES.get(reg['practica'], reg['practica'])
        fecha = reg['created_at'][:16].replace('T', ' ')
        with st.expander(f"{practica_nombre}  —  {fecha}"):
            st.text_area(
                "Contenido:",
                value=reg['contenido'],
                height=280,
                key=f"hist_content_{i}",
                label_visibility="collapsed",
                disabled=True,
            )
            copy_button_component(reg['contenido'], key=f"copy_hist_{i}")
