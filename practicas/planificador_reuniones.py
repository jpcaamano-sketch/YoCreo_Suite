"""
Planificador de Reuniones - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import copy_button_component, create_pdf_reportlab, render_encabezado


def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener JSON valido."""
    try:
        texto_limpio = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except:
        return None


def generar_planificacion_ai(tema, objetivo, duracion):
    """Genera agenda de reunion estructurada."""
    prompt = f"""Actua como un Facilitador Experto. Disena una agenda para una reunion de {duracion} minutos.
TEMA: {tema}
OBJETIVO: {objetivo}

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "agenda": [
        {{"minutos": "00-05", "actividad": "Inicio y contexto", "responsable": "Lider"}},
        {{"minutos": "05-15", "actividad": "...", "responsable": "..."}}
    ],
    "consejos": "Consejo 1. Consejo 2."
}}"""
    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Planificador de Reuniones."""
    info = PRACTICAS["planificador_reuniones"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("planificador_reuniones", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Reuniones Efectivas"):
            st.write("""
            Una reunion efectiva tiene:

            1. Objetivo claro definido
            2. Agenda con tiempos asignados
            3. Responsables por cada punto
            4. Acuerdos y proximos pasos
            """)

    # Estado de sesion
    if 'agenda_resultado' not in st.session_state:
        st.session_state.agenda_resultado = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos de la Reunion")

        tema_input = st.text_input(
            "Tema",
            placeholder="Ej: Planificacion Q3",
            key="plan_tema"
        )

        obj_input = st.text_input(
            "Objetivo",
            placeholder="Ej: Asignar presupuesto por area",
            key="plan_objetivo"
        )

        duracion_input = st.selectbox(
            "Duracion",
            [15, 30, 45, 60, 90],
            index=3,
            format_func=lambda x: f"{x} minutos",
            key="plan_duracion"
        )

        if st.button("Generar Agenda", use_container_width=True):
            if tema_input and obj_input:
                with st.spinner("Disenando agenda..."):
                    data = generar_planificacion_ai(tema_input, obj_input, duracion_input)
                    if data:
                        txt = f"TEMA: {tema_input}\nOBJETIVO: {obj_input}\nDURACION: {duracion_input} minutos\n\nAGENDA:\n"
                        for item in data['agenda']:
                            txt += f"- {item['minutos']} min: {item['actividad']} ({item['responsable']})\n"
                        txt += f"\nCONSEJOS:\n{data.get('consejos', '')}"
                        st.session_state.agenda_resultado = txt
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar la agenda. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Completa el tema y objetivo.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.agenda_resultado:
        with st.container(border=True):
            st.markdown("#### Agenda Generada")

            st.session_state.agenda_resultado = st.text_area(
                "Agenda editable:",
                value=st.session_state.agenda_resultado,
                height=350,
                key="edit_agenda",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.agenda_resultado, key="copy_agenda")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value="Agenda_Reunion",
                    key="plan_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="plan_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Plan de Reunion",
                    [("Agenda", st.session_state.agenda_resultado)]
                )
                st.download_button(
                    "Descargar PDF",
                    data=pdf_data,
                    file_name=f"{fname}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.download_button(
                    "Descargar TXT",
                    data=st.session_state.agenda_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
