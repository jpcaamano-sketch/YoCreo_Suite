"""
Seguimiento de Compromisos - YoCreo Suite
Reclama cumplimiento de compromisos de forma asertiva
"""

import streamlit as st
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import create_word_document, create_pdf_document, get_word_mime, get_pdf_mime, text_area_with_copy


def generar_seguimiento(compromiso, persona, relacion, intentos_previos, urgencia, consecuencias):
    """Genera mensaje de seguimiento asertivo"""
    separador = "|||"

    prompt = f"""Eres un experto en comunicación asertiva y seguimiento de compromisos.

CONTEXTO:
- Compromiso pendiente: {compromiso}
- Persona responsable: {persona}
- Relación con esa persona: {relacion}
- Intentos previos de seguimiento: {intentos_previos}
- Nivel de urgencia: {urgencia}
- Consecuencias si no se cumple: {consecuencias}

OBJETIVO: Genera 3 versiones de un mensaje de seguimiento/reclamo que sea:
- Asertivo pero respetuoso
- Claro sobre el compromiso y la expectativa
- Firme sin ser agresivo
- Orientado a la solución

REGLAS:
- NO incluyas frases introductorias
- SOLO el mensaje listo para enviar
- Adapta el tono según la relación y urgencia

Usa EXACTAMENTE este formato con el separador "{separador}":

Versión Suave:
[Mensaje amable pero claro, ideal para primer seguimiento]
{separador}
Versión Firme:
[Mensaje directo y profesional, ideal cuando ya hubo intentos previos]
{separador}
Versión Formal:
[Mensaje serio con mención de consecuencias, ideal para casos urgentes]"""

    response = generate_response(prompt)

    if response:
        partes = response.replace("*", "").split(separador)
        return {
            "suave": partes[0].replace("Versión Suave:", "").strip() if len(partes) > 0 else "Error",
            "firme": partes[1].replace("Versión Firme:", "").strip() if len(partes) > 1 else "Error",
            "formal": partes[2].replace("Versión Formal:", "").strip() if len(partes) > 2 else "Error"
        }
    return {"error": "No se pudo generar respuesta"}


def render():
    """Renderiza la práctica Seguimiento de Compromisos"""
    info = PRACTICAS["seguimiento_compromisos"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    with st.expander("💡 ¿Cuándo usar esta herramienta?"):
        st.info("""
        Úsala cuando:
        - Alguien no cumplió un compromiso contigo
        - Necesitas hacer seguimiento sin parecer controlador
        - Quieres reclamar de forma profesional
        - Debes escalar un tema sin dañar la relación
        """)

    # Inputs
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**¿Quién tiene el compromiso?**")
            persona = st.text_input("Persona", placeholder="Ej: María, del área de finanzas", label_visibility="collapsed")
            st.markdown("**Tu relación con esa persona:**")
            relacion = st.selectbox("Relación", [
                "Jefe/Superior",
                "Colaborador/Subordinado",
                "Par/Colega",
                "Proveedor externo",
                "Cliente",
                "Otro departamento"
            ], label_visibility="collapsed")

        with col2:
            st.markdown("**Nivel de urgencia:**")
            urgencia = st.selectbox("Urgencia", [
                "Baja - Puede esperar unos días",
                "Media - Necesito respuesta esta semana",
                "Alta - Es urgente, afecta otros procesos",
                "Crítica - Hay consecuencias serias si no se cumple"
            ], label_visibility="collapsed")
            st.markdown("**¿Cuántas veces has hecho seguimiento?**")
            intentos_previos = st.selectbox("Intentos previos", [
                "Ninguna, es el primer recordatorio",
                "1 vez, sin respuesta",
                "2-3 veces, respuestas vagas",
                "Más de 3 veces, sin avance"
            ], label_visibility="collapsed")

        st.markdown("**Describe el compromiso pendiente:**")
        compromiso = st.text_area(
            "Compromiso",
            height=100,
            placeholder="Ej: Enviar el reporte de ventas Q4 que prometió para el viernes pasado...",
            label_visibility="collapsed"
        )

        st.markdown("**¿Qué pasa si no se cumple? (opcional):**")
        consecuencias = st.text_area(
            "Consecuencias",
            height=80,
            placeholder="Ej: No podré cerrar el presupuesto anual / Se retrasa el proyecto...",
            label_visibility="collapsed"
        )

    # Estado
    if 'seguimiento_resultado' not in st.session_state:
        st.session_state.seguimiento_resultado = None
    if 'seguimiento_historial' not in st.session_state:
        st.session_state.seguimiento_historial = []

    # Botón
    if st.button("✨ Generar Mensaje de Seguimiento", type="primary", use_container_width=True):
        if not compromiso or not persona:
            st.warning("⚠️ Describe el compromiso y la persona responsable.")
        else:
            with st.spinner("Generando mensaje asertivo..."):
                st.session_state.seguimiento_resultado = generar_seguimiento(
                    compromiso, persona, relacion, intentos_previos, urgencia, consecuencias
                )
                st.session_state.seguimiento_contexto = {
                    "compromiso": compromiso,
                    "persona": persona,
                    "relacion": relacion
                }

                # Historial
                st.session_state.seguimiento_historial.insert(0, {
                    "persona": persona,
                    "compromiso": compromiso[:50] + "..." if len(compromiso) > 50 else compromiso,
                    "resultado": st.session_state.seguimiento_resultado
                })
                st.session_state.seguimiento_historial = st.session_state.seguimiento_historial[:5]

    # Resultados
    if st.session_state.seguimiento_resultado:
        res = st.session_state.seguimiento_resultado

        if "error" in res:
            st.error(f"Error técnico: {res['error']}")
        else:
            st.markdown("### Opciones de Mensaje")
            st.caption("Puedes editar los textos antes de copiar o descargar")

            version_suave = text_area_with_copy(
                "Suave (Primer recordatorio):",
                res.get('suave', ''),
                key="edit_suave",
                height=150
            )

            version_firme = text_area_with_copy(
                "Firme (Ya hubo intentos previos):",
                res.get('firme', ''),
                key="edit_firme",
                height=150
            )

            version_formal = text_area_with_copy(
                "Formal (Urgente/Consecuencias):",
                res.get('formal', ''),
                key="edit_formal",
                height=150
            )

            res_editado = {
                "suave": version_suave,
                "firme": version_firme,
                "formal": version_formal
            }

            st.divider()

            # Descarga
            st.subheader("📥 Descargar Mensajes")

            col_name, col_type = st.columns([2, 1])
            with col_name:
                ctx = st.session_state.get('seguimiento_contexto', {})
                nombre_archivo = st.text_input(
                    "Nombre del archivo:",
                    value=f"Seguimiento_{ctx.get('persona', 'Compromiso').split()[0]}",
                    help="Sin extensión"
                )
            with col_type:
                tipo_archivo = st.radio("Formato:", ["Word (.docx)", "PDF (.pdf)"], horizontal=True)

            secciones = [
                ("Compromiso", st.session_state.get('seguimiento_contexto', {}).get('compromiso', '')),
                ("1. Versión Suave", res_editado['suave']),
                ("2. Versión Firme", res_editado['firme']),
                ("3. Versión Formal", res_editado['formal'])
            ]

            if tipo_archivo == "Word (.docx)":
                data = create_word_document("Seguimiento de Compromiso", secciones)
                mime = get_word_mime()
                ext = "docx"
            else:
                data = create_pdf_document("Seguimiento de Compromiso", secciones)
                mime = get_pdf_mime()
                ext = "pdf"

            st.download_button(
                label=f"💾 Descargar {tipo_archivo}",
                data=data,
                file_name=f"{nombre_archivo}.{ext}",
                mime=mime,
                use_container_width=True
            )

    # Historial
    st.divider()
    if st.session_state.seguimiento_historial:
        with st.expander("📜 Historial de seguimientos (últimos 5)", expanded=False):
            for i, item in enumerate(st.session_state.seguimiento_historial):
                st.markdown(f"**{i+1}. {item['persona']}:** {item['compromiso']}")
                if st.button(f"Cargar", key=f"cargar_seg_{i}"):
                    st.session_state.seguimiento_resultado = item['resultado']
                    st.rerun()
                st.markdown("---")
