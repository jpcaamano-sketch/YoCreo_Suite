"""
Priorizador de Tareas - YoCreo Suite
Organiza tus tareas pendientes con la Matriz de Eisenhower
"""

import streamlit as st
import json
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import create_word_document, create_pdf_document, get_word_mime, get_pdf_mime, copy_button


def analyze_tasks(tasks, role):
    """Analiza tareas y las clasifica en la matriz de Eisenhower"""
    prompt = f"""
    Actúa como un experto en productividad para un "{role}".
    Clasifica estas tareas en la Matriz de Eisenhower.

    TAREAS:
    {tasks}

    FORMATO JSON REQUERIDO (Estrictamente solo JSON):
    {{
        "hacer": ["tarea 1", "tarea 2"],
        "planificar": ["tarea 3"],
        "delegar": ["tarea 4"],
        "eliminar": ["tarea 5"],
        "recomendacion_top": "Un consejo breve de una frase sobre el foco de hoy"
    }}
    """

    response = generate_response(prompt)
    if response:
        try:
            clean_text = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except:
            return None
    return None


def render():
    """Renderiza la práctica Priorizador de Tareas"""
    info = PRACTICAS["priorizador_tareas"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    # Roles predefinidos
    ROLES_PREDEFINIDOS = [
        "Selecciona un rol...",
        "Gerente / Director",
        "Jefatura / Encargado",
        "Jefe de Turno / Supervisor",
        "Emprendedor / Dueño de negocio",
        "Profesional independiente",
        "Ejecutivo de ventas",
        "Abogado / Contador",
        "Médico / Profesional de salud",
        "Profesor / Educador",
        "Diseñador / Creativo",
        "Desarrollador / IT",
        "Dueña(o) de casa",
        "Estudiante",
        "Otro (escribir)"
    ]

    # Inputs
    with st.container(border=True):
        st.markdown("**Tu rol o cargo:**")
        rol_seleccionado = st.selectbox(
            "Selecciona un rol predefinido:",
            options=ROLES_PREDEFINIDOS,
            index=0,
            label_visibility="collapsed"
        )

        # Si elige "Otro", mostrar campo de texto
        if rol_seleccionado == "Otro (escribir)":
            st.markdown("**Especifica tu rol:**")
            user_role = st.text_input(
                "Escribe tu rol o cargo:",
                placeholder="Ej: Consultor de marketing, Chef, Arquitecto...",
                label_visibility="collapsed"
            )
        elif rol_seleccionado == "Selecciona un rol...":
            user_role = ""
        else:
            user_role = rol_seleccionado

        st.markdown("**Tu lista de pendientes:**")
        tasks_input = st.text_area(
            "Escribe tus tareas aquí (una por línea):",
            height=100,
            placeholder="Revisar contrato del cliente X\nComprar cartulina para el hijo\nLlamar al contador...",
            label_visibility="collapsed"
        )

    # Estado
    if 'priorizador_resultado' not in st.session_state:
        st.session_state.priorizador_resultado = None

    # Botón
    if st.button("🚀 Priorizar Ahora", type="primary", use_container_width=True):
        if not tasks_input:
            st.warning("⚠️ La lista está vacía. Escribe algo para comenzar.")
        else:
            with st.spinner("Analizando urgencia e importancia..."):
                result = analyze_tasks(tasks_input, user_role or "Profesional ocupado")
                if result:
                    st.session_state.priorizador_resultado = result
                    st.session_state.priorizador_tareas = tasks_input
                    st.session_state.priorizador_rol = user_role
                else:
                    st.error("Error al procesar las tareas")

    # Resultados
    if st.session_state.priorizador_resultado:
        result = st.session_state.priorizador_resultado

        st.divider()

        # Fila superior
        col1, col2 = st.columns(2)
        with col1:
            st.success("🔥 1. HACER YA (Urgente e Importante)")
            for t in result.get("hacer", []):
                st.write(f"• {t}")
            if not result.get("hacer"):
                st.write("*Nada por aquí*")

        with col2:
            st.info("📅 2. PLANIFICAR (No Urgente pero Importante)")
            for t in result.get("planificar", []):
                st.write(f"• {t}")
            if not result.get("planificar"):
                st.write("*Nada por aquí*")

        st.divider()

        # Fila inferior
        col3, col4 = st.columns(2)
        with col3:
            st.warning("🤝 3. DELEGAR (Urgente pero No Importante)")
            for t in result.get("delegar", []):
                st.write(f"• {t}")
            if not result.get("delegar"):
                st.write("*Nada por aquí*")

        with col4:
            st.error("🗑️ 4. ELIMINAR (Ni Urgente ni Importante)")
            for t in result.get("eliminar", []):
                st.write(f"• {t}")
            if not result.get("eliminar"):
                st.write("*Nada por aquí*")

        # Preparar texto para copiar (toda la matriz)
        matriz_text = f"""HACER YA (Urgente e Importante):
{chr(10).join(['- ' + t for t in result.get('hacer', [])]) or '(ninguna)'}

PLANIFICAR (No Urgente pero Importante):
{chr(10).join(['- ' + t for t in result.get('planificar', [])]) or '(ninguna)'}

DELEGAR (Urgente pero No Importante):
{chr(10).join(['- ' + t for t in result.get('delegar', [])]) or '(ninguna)'}

ELIMINAR (Ni Urgente ni Importante):
{chr(10).join(['- ' + t for t in result.get('eliminar', [])]) or '(ninguna)'}

Consejo: {result.get('recomendacion_top', '')}"""

        # Consejo y botón copiar
        col_consejo, col_copy = st.columns([5, 1])
        with col_consejo:
            st.info(f"**Consejo del Coach:** {result.get('recomendacion_top', '')}")
        with col_copy:
            copy_button(matriz_text, "Copiar", key="copy_matriz")

        st.divider()

        # Descarga
        st.subheader("📥 Descargar Matriz")
        c_name, c_type = st.columns([2, 1])
        with c_name:
            f_name = st.text_input("Nombre del archivo:", value="Matriz_Eisenhower")
        with c_type:
            f_fmt = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True)

        hacer_text = "\n".join([f"• {t}" for t in result.get("hacer", [])])
        planificar_text = "\n".join([f"• {t}" for t in result.get("planificar", [])])
        delegar_text = "\n".join([f"• {t}" for t in result.get("delegar", [])])
        eliminar_text = "\n".join([f"• {t}" for t in result.get("eliminar", [])])

        secciones = [
            ("1. HACER YA (Urgente e Importante)", hacer_text or "Ninguna"),
            ("2. PLANIFICAR (No Urgente pero Importante)", planificar_text or "Ninguna"),
            ("3. DELEGAR (Urgente pero No Importante)", delegar_text or "Ninguna"),
            ("4. ELIMINAR (Ni Urgente ni Importante)", eliminar_text or "Ninguna"),
            ("Consejo del Coach", result.get('recomendacion_top', ''))
        ]

        if f_fmt == "Word (.docx)":
            data = create_word_document("Matriz de Eisenhower", secciones)
            mime = get_word_mime()
            ext = "docx"
        else:
            data = create_pdf_document("Matriz de Eisenhower", secciones)
            mime = get_pdf_mime()
            ext = "pdf"

        st.download_button(
            label=f"💾 Descargar {f_fmt}",
            data=data,
            file_name=f"{f_name}.{ext}",
            mime=mime,
            use_container_width=True
        )
