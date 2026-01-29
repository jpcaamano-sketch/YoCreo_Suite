"""
Preguntas Desafiantes - YoCreo Suite
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


def generar_grow_ai(situacion):
    """Genera preguntas de coaching usando modelo GROW."""
    prompt = f"""Actua como un Master Coach Ejecutivo experto en el modelo GROW.
CONTEXTO: Un lider presenta la siguiente situacion con su equipo: "{situacion}".

OBJETIVO: Generar una "Guia de Conversacion" con preguntas poderosas.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.
3. Usa vinetas simples (-) para listar las preguntas.
4. Usa MAYUSCULAS para los titulos de las etapas (ej: META, REALIDAD).

ESTRUCTURA:
META
- Pregunta 1
- Pregunta 2

REALIDAD
- Pregunta 1
- Pregunta 2

OPCIONES
- Pregunta 1
- Pregunta 2

VOLUNTAD
- Pregunta 1
- Pregunta 2

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "guia": "Texto completo de la guia de preguntas..."
}}"""
    response = generate_response(prompt)
    if response:
        data = limpiar_json(response)
        if data:
            data['guia'] = data['guia'].replace("**", "").replace("##", "").replace("__", "")
            return data
    return None


def render():
    """Renderiza la practica Preguntas Desafiantes."""
    info = PRACTICAS["preguntas_desafiantes"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("preguntas_desafiantes", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Modelo GROW"):
            st.write("""
            Esta herramienta genera preguntas estrategicas para cada etapa:

            - G (Goal): Que quieres lograr.
            - R (Reality): Que esta pasando hoy.
            - O (Options): Que podrias hacer.
            - W (Will): Que haras concretamente.
            """)

    # Estado de sesion
    if 'grow_resultado' not in st.session_state:
        st.session_state.grow_resultado = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Describe la Situacion")

        situacion_in = st.text_area(
            "Describe la situacion o bloqueo del empleado:",
            placeholder="Ej: Mi reporte dice que no tiene tiempo para innovar porque la operacion lo consume.",
            height=100,
            key="grow_input"
        )

        if st.button("Generar Preguntas", use_container_width=True):
            if situacion_in:
                with st.spinner("Disenando estrategia..."):
                    data = generar_grow_ai(situacion_in)
                    if data:
                        st.session_state.grow_resultado = data['guia']
                    else:
                        st.markdown('<div class="custom-error">No se pudieron generar las preguntas. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Por favor describe la situacion primero.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.grow_resultado:
        with st.container(border=True):
            st.markdown("#### Guia de Coaching")

            st.session_state.grow_resultado = st.text_area(
                "Guia editable:",
                value=st.session_state.grow_resultado,
                height=350,
                key="edit_grow",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.grow_resultado, key="copy_grow")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value="Guia_GROW",
                    key="grow_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="grow_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Guia de Coaching (GROW)",
                    [("Preguntas", st.session_state.grow_resultado)]
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
                    data=st.session_state.grow_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
