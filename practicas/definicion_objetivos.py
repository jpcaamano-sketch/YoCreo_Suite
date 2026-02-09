"""
Definicion de Objetivos - YoCreo Suite
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


def generar_objetivos(deseo, rol):
    """Genera objetivos estructurados a partir de un deseo."""
    prompt = f"""Actua como un Experto en Planificacion Estrategica.
El usuario tiene un deseo vago: "{deseo}".
Su rol es: "{rol}".

Tu tarea es transformar ese deseo en una estructura profesional:
1. Un OBJETIVO PRINCIPAL inspirador.
2. Tres OBJETIVOS ESPECIFICOS que sean medibles y concretos.

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *).
2. Texto plano limpio.

Responde EXCLUSIVAMENTE con un JSON valido:
{{
    "objetivo_inspirador": "Texto del objetivo principal...",
    "res1": "Objetivo Especifico 1...",
    "res2": "Objetivo Especifico 2...",
    "res3": "Objetivo Especifico 3...",
    "plan_accion": "Una primera accion sugerida..."
}}"""
    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Definicion de Objetivos."""
    info = PRACTICAS["definicion_objetivos"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("definicion_objetivos", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Como funciona"):
            st.write("""
            Ingresa lo que quieres lograr y la IA lo estructurara en:

            - Un Objetivo Principal inspirador
            - Tres Objetivos Específicos medibles
            - Un primer paso de acción concreto
            """)

    # Estado de sesion
    if 'obj_resultado' not in st.session_state:
        st.session_state.obj_resultado = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Datos Iniciales")

        deseo = st.text_area(
            "Que quieres lograr?",
            placeholder="Ej: Quiero vender mas este ano...",
            height=100,
            key="obj_deseo"
        )

        rol_seleccion = st.selectbox(
            "Define tu Rol",
            ["Emprendedor", "Gerente", "Coach", "Profesional", "Estudiante", "Otro"],
            key="obj_rol_sel"
        )
        if rol_seleccion == "Otro":
            rol = st.text_input(
                "Escribe tu Rol especifico",
                placeholder="Ej: Consultor de Marketing",
                key="obj_rol_otro"
            )
        else:
            rol = rol_seleccion

        if st.button("Generar Objetivos", use_container_width=True):
            if deseo:
                rol_final = rol if rol else "Profesional"
                with st.spinner("Estructurando objetivos..."):
                    res = generar_objetivos(deseo, rol_final)
                    if res:
                        resultado = f"""OBJETIVO PRINCIPAL:
{res['objetivo_inspirador']}

OBJETIVOS ESPECIFICOS:
1. {res['res1']}
2. {res['res2']}
3. {res['res3']}

PRIMER PASO DE ACCION:
{res['plan_accion']}"""
                        st.session_state.obj_resultado = resultado
                        registrar_uso("definicion_objetivos")
                    else:
                        st.markdown('<div class="custom-error">No se pudieron generar los objetivos. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Por favor escribe tu deseo primero.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.obj_resultado:
        with st.container(border=True):
            st.markdown("#### Estrategia Generada")

            st.session_state.obj_resultado = st.text_area(
                "Objetivos editables:",
                value=st.session_state.obj_resultado,
                height=350,
                key="edit_obj",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.obj_resultado, key="copy_obj")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                nombre_archivo = st.text_input(
                    "Nombre del archivo",
                    value="mis_objetivos",
                    key="obj_fname"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="obj_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Plan de Objetivos",
                    [("Estrategia", st.session_state.obj_resultado)]
                )
                st.download_button(
                    "Descargar PDF",
                    data=pdf_data,
                    file_name=f"{nombre_archivo}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.download_button(
                    "Descargar TXT",
                    data=st.session_state.obj_resultado,
                    file_name=f"{nombre_archivo}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
