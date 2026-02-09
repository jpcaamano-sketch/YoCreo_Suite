"""
Delegacion Situacional - YoCreo Suite
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


def generar_estrategia_ai(tarea, nivel, disposicion):
    """Genera estrategia de delegación basada en liderazgo situacional."""
    prompt = f"""Actua como un Coach experto en Liderazgo Situacional (Hersey & Blanchard).
TAREA A DELEGAR: {tarea}
NIVEL DE COMPETENCIA (Hacer): {nivel}
NIVEL DE COMPROMISO (Querer): {disposicion}

Genera una estrategia de delegacion precisa.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.
3. En la seccion pasos, usa vinetas simples con guion (-).

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "diagnostico": "Identifica si es E1, E2, E3 o E4 y explica el estilo (Dirigir, Persuadir, Participar o Delegar).",
    "pasos": "- Paso 1: ...\\n- Paso 2: ...\\n- Paso 3: ...",
    "guion": "Escribe un guión directo y conversacional para iniciar la delegación."
}}"""
    response = generate_response(prompt)
    if response:
        data = limpiar_json(response)
        if data:
            for key in data:
                data[key] = data[key].replace("**", "").replace("[", "").replace("]", "")
            return data
    return None


def render():
    """Renderiza la practica Delegacion Situacional."""
    info = PRACTICAS["delegacion_situacional"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("delegacion_situacional", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Los 4 Estilos de Liderazgo"):
            st.write("""
            Esta herramienta analiza el nivel de competencia y compromiso de tu colaborador:

            - E1 - Dirigir: Alta instrucción, bajo apoyo. (Para principiantes).
            - E2 - Persuadir: Alta instrucción, alto apoyo. (Para aprendices motivados).
            - E3 - Participar: Baja instrucción, alto apoyo. (Para capaces pero inseguros).
            - E4 - Delegar: Baja instrucción, bajo apoyo. (Para expertos autónomos).
            """)

    # Estado de sesion
    if 'deleg_resultado' not in st.session_state:
        st.session_state.deleg_resultado = None
    if 'deleg_colab' not in st.session_state:
        st.session_state.deleg_colab = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos del Colaborador")

        colab_input = st.text_input(
            "Nombre del Colaborador",
            placeholder="Ej: Juan Pérez",
            key="deleg_nombre"
        )

        col1, col2 = st.columns(2)
        with col1:
            nivel_input = st.selectbox(
                "Nivel de Competencia (Hacer)",
                [
                    "Principiante (No hace)",
                    "Aprendiz (Empezando a hacer)",
                    "Avanzado (Hace bastante y a veces consulta)",
                    "Experto (Hace y dicta cátedra)"
                ],
                key="deleg_nivel"
            )
        with col2:
            disp_input = st.selectbox(
                "Nivel de Compromiso (Querer)",
                [
                    "Bajo (Inseguro o no quiere)",
                    "Variable (Motivado pero inexperto)",
                    "Variable (Capaz pero cauteloso)",
                    "Alto (Motivado y seguro)"
                ],
                key="deleg_disposicion"
            )

        tarea_input = st.text_area(
            "Tarea a delegar",
            placeholder="Ej: Realizar el informe mensual de ventas...",
            height=100,
            key="deleg_tarea_input"
        )

        if st.button("Generar Estrategia", use_container_width=True):
            if colab_input and tarea_input:
                with st.spinner("Analizando estilo de liderazgo..."):
                    data = generar_estrategia_ai(tarea_input, nivel_input, disp_input)
                    if data:
                        res_texto = f"""DIAGNOSTICO:
{data['diagnostico']}

PASOS:
{data['pasos']}

GUION DE CONVERSACION:
{data['guion']}"""
                        st.session_state.deleg_resultado = res_texto
                        st.session_state.deleg_colab = colab_input
                        registrar_uso("delegacion_situacional")
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar la estrategia. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Ingresa el nombre del colaborador y la tarea.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.deleg_resultado:
        with st.container(border=True):
            st.markdown("#### Estrategia de Delegación")

            st.session_state.deleg_resultado = st.text_area(
                "Estrategia editable:",
                value=st.session_state.deleg_resultado,
                height=350,
                key="edit_deleg",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.deleg_resultado, key="copy_deleg")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value=f"Delegacion_{st.session_state.deleg_colab}",
                    key="deleg_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="deleg_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Plan de Delegación Situacional",
                    [("Estrategia", st.session_state.deleg_resultado)]
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
                    data=st.session_state.deleg_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
