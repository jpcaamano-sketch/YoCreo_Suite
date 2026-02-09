"""
Priorizador de Tareas - YoCreo Suite
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


def priorizar_tareas(lista_tareas, rol):
    """Usa IA para clasificar tareas en la Matriz Eisenhower."""
    prompt = f"""Actua como un Experto en Productividad.
Rol del usuario: "{rol}".
Lista de tareas:
"{lista_tareas}"

Tu tarea:
1. Clasificar las tareas en la Matriz Eisenhower.
2. Debes devolver las tareas como una lista con vinetas (usando "- ").

REGLAS DE FORMATO:
1. NO uses Markdown (ni negritas **, ni cursivas *, ni encabezados #).
2. Texto plano limpio.

RESPONDE SOLO JSON:
{{
    "hacer_ya": "- Tarea 1\\n- Tarea 2...",
    "planificar": "- Tarea A\\n- Tarea B...",
    "delegar": "- Tarea X\\n- Tarea Y...",
    "eliminar": "- Tarea Z...",
    "consejo_final": "Consejo breve..."
}}"""

    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Priorizador de Tareas."""
    info = PRACTICAS["priorizador_tareas"]

    # ==================== CAJA 1: ENCABEZADO ====================
    with st.container(border=True):
        render_encabezado("priorizador_tareas", info['titulo'], info['descripcion'])

        with st.expander("Ayuda: Matriz Eisenhower"):
            st.write("""
            La matriz clasifica tareas en 4 cuadrantes:

            1. HACER YA: Urgente + Importante
            2. PLANIFICAR: No urgente + Importante
            3. DELEGAR: Urgente + No importante
            4. ELIMINAR: No urgente + No importante
            """)

    # Estado de sesion
    if 'eisen_resultado' not in st.session_state:
        st.session_state.eisen_resultado = None

    # ==================== CAJA 2: INPUTS ====================
    with st.container(border=True):
        st.markdown("#### Tu Lista de Tareas")

        rol = st.text_input(
            "Tu Rol (opcional)",
            placeholder="Ej: Gerente Comercial",
            key="priorizador_rol"
        )

        lista = st.text_area(
            "Pega aqui todas tus pendientes (una por linea)",
            placeholder="- Enviar reporte mensual\n- Comprar cafe\n- Llamar al cliente X...",
            height=150,
            key="priorizador_lista"
        )

        if st.button("Priorizar Tareas", use_container_width=True):
            if lista:
                rol_final = rol if rol else "Profesional"
                with st.spinner("Organizando prioridades..."):
                    res = priorizar_tareas(lista, rol_final)
                    if res and "hacer_ya" in res:
                        resultado = f"""1. HACER YA (Urgente + Importante)
{res['hacer_ya']}

2. PLANIFICAR (No urgente + Importante)
{res['planificar']}

3. DELEGAR (Urgente + No importante)
{res['delegar']}

4. ELIMINAR (No urgente + No importante)
{res['eliminar']}

CONSEJO ESTRATEGICO:
{res['consejo_final']}"""
                        st.session_state.eisen_resultado = resultado
                        registrar_uso("priorizador_tareas")
                    else:
                        st.markdown('<div class="custom-error">No se pudo generar la priorizacion. Intenta de nuevo.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="custom-warning">Por favor ingresa una lista de tareas.</div>', unsafe_allow_html=True)

    # ==================== CAJA 3: RESULTADOS ====================
    if st.session_state.eisen_resultado:
        with st.container(border=True):
            st.markdown("#### Matriz de Prioridades")

            st.session_state.eisen_resultado = st.text_area(
                "Resultado editable:",
                value=st.session_state.eisen_resultado,
                height=400,
                key="edit_eisen",
                label_visibility="collapsed"
            )

        copy_button_component(st.session_state.eisen_resultado, key="copy_eisen")

        # ==================== CAJA 4: DESCARGA ====================
        with st.container(border=True):
            st.markdown("#### Descargar")

            col1, col2 = st.columns(2)
            with col1:
                nombre_archivo = st.text_input(
                    "Nombre del archivo",
                    value="mis_prioridades",
                    key="priorizador_nombre"
                )
            with col2:
                fmt = st.selectbox(
                    "Formato",
                    ["PDF", "Texto (.txt)"],
                    key="priorizador_formato"
                )

            if fmt == "PDF":
                pdf_data = create_pdf_reportlab(
                    "Matriz de Priorizacion Eisenhower",
                    [("Resultado", st.session_state.eisen_resultado)]
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
                    data=st.session_state.eisen_resultado,
                    file_name=f"{nombre_archivo}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
