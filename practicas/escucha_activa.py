"""
Escucha Activa - YoCreo Suite
Gimnasio para practicar escucha activa con roleplay interactivo
"""

import streamlit as st
import json
import re
import random
from core.config import PRACTICAS
from core.ai_client import generate_response
from core.export import text_area_with_copy


def limpiar_json(texto):
    """Limpia la respuesta de la IA para obtener JSON valido."""
    try:
        texto_limpio = texto.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except:
        match = re.search(r'(\{.*\}|\[.*\])', texto, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None


def generar_personaje():
    """Crea un personaje frustrado aleatorio con alta variabilidad."""

    contextos = [
        "un problema urgente en la oficina que nadie resuelve",
        "una discusion familiar por dinero",
        "un reclamo de servicio al cliente por un cobro indebido",
        "un conflicto con vecinos por ruidos molestos",
        "estres por sobrecarga de trabajo y falta de reconocimiento",
        "un error tecnico que borro su trabajo",
        "una decepcion con un amigo cercano",
        "un proyecto que se cancelo sin explicacion",
        "una promesa incumplida por un proveedor"
    ]
    contexto_azar = random.choice(contextos)

    prompt = f"""Genera un caso breve de roleplay para practicar escucha activa.
CONTEXTO OBLIGATORIO: {contexto_azar}.

El personaje debe estar ESTRESADO, TRISTE o PREOCUPADO.
Escribe un monologo (3 a 5 frases) donde mezcle hechos con emociones intensas.
El texto debe ser desordenado y natural, como habla la gente real cuando se desahoga.

Responde SOLO JSON con esta estructura:
{{
    "nombre": "Nombre del personaje",
    "rol": "Ej: Cliente, Hijo, Jefe, Vecino",
    "emocion_dominante": "La emocion principal oculta",
    "texto_monologo": "Lo que dice el personaje..."
}}"""

    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def evaluar_respuesta(caso_original, respuesta_usuario):
    """Evalua si el usuario escucho o si dio consejos (lo cual esta prohibido)."""

    prompt = f"""Actua como Supervisor de Coaching. Evalua la respuesta del usuario ante una queja.

CASO ORIGINAL (Dijo el personaje): "{caso_original}"
RESPUESTA DEL USUARIO (Dijo el coach): "{respuesta_usuario}"

CRITERIOS DE EVALUACION:
1. PROHIBIDO ACONSEJAR: Si el usuario dice "deberias", "tienes que", "por que no pruebas", "yo en tu lugar", califica con 0 en empatia.
2. VALIDACION: El usuario reconocio la emocion explicita o implicita?
3. PARAFRASEO: El usuario resumio los hechos principales sin agregar de su cosecha?

Responde SOLO JSON:
{{
    "consejo_detectado": true/false,
    "puntaje": (Numero del 1 al 10),
    "feedback_positivo": "Breve: Lo que hizo bien...",
    "feedback_mejora": "Breve: Lo que le falto...",
    "ejemplo_ideal": "Escribe un ejemplo de como hubiese sido una respuesta perfecta (Reflective Listening)"
}}"""

    response = generate_response(prompt)
    if response:
        return limpiar_json(response)
    return None


def render():
    """Renderiza la practica Escucha Activa"""
    info = PRACTICAS["escucha_activa"]

    # Header
    st.header(f"{info['icono']} {info['titulo']}")
    st.write(info['descripcion'])

    with st.expander("Regla de Oro de la Escucha Activa"):
        st.warning("""
        **NO des consejos ni soluciones.**
        Solo escucha, valida la emocion y resume lo que entendiste.

        Evita frases como:
        - "Deberias..."
        - "Por que no pruebas..."
        - "Yo en tu lugar..."
        """)

    # Estado de sesion
    if 'escucha_caso_actual' not in st.session_state:
        st.session_state.escucha_caso_actual = None
    if 'escucha_evaluacion' not in st.session_state:
        st.session_state.escucha_evaluacion = None
    if 'escucha_historial' not in st.session_state:
        st.session_state.escucha_historial = []

    # Boton para generar caso
    if st.button("Traer un nuevo interlocutor", type="primary", use_container_width=True):
        with st.spinner("Buscando a alguien que necesita ser escuchado..."):
            st.session_state.escucha_caso_actual = generar_personaje()
            st.session_state.escucha_evaluacion = None

    # Mostrar el caso si existe
    if st.session_state.escucha_caso_actual:
        caso = st.session_state.escucha_caso_actual

        st.markdown(f"### {caso.get('nombre', 'Persona')} ({caso.get('rol', 'Desconocido')}) te dice:")

        # Cuadro de dialogo destacado
        monologo = caso.get('texto_monologo', '')
        st.info(f'"{monologo}"')

        st.write("**Tu mision:** Demuestrale que le entendiste. NO soluciones su problema.")

        # Input del usuario con icono de copiar
        respuesta_user = text_area_with_copy(
            "Tu respuesta (Escribe lo que le dirias):",
            "",
            key="respuesta_escucha",
            height=100
        )

        # Boton evaluar
        if st.button("Evaluar mi Escucha", type="secondary", use_container_width=True):
            if len(respuesta_user) < 5:
                st.warning("Escribe una respuesta mas completa antes de evaluar.")
            else:
                with st.spinner("El Supervisor esta analizando tu empatia..."):
                    evaluacion = evaluar_respuesta(monologo, respuesta_user)
                    st.session_state.escucha_evaluacion = evaluacion

                    # Guardar en historial
                    if evaluacion:
                        st.session_state.escucha_historial.insert(0, {
                            "personaje": caso.get('nombre', 'Persona'),
                            "monologo": monologo[:50] + "...",
                            "respuesta": respuesta_user,
                            "puntaje": evaluacion.get('puntaje', 0)
                        })
                        st.session_state.escucha_historial = st.session_state.escucha_historial[:5]

    # Mostrar resultados de evaluacion
    if st.session_state.escucha_evaluacion:
        ev = st.session_state.escucha_evaluacion

        st.divider()
        st.subheader("Veredicto del Coach")

        score = ev.get('puntaje', 0)

        if ev.get('consejo_detectado'):
            st.error("ALERTA DE SOLUCIONITIS!")
            st.markdown("**Error fatal:** Intentaste arreglar el problema o dar un consejo. En la escucha activa pura, primero debemos validar.")
        elif score >= 8:
            st.balloons()
            st.success(f"Excelente Escucha! Nota: {score}/10")
        elif score >= 5:
            st.warning(f"Escucha aceptable. Nota: {score}/10")
        else:
            st.error(f"No te sintieron presente. Nota: {score}/10")

        # Columnas de Feedback
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Lo bueno:**")
            st.write(ev.get('feedback_positivo', ''))
        with c2:
            st.markdown("**A corregir:**")
            st.write(ev.get('feedback_mejora', ''))

        st.markdown("---")

        # Ejemplo ideal (editable con icono copiar)
        st.markdown("**Respuesta Ideal (Ejemplo):**")
        ejemplo = ev.get('ejemplo_ideal', '')

        ejemplo_editado = text_area_with_copy(
            "Puedes editar y copiar:",
            ejemplo,
            key="ejemplo_ideal_edit",
            height=100
        )

    # Pie de pagina
    if not st.session_state.escucha_caso_actual:
        st.info("Presiona el boton para comenzar el simulacro.")

    # Historial
    st.divider()
    if st.session_state.escucha_historial:
        with st.expander("Historial de practicas (ultimas 5)", expanded=False):
            for i, item in enumerate(st.session_state.escucha_historial):
                st.markdown(f"**{i+1}. {item['personaje']}** - Puntaje: {item['puntaje']}/10")
                st.caption(f"Caso: {item['monologo']}")
                st.markdown("---")
