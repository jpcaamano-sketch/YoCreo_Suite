"""
Evaluacion de Desempeno - YoCreo Suite
Detector de Sesgos Inconscientes en evaluaciones
"""

import streamlit as st
import json
import re
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import (
    create_word_document, create_pdf_document,
    get_word_mime, get_pdf_mime, copy_button, text_area_with_copy
)


def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener JSON valido."""
    try:
        texto = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto)
    except:
        match = re.search(r'(\{.*\}|\[.*\])', texto, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None


def analizar_evaluacion(texto_evaluacion):
    """Analiza el texto en busca de sesgos inconscientes."""

    prompt = f"""Actua como un Experto en Diversidad e Inclusion. Analiza esta evaluacion de desempeno.

TEXTO: "{texto_evaluacion}"

INSTRUCCIONES:
1. Detecta sesgos (Genero, Recencia, Efecto Halo, Subjetividad, Afinidad, Confirmacion).
2. Reescribe el texto eliminando los sesgos.

RESPONDE SOLO JSON:
{{
    "puntaje_neutralidad": (1-100),
    "analisis_detallado": [
        {{
            "frase_original": "Cita exacta del texto",
            "tipo_sesgo": "Ej: Subjetividad / Genero",
            "explicacion": "Por que es un sesgo",
            "sugerencia": "Como decirlo mejor"
        }}
    ],
    "texto_reescrito": "La version final completa y neutral."
}}"""

    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Evaluacion de Desempeno"""
    info = PRACTICAS["evaluacion_desempeno"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    with st.expander("Tipos de sesgos que detectamos"):
        st.markdown("""
        - **Sesgo de Genero:** Usar adjetivos diferentes para hombres y mujeres
        - **Sesgo de Recencia:** Juzgar solo por eventos recientes
        - **Efecto Halo:** Una caracteristica positiva influye todo el juicio
        - **Subjetividad:** Opiniones sin hechos concretos
        - **Sesgo de Afinidad:** Favorecer a quienes son similares a nosotros
        - **Sesgo de Confirmacion:** Buscar evidencia que confirme prejuicios
        """)

    # Input
    with st.container(border=True):
        st.markdown("**Texto de la evaluación a auditar:**")
        texto_input = st.text_area(
            "Pega aqui el borrador de la evaluacion:",
            height=200,
            placeholder="Ej: Laura es muy emocional y siento que a veces no se enfoca en lo importante. Es buena persona pero...",
            label_visibility="collapsed"
        )

    # Estado
    if 'sesgos_resultado' not in st.session_state:
        st.session_state.sesgos_resultado = None
    if 'sesgos_texto_original' not in st.session_state:
        st.session_state.sesgos_texto_original = None
    if 'sesgos_historial' not in st.session_state:
        st.session_state.sesgos_historial = []

    # Boton de accion
    if st.button("Auditar Texto", type="primary", use_container_width=True):
        if not texto_input or len(texto_input) < 20:
            st.warning("Escribe un texto mas completo para analizar.")
        else:
            with st.spinner("Analizando frase por frase..."):
                st.session_state.sesgos_resultado = analizar_evaluacion(texto_input)
                st.session_state.sesgos_texto_original = texto_input

                # Historial
                if st.session_state.sesgos_resultado:
                    st.session_state.sesgos_historial.insert(0, {
                        "texto": texto_input[:50] + "...",
                        "puntaje": st.session_state.sesgos_resultado.get('puntaje_neutralidad', 0),
                        "resultado": st.session_state.sesgos_resultado
                    })
                    st.session_state.sesgos_historial = st.session_state.sesgos_historial[:5]

    # Mostrar resultados
    if st.session_state.sesgos_resultado:
        datos = st.session_state.sesgos_resultado

        st.divider()

        # Seccion 2: Resultados
        st.subheader("2. Resultados del Analisis")

        # Barra de puntaje
        score = datos.get("puntaje_neutralidad", 0)
        col_score, col_msg = st.columns([3, 1])
        with col_score:
            st.progress(score / 100)
        with col_msg:
            if score >= 80:
                st.success(f"**{score}/100**")
            elif score >= 50:
                st.warning(f"**{score}/100**")
            else:
                st.error(f"**{score}/100**")

        # Lista de alertas
        alertas = datos.get("analisis_detallado", [])
        if alertas:
            st.info(f"Se detectaron {len(alertas)} puntos de mejora.")
            for i, item in enumerate(alertas):
                with st.expander(f"{item.get('tipo_sesgo', 'Sesgo')}: \"{item.get('frase_original', '')[:40]}...\""):
                    st.markdown(f"**Frase original:** *{item.get('frase_original')}*")
                    st.markdown(f"**Por que es sesgo:** {item.get('explicacion')}")
                    st.success(f"**Mejor di:** {item.get('sugerencia')}")

                    # Boton copiar sugerencia
                    copy_button(item.get('sugerencia', ''), "Copiar", key=f"copy_sug_{i}")
        else:
            st.success("Excelente! El texto parece muy objetivo y libre de sesgos evidentes.")

        st.divider()

        # Seccion 3: Version corregida (editable)
        st.subheader("3. Version Corregida (Neutral)")

        texto_reescrito = datos.get("texto_reescrito", "No se genero texto.")

        texto_final_editado = text_area_with_copy(
            "Puedes editar antes de copiar o descargar:",
            texto_reescrito,
            key="texto_reescrito_edit",
            height=200
        )

        st.divider()

        # Seccion 4: Descarga
        st.subheader("4. Descargar Informe")

        col_name, col_type = st.columns([2, 1])
        with col_name:
            nombre_archivo = st.text_input(
                "Nombre del archivo:",
                value="Auditoria_Sesgos",
                help="Sin extension"
            )
        with col_type:
            tipo_archivo = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True)

        secciones = [
            ("Texto Original", st.session_state.sesgos_texto_original or ""),
            ("Analisis de Sesgos", "\n".join([
                f"- {a.get('tipo_sesgo')}: {a.get('frase_original')}\n  Sugerencia: {a.get('sugerencia')}"
                for a in alertas
            ]) if alertas else "Sin sesgos detectados"),
            ("Version Neutral", texto_final_editado)
        ]

        if tipo_archivo == "Word (.docx)":
            data = create_word_document("Auditoria de Sesgos Inconscientes", secciones)
            mime = get_word_mime()
            ext = "docx"
        else:
            data = create_pdf_document("Auditoria de Sesgos Inconscientes", secciones)
            mime = get_pdf_mime()
            ext = "pdf"

        st.download_button(
            label=f"Descargar {tipo_archivo}",
            data=data,
            file_name=f"{nombre_archivo}.{ext}",
            mime=mime,
            use_container_width=True
        )

    # Historial
    st.divider()
    if st.session_state.sesgos_historial:
        with st.expander("Historial de auditorias (ultimas 5)", expanded=False):
            for i, item in enumerate(st.session_state.sesgos_historial):
                st.markdown(f"**{i+1}. Neutralidad: {item['puntaje']}/100**")
                st.caption(f"Texto: {item['texto']}")
                if st.button(f"Cargar", key=f"cargar_sesgo_{i}"):
                    st.session_state.sesgos_resultado = item['resultado']
                    st.rerun()
                st.markdown("---")
