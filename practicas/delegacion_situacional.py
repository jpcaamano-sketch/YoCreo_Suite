"""
Delegación Situacional - YoCreo Suite
Estrategia de liderazgo basada en Hersey & Blanchard
"""

import streamlit as st
import re
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import create_word_document, create_pdf_document, get_word_mime, get_pdf_mime, text_area_with_copy


def analizar_delegacion(tarea, exp, disp):
    """Analiza la situación y genera estrategia de delegación"""
    prompt = f"""
    Actúa como Coach experto en Liderazgo Situacional.
    Tarea: {tarea} | Nivel: {exp} | Disposición: {disp}

    USA EXACTAMENTE ESTOS TÍTULOS PARA SEPARAR LAS SECCIONES:

    SECCION_DIAGNOSTICO:
    [Identifica si es E1, E2, E3 o E4 y explica por qué]

    SECCION_PASOS:
    [Lista 3 pasos clave para la reunión]

    SECCION_GUION:
    [Escribe el diálogo exacto entre comillas]
    """

    response = generate_response(prompt)

    if response:
        texto = response
        diag = re.search(r"SECCION_DIAGNOSTICO:(.*?)(?=SECCION_PASOS:|$)", texto, re.DOTALL | re.IGNORECASE)
        pasos = re.search(r"SECCION_PASOS:(.*?)(?=SECCION_GUION:|$)", texto, re.DOTALL | re.IGNORECASE)
        guion = re.search(r"SECCION_GUION:(.*?)(?=$)", texto, re.DOTALL | re.IGNORECASE)

        return {
            "diagnostico": diag.group(1).strip().replace("*", "") if diag else "Error generando diagnóstico.",
            "pasos": pasos.group(1).strip().replace("*", "") if pasos else "Error generando pasos.",
            "guion": guion.group(1).strip().replace("*", "").replace('"', '') if guion else "Error generando guion."
        }
    return {"error": "No se pudo generar respuesta"}


def render():
    """Renderiza la práctica Delegación Situacional"""
    info = PRACTICAS["delegacion_situacional"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    # Inputs
    with st.container(border=True):
        st.markdown("**Nombre del Colaborador:**")
        nombre_colab = st.text_input("Nombre del Colaborador", value="", placeholder="Ej: Juan Pérez", label_visibility="collapsed")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Nivel de Competencia (Saber):**")
            nivel_experiencia = st.selectbox("Nivel de Competencia", [
                "M1 - Principiante (Baja competencia)",
                "M2 - Aprendiz (Competencia moderada)",
                "M3 - Avanzado (Competencia alta)",
                "M4 - Experto (Alta competencia)"
            ], label_visibility="collapsed")
        with col2:
            st.markdown("**Nivel de Compromiso (Querer):**")
            disposicion = st.selectbox("Nivel de Compromiso", [
                "Bajo (Inseguro o no dispuesto)",
                "Variable (Motivado pero sin experiencia)",
                "Variable (Capaz pero cauteloso)",
                "Alto (Seguro, motivado y capaz)"
            ], label_visibility="collapsed")

        st.markdown("**Tarea a delegar:**")
        tarea = st.text_area("Tarea a delegar", height=100, placeholder="Ej: Realizar el informe mensual...", label_visibility="collapsed")

    # Estado
    if 'delegacion_resultado' not in st.session_state:
        st.session_state.delegacion_resultado = None

    # Botón
    if st.button("🚀 Generar Estrategia", type="primary", use_container_width=True):
        if not tarea:
            st.warning("⚠️ Escribe una tarea primero.")
        else:
            with st.spinner("Analizando situación..."):
                st.session_state.delegacion_resultado = analizar_delegacion(tarea, nivel_experiencia, disposicion)
                st.session_state.delegacion_tarea = tarea
                st.session_state.delegacion_colaborador = nombre_colab

    # Resultados
    if st.session_state.delegacion_resultado:
        res = st.session_state.delegacion_resultado

        if "error" in res:
            st.error(f"Error técnico: {res['error']}")
        else:
            st.caption("Puedes editar los textos antes de copiar o descargar")

            st.markdown("### Diagnóstico")
            diagnostico_edit = text_area_with_copy(
                "Análisis de la situación:",
                res.get('diagnostico', 'Sin datos'),
                key="diagnostico_edit",
                height=100
            )

            st.markdown("### Pasos Clave")
            pasos_edit = text_area_with_copy(
                "Pasos para la reunión:",
                res.get('pasos', 'Sin datos'),
                key="pasos_edit",
                height=120
            )

            st.markdown("### Guion Sugerido")
            guion_edit = text_area_with_copy(
                "Diálogo de conversación:",
                res.get('guion', 'Sin datos'),
                key="guion_edit",
                height=150
            )

            st.divider()

            # Descarga
            st.subheader("📥 Descargar Plan")
            c_name, c_type = st.columns([2, 1])
            with c_name:
                colab = st.session_state.get('delegacion_colaborador', 'Colaborador')
                f_name = st.text_input("Nombre del archivo:", value=f"Delegacion_{colab.split()[0] if colab else 'Plan'}")
            with c_type:
                f_fmt = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True)

            tarea_orig = st.session_state.get('delegacion_tarea', tarea)
            secciones = [
                ("Tarea", tarea_orig),
                ("Colaborador", st.session_state.get('delegacion_colaborador', '')),
                ("1. Diagnóstico", diagnostico_edit),
                ("2. Pasos Clave", pasos_edit),
                ("3. Guion de Conversación", guion_edit)
            ]

            if f_fmt == "Word (.docx)":
                data = create_word_document("Plan de Delegación Situacional", secciones)
                mime = get_word_mime()
                ext = "docx"
            else:
                data = create_pdf_document("Plan de Delegación Situacional", secciones)
                mime = get_pdf_mime()
                ext = "pdf"

            st.download_button(
                label=f"💾 Descargar {f_fmt}",
                data=data,
                file_name=f"{f_name}.{ext}",
                mime=mime,
                use_container_width=True
            )
