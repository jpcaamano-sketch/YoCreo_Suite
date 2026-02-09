"""
Disculpas Efectivas - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import json

from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import copy_button_component, create_pdf_reportlab, render_encabezado
from core.analytics import registrar_uso


def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener JSON valido."""
    try:
        texto_limpio = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except:
        return None


def generar_disculpa_ai(quien, que_paso, excusa):
    """Genera una disculpa efectiva sin justificaciones."""
    prompt = f"""Actua como un experto en Resolucion de Conflictos y Coaching.
El usuario cometio un error con: {quien}.

HECHO (Lo que paso): "{que_paso}"
JUSTIFICACION MENTAL (La excusa que se da): "{excusa}"

TU MISION:
Redacta una DISCULPA EFECTIVA que elimine el "PERO" y la justificacion.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.
3. Usa vinetas simples (-) si es necesario listar.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "analisis": "Breve explicacion de por que su justificacion invalida la disculpa.",
    "guion": "El texto exacto para decir, profesional y humilde.",
    "reparacion": "Una accion concreta sugerida para compensar el dano."
}}"""
    response = generate_response(prompt)
    if response:
        data = limpiar_json(response)
        if data:
            for key in data:
                data[key] = data[key].replace("**", "").replace("##", "")
            return data
    return None


def render():
    """Renderiza la practica Disculpas Efectivas."""
    info = PRACTICAS["disculpas_efectivas"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("disculpas_efectivas", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Metodologia"):
            st.write("""
            Las disculpas no cambian el pasado, pero reparan el futuro.

            Pasos para una disculpa real:
            - Reconocer el hecho sin 'peros'.
            - Validar la emoción del otro.
            - Ofrecer una reparación concreta.
            """)

    # Estado de sesion
    if 'rep_resultado' not in st.session_state:
        st.session_state.rep_resultado = None
    if 'rep_quien' not in st.session_state:
        st.session_state.rep_quien = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos del Caso")

        col1, col2 = st.columns(2)
        with col1:
            quien = st.text_input(
                "A quien ofendiste?",
                placeholder="Ej: Mi Pareja / Cliente",
                key="disc_quien"
            )
        with col2:
            que_paso = st.text_input(
                "Cual fue el error?",
                placeholder="Ej: Olvide el aniversario",
                key="disc_que"
            )

        excusa = st.text_area(
            "Que excusa te estas dando a ti mismo?",
            placeholder="Ej: Es que tenia mucho trabajo...",
            height=100,
            key="disc_excusa"
        )

        if st.button("Disenar Disculpa", use_container_width=True):
            if quien and que_paso:
                with st.spinner("Analizando situacion..."):
                    data = generar_disculpa_ai(quien, que_paso, excusa)
                    if data:
                        resultado = f"""ANALISIS DEL ERROR:
{data['analisis']}

GUION DE DISCULPA:
{data['guion']}

ACCION REPARADORA:
{data['reparacion']}"""
                        st.session_state.rep_resultado = resultado
                        st.session_state.rep_quien = quien
                        registrar_uso("disculpas_efectivas")
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar la disculpa. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Por favor completa a quien y que paso.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.rep_resultado:
        with st.container(border=True):
            st.markdown("#### Plan de Reparacion")

            st.session_state.rep_resultado = st.text_area(
                "Plan editable:",
                value=st.session_state.rep_resultado,
                height=350,
                key="edit_disc",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.rep_resultado, key="copy_disc")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value=f"Disculpa_{st.session_state.rep_quien}",
                    key="disc_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="disc_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    f"Plan de Disculpa para {st.session_state.rep_quien}",
                    [("Plan", st.session_state.rep_resultado)]
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
                    data=st.session_state.rep_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
