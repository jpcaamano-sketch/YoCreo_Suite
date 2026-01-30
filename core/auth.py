"""
Sistema de autenticación para YoCreo Suite
Verifica suscripciones en Supabase
"""

import streamlit as st
import base64
import os
from .database import verificar_suscripcion, obtener_url_suscripcion, get_supabase


def get_logo_base64():
    """Obtiene el logo en base64"""
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def obtener_rol_usuario(email: str) -> dict:
    """
    Retorna información del usuario y su rol.
    Returns: {
        'tipo': 'individual' | 'empresa_admin' | 'empresa_member' | None,
        'organization_id': UUID | None,
        'organization_name': str | None
    }
    """
    try:
        supabase = get_supabase()
        email_lower = email.lower()
        print(f"[DEBUG] Verificando rol para email: {email_lower}")

        # Verificar si es suscriptor individual
        individual = supabase.table('subscriptions').select('*').eq('email', email_lower).eq('status', 'active').execute()
        print(f"[DEBUG] Subscriptions result: {individual.data}")
        if individual.data:
            return {
                'tipo': 'individual',
                'organization_id': None,
                'organization_name': None
            }

        # Verificar si es miembro de organización activa
        member = supabase.table('organization_members').select(
            '*, organizations(*)'
        ).eq('email', email_lower).eq('status', 'active').execute()
        print(f"[DEBUG] Organization members result: {member.data}")

        if member.data:
            member_data = member.data[0]
            org = member_data.get('organizations', {})
            print(f"[DEBUG] Org data: {org}")
            print(f"[DEBUG] Role: {member_data.get('role')}")

            # Verificar que la organización esté activa
            if org and org.get('status') == 'active':
                role = member_data.get('role', 'member')
                result = {
                    'tipo': 'empresa_admin' if role == 'admin' else 'empresa_member',
                    'organization_id': org.get('id'),
                    'organization_name': org.get('name')
                }
                print(f"[DEBUG] Returning: {result}")
                return result

        print("[DEBUG] No membership found, returning None")
        return {
            'tipo': None,
            'organization_id': None,
            'organization_name': None
        }

    except Exception as e:
        print(f"Error obteniendo rol de usuario: {e}")
        return {
            'tipo': None,
            'organization_id': None,
            'organization_name': None
        }


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
                    email_clean = email.strip().lower()

                    # Primero verificar suscripción individual
                    resultado = verificar_suscripcion(email_clean)

                    # También verificar si es miembro de organización
                    rol_usuario = obtener_rol_usuario(email_clean)

                    if resultado['tiene_suscripcion'] or rol_usuario['tipo'] is not None:
                        st.session_state.user = {
                            'email': email_clean,
                            'status': resultado['status'] if resultado['tiene_suscripcion'] else 'active',
                            'customer_id': resultado['customer_id']
                        }
                        st.session_state.user_role = rol_usuario
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

    # Verificar que tenga rol asignado
    if 'user_role' not in st.session_state:
        user = st.session_state.get('user')
        if user:
            st.session_state.user_role = obtener_rol_usuario(user['email'])

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
    st.session_state.user_role = None
    if 'practica_sel' in st.session_state:
        del st.session_state.practica_sel


def mostrar_info_usuario():
    """Muestra información del usuario en el sidebar"""
    user = obtener_usuario_actual()
    if user:
        status_text = "Activa" if user.get('status') == 'active' else "Trial"

        # Mostrar información de organización si aplica
        user_role = st.session_state.get('user_role', {})
        org_name = user_role.get('organization_name')
        role_type = user_role.get('tipo')

        role_badge = ""
        if role_type == 'empresa_admin':
            role_badge = f"<p style='color: #9B59B6; font-size: 10px; margin: 0;'>Admin: {org_name}</p>"
        elif role_type == 'empresa_member':
            role_badge = f"<p style='color: #3498DB; font-size: 10px; margin: 0;'>{org_name}</p>"

        st.markdown(f"""
            <div style="padding: 10px; margin-top: 20px; border-top: 1px solid #4a4a4a;">
                <p style="color: #FFFFFF; font-size: 11px; margin: 0;">{user['email']}</p>
                <p style="color: #95A5A6; font-size: 10px; margin: 0;">Suscripción: {status_text}</p>
                {role_badge}
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
