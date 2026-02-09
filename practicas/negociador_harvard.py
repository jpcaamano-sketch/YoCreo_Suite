"""
Negociador Harvard - YoCreo Suite
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


def generar_negociacion_ai(rol, contraparte, problema, intereses_mios, intereses_ellos, maan):
    """Genera estrategia de negociacion estilo Harvard."""
    prompt = f"""Actua como un Experto en Negociacion del 'Harvard Negotiation Project' (Fisher & Ury).

CONTEXTO:
- Usuario: {rol}
- Contraparte: {contraparte}
- Conflicto: {problema}
- Intereses Usuario: {intereses_mios}
- Intereses Contraparte: {intereses_ellos}
- MAAN (Plan B): {maan}

TAREA: Genera una hoja de ruta estrategica.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.
3. Usa vinetas simples (-) para listas.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "diagnostico": "Analisis breve del poder y el MAAN...",
    "estrategia_creativa": "Propuesta de valor y frase de apertura (Speech exacto)...",
    "criterios": "Criterios objetivos a utilizar si se ponen duros...",
    "preguntas": "3 preguntas poderosas para descubrir informacion..."
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
    """Renderiza la practica Negociador Harvard."""
    info = PRACTICAS["negociador_harvard"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("negociador_harvard", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Metodo Harvard"):
            st.write("""
            Este metodo busca acuerdos sensatos de mutuo beneficio:

            - Intereses: Enfocate en lo que necesitan, no en lo que piden.
            - Opciones: Busca soluciones creativas donde ambos ganen.
            - Criterios: Usa datos objetivos (mercado, ley) para decidir.
            - MAAN: Tu 'As bajo la manga' (Mejor Alternativa al Acuerdo Negociado).
            """)

    # Estado de sesion
    if 'harvard_resultado' not in st.session_state:
        st.session_state.harvard_resultado = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos de la Negociacion")

        col1, col2 = st.columns(2)
        with col1:
            rol = st.text_input(
                "Tu Rol",
                placeholder="Ej: Proveedor de Servicios",
                key="harvard_rol"
            )
            intereses_mios = st.text_area(
                "Tus Intereses (Para que lo quieres?)",
                placeholder="Estabilidad, prestigio...",
                height=100,
                key="harvard_mis_int"
            )
        with col2:
            contraparte = st.text_input(
                "La Contraparte",
                placeholder="Ej: Gerente de Compras",
                key="harvard_contra"
            )
            intereses_ellos = st.text_area(
                "Intereses de Ellos (Que les preocupa?)",
                placeholder="Presupuesto, plazos...",
                height=100,
                key="harvard_sus_int"
            )

        problema = st.text_area(
            "Conflicto a negociar",
            placeholder="Ej: Renovacion de contrato con aumento de tarifas...",
            height=80,
            key="harvard_problema"
        )
        maan = st.text_input(
            "Tu MAAN (Plan B si no hay acuerdo)",
            placeholder="Ej: Tengo otra oferta lista...",
            key="harvard_maan"
        )

        if st.button("Generar Estrategia", use_container_width=True):
            if rol and intereses_mios and maan:
                with st.spinner("Analizando intereses y opciones..."):
                    data = generar_negociacion_ai(rol, contraparte, problema, intereses_mios, intereses_ellos, maan)
                    if data:
                        resultado = f"""DIAGNOSTICO:
{data['diagnostico']}

ESTRATEGIA:
{data['estrategia_creativa']}

CRITERIOS:
{data['criterios']}

PREGUNTAS:
{data['preguntas']}"""
                        st.session_state.harvard_resultado = resultado
                        registrar_uso("negociador_harvard")
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar la estrategia. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Define al menos tu Rol, tus Intereses y tu MAAN.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.harvard_resultado:
        with st.container(border=True):
            st.markdown("#### Hoja de Ruta")

            st.session_state.harvard_resultado = st.text_area(
                "Estrategia editable:",
                value=st.session_state.harvard_resultado,
                height=400,
                key="edit_harvard",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.harvard_resultado, key="copy_harvard")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(
                    "Nombre del archivo",
                    value="Estrategia_Harvard",
                    key="harvard_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="harvard_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Estrategia de Negociacion Harvard",
                    [("Estrategia", st.session_state.harvard_resultado)]
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
                    data=st.session_state.harvard_resultado,
                    file_name=f"{fname}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
