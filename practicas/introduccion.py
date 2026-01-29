"""
Introduccion - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
from core.config import PRACTICAS


def render():
    """Renderiza la introduccion de la Suite."""
    info = PRACTICAS["introduccion"]

    with st.container(border=True):
        st.markdown(f"### {info['titulo']}")

        st.markdown("""
        <div style="font-size: 16px; line-height: 1.8; color: #333; text-align: justify; padding: 10px 0;">
            Puedes concebir la <strong style="color: #4E32AD;">'Suite Liderazgo Consciente'</strong> como un ecosistema dual:
            por un lado, un set práctico de herramientas; por el otro, un camino de evolución personal.
        </div>

        <div style="font-size: 16px; line-height: 1.8; color: #333; text-align: justify; padding: 10px 0;">
            Un viaje que va desde el <strong style="color: #FF6B4E;">dominio interior</strong> (autogestión),
            pasando por la <strong style="color: #FF6B4E;">excelencia con otros</strong> (coordinación),
            hasta alcanzar la <strong style="color: #FF6B4E;">maestría en la visión estratégica</strong>.
        </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### El Camino del Lider Consciente")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **1. Autogestión y Foco**
            - Priorizar con claridad
            - Presentar con impacto

            **2. Coordinación Impecable**
            - Pedir con precisión
            - Delegar con inteligencia
            - Comunicar con diplomacia
            - Cumplir compromisos
            """)

        with col2:
            st.markdown("""
            **3. Desarrollo de Otros**
            - Escuchar activamente
            - Preguntar con profundidad
            - Dar feedback constructivo
            - Evaluar con justicia

            **4. Estrategia y Relaciones**
            - Definir objetivos claros
            - Planificar reuniones efectivas
            - Negociar con maestría
            - Reparar vínculos
            """)
