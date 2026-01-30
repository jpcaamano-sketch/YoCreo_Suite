"""
Sistema de autenticación para YoCreo Suite
Verifica suscripciones en Supabase
"""

import streamlit as st
import base64
import os
from .database import verificar_suscripcion, obtener_url_suscripcion


def get_logo_base64():
    """Obtiene el logo en base64"""
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def mostrar_login():
    """Muestra el formulario de acceso"""

    # Centrar contenido
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        logo_b64 = get_logo_base64()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 50px; margin-right: 10px; vertical-align: middle;">' if logo_b64 else ''

        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2D3436; margin-bottom: 5px; display: flex; align-items: center; justify-content: center;">
                    {logo_html}
                    <span>YoCreo IA</span>
                </h1>
                <p style="color: #6c757d;">Suite Liderazgo Consciente</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### Accede a la Plataforma")
            st.markdown("<p style='color: #6c757d; font-size: 14px;'>Ingresa el email con el que te suscribiste</p>", unsafe_allow_html=True)

            email = st.text_input("Email", placeholder="tu@email.com", label_visibility="collapsed")
            submit = st.form_submit_button("Ingresar", use_container_width=True)

            if submit:
                if not email:
                    st.error("Ingresa tu email")
                else:
                    resultado = verificar_suscripcion(email.strip())

                    if resultado['tiene_suscripcion']:
                        st.session_state.user = {
                            'email': email.strip().lower(),
                            'status': resultado['status'],
                            'customer_id': resultado['customer_id']
                        }
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        if resultado['status'] == 'none':
                            st.warning("Este email no tiene una suscripción activa.")
                        elif resultado['status'] == 'canceled':
                            st.warning("Tu suscripción fue cancelada. Renuévala para continuar.")
                        else:
                            st.error(resultado['message'])

        # Link para suscribirse
        landing_url = obtener_url_suscripcion()
        st.markdown(f"""
            <div style="text-align: center; margin-top: 24px;">
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 12px;">¿No tienes suscripción?</p>
                <a href="{landing_url}" target="_blank" style="
                    display: inline-block;
                    background-color: #E67E22;
                    color: white;
                    padding: 12px 24px;
                    border-radius: 10px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 14px;
                ">Suscribirme Ahora</a>
            </div>
        """, unsafe_allow_html=True)


def verificar_autenticacion():
    """
    Verifica si el usuario está autenticado.
    Retorna True si puede acceder, False si no.
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        return False

    return True


def obtener_usuario_actual():
    """Retorna el usuario actual o None"""
    if st.session_state.get('authenticated'):
        return st.session_state.get('user')
    return None


def cerrar_sesion():
    """Cierra la sesión del usuario"""
    st.session_state.authenticated = False
    st.session_state.user = None
    if 'practica_sel' in st.session_state:
        del st.session_state.practica_sel


def mostrar_info_usuario():
    """Muestra información del usuario en el sidebar"""
    user = obtener_usuario_actual()
    if user:
        status_text = "Activa" if user.get('status') == 'active' else "Trial"

        st.markdown(f"""
            <div style="padding: 10px; margin-top: 20px; border-top: 1px solid #4a4a4a;">
                <p style="color: #FFFFFF; font-size: 11px; margin: 0;">{user['email']}</p>
                <p style="color: #95A5A6; font-size: 10px; margin: 0;">Suscripción: {status_text}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Cerrar sesión", key="logout_btn", use_container_width=True):
            cerrar_sesion()
            st.rerun()


def mostrar_suscripcion_expirada():
    """Muestra mensaje cuando no hay suscripción activa"""
    landing_url = obtener_url_suscripcion()

    st.markdown(f"""
        <div style="text-align: center; padding: 40px;">
            <h2>Suscripción requerida</h2>
            <p style="color: #6c757d; margin-bottom: 24px;">Para acceder a YoCreo Suite necesitas una suscripción activa.</p>
            <a href="{landing_url}" target="_blank" style="
                display: inline-block;
                background-color: #E67E22;
                color: white;
                padding: 14px 28px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
            ">Suscribirme Ahora - $10.000/mes</a>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar sesión", use_container_width=True):
        cerrar_sesion()
        st.rerun()
