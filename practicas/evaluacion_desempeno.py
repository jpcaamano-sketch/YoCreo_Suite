"""
Evaluacion de Desempeno - YoCreo Suite
Protocolo Estandar v2.0
"""

import streamlit as st
import json

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


def analizar_sesgos_ai(texto_evaluacion):
    """Analiza sesgos inconscientes en una evaluacion de desempeno."""
    prompt = f"""Actua como un Experto en Diversidad e Inclusion. Analiza esta evaluacion de desempeno.

TEXTO: "{texto_evaluacion}"

INSTRUCCIONES:
1. Detecta sesgos inconscientes (Genero, Recencia, Halo, Subjetividad, Afinidad).
2. Reescribe el texto eliminando los sesgos, dejandolo neutral y basado en hechos.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.
3. En la lista de sesgos, usa vinetas simples (-).

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "puntaje": "Un numero del 1 al 100 indicando nivel de neutralidad actual.",
    "analisis": "Lista con vinetas (-) de los sesgos especificos encontrados y por que.",
    "texto_neutral": "La version reescrita completa, profesional y objetiva."
}}"""
    response = generate_response(prompt)
    if response:
        data = limpiar_json(response)
        if data:
            for key in data:
                if isinstance(data[key], str):
                    data[key] = data[key].replace("**", "").replace("##", "").replace("[", "").replace("]", "")
            return data
    return None


def render():
    """Renderiza la practica Evaluacion de Desempeno."""
    info = PRACTICAS["evaluacion_desempeno"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("evaluacion_desempeno", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Tipos de Sesgos"):
            st.write("""
            Esta herramienta analiza tus borradores de evaluacion para asegurar que sean justos:

            - Genero: Adjetivos diferentes para hombres/mujeres.
            - Recencia: Juzgar solo por lo ultimo que paso.
            - Halo: Una caracteristica buena tapa todo lo malo.
            - Subjetividad: Opiniones en lugar de hechos.
            """)

    # Estado de sesion
    if 'sesgos_resultado' not in st.session_state:
        st.session_state.sesgos_resultado = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Texto a Auditar")

        texto_input = st.text_area(
            "Ingresa el borrador de la evaluacion:",
            placeholder="Ej: Laura es muy emocional y siento que no se enfoca en lo importante...",
            height=150,
            key="eval_texto"
        )

        if st.button("Auditar Texto", use_container_width=True):
            if texto_input and len(texto_input) >= 10:
                with st.spinner("Detectando sesgos..."):
                    data = analizar_sesgos_ai(texto_input)
                    if data:
                        resultado = f"""PUNTAJE DE NEUTRALIDAD: {data['puntaje']}/100

ANALISIS DE SESGOS:
{data['analisis']}

--------------------------------------------------

VERSION CORREGIDA (Neutral):
{data['texto_neutral']}"""
                        st.session_state.sesgos_resultado = resultado
                    else:
                        st.markdown('<div class="custom-error">No se pudo analizar el texto. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Escribe un texto mas completo para analizar (minimo 10 caracteres).</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.sesgos_resultado:
        with st.container(border=True):
            st.markdown("#### Informe de Auditoria")

            st.session_state.sesgos_resultado = st.text_area(
                "Informe editable:",
                value=st.session_state.sesgos_resultado,
                height=450,
                key="edit_sesgos",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.sesgos_resultado, key="copy_sesgos")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value="Auditoria_Sesgos",
                    key="eval_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="eval_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Auditoria de Sesgos Inconscientes",
                    [("Informe", st.session_state.sesgos_resultado)]
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
                    data=st.session_state.sesgos_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
