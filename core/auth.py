"""
Sistema de autenticación para YoCreo Suite
Verificación en dos pasos: email → código OTP enviado por Resend
"""

import logging
import random
import time
import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from .database import verificar_suscripcion, obtener_url_suscripcion, obtener_datos_usuario, get_empresa_config
from .session_token import generar_token, validar_token

logger = logging.getLogger(__name__)

OTP_TTL_SECS = 600   # 10 minutos


def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def obtener_rol_usuario(email: str) -> dict:
    try:
        usuario = obtener_datos_usuario(email)
        if not usuario:
            return {'tipo': None, 'organization_id': None, 'organization_name': None}
        if usuario.get('rol') == 'administrador':
            return {'tipo': 'empresa_admin',   'organization_id': None, 'organization_name': usuario.get('empresa') or 'YoCreo'}
        elif usuario.get('plan') == 'empresa':
            return {'tipo': 'empresa_member',  'organization_id': None, 'organization_name': usuario.get('empresa')}
        else:
            return {'tipo': 'individual',      'organization_id': None, 'organization_name': None}
    except Exception as e:
        logger.warning("Error obteniendo rol: %s", e)
        return {'tipo': None, 'organization_id': None, 'organization_name': None}


def _set_session(email: str) -> bool:
    """Carga datos del usuario desde DB y establece la sesión. Retorna True si tuvo acceso."""
    resultado   = verificar_suscripcion(email)
    rol_usuario = obtener_rol_usuario(email)
    if not (resultado['tiene_suscripcion'] or rol_usuario['tipo'] is not None):
        return False
    datos = obtener_datos_usuario(email)
    st.session_state.user = {
        'email':               email,
        'status':              resultado['status'] if resultado['tiene_suscripcion'] else 'active',
        'customer_id':         resultado['customer_id'],
        'nombre':              (datos or {}).get('nombre', ''),
        'stripe_customer_id':  (datos or {}).get('stripe_customer_id', ''),
        'organization_id':     (datos or {}).get('organization_id', ''),
    }
    st.session_state.user_role     = rol_usuario
    st.session_state.authenticated = True

    # Cargar logo de empresa en sesión (para marca blanca en PDFs)
    org_name = rol_usuario.get('organization_name')
    if rol_usuario.get('tipo') in ('empresa_admin', 'empresa_member') and org_name:
        try:
            config = get_empresa_config(org_name)
            st.session_state.empresa_logo = (config or {}).get('logo_b64')
        except Exception:
            st.session_state.empresa_logo = None
    else:
        st.session_state.empresa_logo = None

    return True


def _restaurar_sesion_si_aplica():
    """Lee el token _st del query param (puesto por el JS de localStorage) y restaura la sesión."""
    if st.session_state.get('authenticated'):
        return
    token = st.query_params.get("_st", "")
    if not token:
        return
    email = validar_token(token)
    if email and _set_session(email):
        # Limpiar _st de la URL sin recargar
        components.html("""<script>
            var u = new URL(window.parent.location.href);
            u.searchParams.delete('_st');
            window.parent.history.replaceState({}, '', u.toString());
        </script>""", height=0)
    else:
        # Token inválido o usuario sin acceso — borrar localStorage
        components.html("""<script>
            window.parent.localStorage.removeItem('yocreo_session');
            var u = new URL(window.parent.location.href);
            u.searchParams.delete('_st');
            window.parent.history.replaceState({}, '', u.toString());
        </script>""", height=0)


def _generar_codigo() -> str:
    return str(random.randint(100000, 999999))


def _enviar_otp(email: str, codigo: str) -> bool:
    """Envía el código OTP vía Resend. Retorna True si tuvo éxito."""
    try:
        import resend
        resend.api_key = st.secrets.get("RESEND_API_KEY", "")
        if not resend.api_key:
            logger.error("RESEND_API_KEY no configurada en secrets.toml")
            return False

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;">
          <h2 style="color:#4E32AD;margin-bottom:8px;">YoCreo Suite</h2>
          <p style="color:#555;margin-bottom:24px;">Tu código de acceso:</p>
          <div style="background:#f4f1ff;border-radius:12px;padding:24px;text-align:center;margin-bottom:24px;">
            <span style="font-size:36px;font-weight:800;letter-spacing:10px;color:#4E32AD;">{codigo}</span>
          </div>
          <p style="color:#888;font-size:13px;">Expira en 10 minutos.<br>Si no lo solicitaste, ignora este correo.</p>
        </div>"""

        resend.Emails.send({
            "from":    "YoCreo Suite <noreply@escuelayocreo.cl>",
            "to":      [email],
            "subject": f"YoCreo Suite — Código de acceso: {codigo}",
            "html":    html_body,
        })
        return True
    except Exception as e:
        logger.error("Error enviando OTP a %s: %s", email, e)
        return False


def _enviar_bienvenida(email: str, nombre: str) -> None:
    """Envía email de bienvenida al primer login vía Resend. Falla silenciosamente."""
    try:
        import resend
        resend.api_key = st.secrets.get("RESEND_API_KEY", "")
        if not resend.api_key:
            return

        landing_url    = st.secrets.get("LANDING_URL", "https://yocreo-landing.vercel.app")
        nombre_display = nombre.split()[0].capitalize() if nombre else "Líder"

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:580px;margin:0 auto;padding:32px;">
          <h2 style="color:#4E32AD;margin-bottom:4px;">YoCreo Suite</h2>
          <p style="color:#888;font-size:13px;margin-top:0;">Suite Liderazgo Consciente</p>
          <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
          <p style="font-size:16px;color:#333;">Hola <strong>{nombre_display}</strong>,</p>
          <p style="color:#555;font-size:15px;line-height:1.6;">
            Tu acceso a <strong style="color:#4E32AD;">YoCreo Suite</strong> está activo.
            Tienes disponibles <strong>14 prácticas de liderazgo</strong> organizadas en 4 categorías:
          </p>
          <table style="width:100%;border-collapse:collapse;margin:20px 0;">
            <tr>
              <td style="padding:10px 14px;background:#f7f4ff;border-radius:8px;width:50%;">
                <strong style="color:#4E32AD;">1. Autogestión y Foco</strong><br>
                <span style="color:#777;font-size:13px;">Priorizar, presentar, enfocar</span>
              </td>
              <td style="padding:10px 14px;background:#fff8f4;border-radius:8px;width:50%;">
                <strong style="color:#E67E22;">2. Coordinación Impecable</strong><br>
                <span style="color:#777;font-size:13px;">Delegar, pedir, comprometerse</span>
              </td>
            </tr>
            <tr><td colspan="2" style="height:8px;"></td></tr>
            <tr>
              <td style="padding:10px 14px;background:#f4fff7;border-radius:8px;">
                <strong style="color:#27AE60;">3. Desarrollo de Otros</strong><br>
                <span style="color:#777;font-size:13px;">Escuchar, preguntar, evaluar</span>
              </td>
              <td style="padding:10px 14px;background:#f0f8ff;border-radius:8px;">
                <strong style="color:#2980B9;">4. Estrategia y Relaciones</strong><br>
                <span style="color:#777;font-size:13px;">Objetivos, negociar, reparar</span>
              </td>
            </tr>
          </table>
          <div style="text-align:center;margin:30px 0;">
            <a href="{landing_url}" style="background:#FF6B4E;color:#fff;padding:14px 32px;
              border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;">
              Ir a la plataforma →
            </a>
          </div>
          <p style="color:#aaa;font-size:12px;text-align:center;">
            Si no solicitaste este acceso, ignora este correo.
          </p>
        </div>"""

        resend.Emails.send({
            "from":    "YoCreo Suite <noreply@escuelayocreo.cl>",
            "to":      [email],
            "subject": "Bienvenido a YoCreo Suite — Tu plataforma está activa",
            "html":    html_body,
        })
    except Exception as e:
        logger.warning("No se pudo enviar email de bienvenida a %s: %s", email, e)


def _header_html():
    logo_b64  = get_logo_base64()
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        f'style="height:50px;margin-right:10px;vertical-align:middle;">'
        if logo_b64 else ''
    )
    st.markdown(f"""
        <div style="text-align:center;margin-bottom:30px;">
          <h1 style="color:#2D3436;margin-bottom:5px;display:flex;align-items:center;justify-content:center;">
            {logo_html}<span>YoCreo IA</span>
          </h1>
          <p style="color:#6c757d;">Suite Liderazgo Consciente</p>
        </div>
    """, unsafe_allow_html=True)


def mostrar_login():
    """Formulario en 2 pasos: email → código OTP enviado por Gmail."""

    # Si no hay _st en la URL, revisar localStorage y redirigir con token si existe
    if not st.query_params.get("_st"):
        components.html("""<script>
            var t = window.parent.localStorage.getItem('yocreo_session');
            if (t) {
                var u = new URL(window.parent.location.href);
                u.searchParams.set('_st', t);
                window.parent.location.href = u.toString();
            }
        </script>""", height=0)

    if 'login_step'      not in st.session_state: st.session_state.login_step      = 'email'
    if 'login_email_tmp' not in st.session_state: st.session_state.login_email_tmp = None
    if 'login_otp_code'  not in st.session_state: st.session_state.login_otp_code  = None
    if 'login_otp_ts'    not in st.session_state: st.session_state.login_otp_ts    = 0

    _header_html()

    # ── PASO 1: ingresar email ─────────────────────────────────────────────
    if st.session_state.login_step == 'email':
        with st.form("login_email_form"):
            st.markdown("### Accede a la Plataforma")
            st.markdown(
                "<p style='color:#6c757d;font-size:14px;'>"
                "Ingresa tu email para recibir un código de verificación</p>",
                unsafe_allow_html=True,
            )
            email  = st.text_input("Email", placeholder="tu@email.com", label_visibility="collapsed")
            tos    = st.checkbox(
                "Acepto los [Términos de Servicio](https://yocreo-landing.vercel.app/terminos) "
                "y la [Política de Privacidad](https://yocreo-landing.vercel.app/privacidad)",
            )
            submit = st.form_submit_button("Enviar Código →", use_container_width=True)

        if submit:
            if not email or "@" not in email:
                st.error("Ingresa un email válido.")
                return
            if not tos:
                st.error("Debes aceptar los Términos de Servicio para continuar.")
                return
            email_clean = email.strip().lower()

            resultado   = verificar_suscripcion(email_clean)
            rol_usuario = obtener_rol_usuario(email_clean)

            if not (resultado['tiene_suscripcion'] or rol_usuario['tipo'] is not None):
                st.warning("Este email no tiene una suscripción activa.")
                return

            codigo = _generar_codigo()
            with st.spinner("Enviando código a tu correo..."):
                ok = _enviar_otp(email_clean, codigo)

            if ok:
                st.session_state.login_email_tmp = email_clean
                st.session_state.login_otp_code  = codigo
                st.session_state.login_otp_ts    = time.time()
                st.session_state.login_step      = 'otp'
                st.rerun()
            else:
                st.error("No se pudo enviar el código. Revisa la configuración SMTP o intenta de nuevo.")

        landing_url = obtener_url_suscripcion()
        st.markdown(f"""
            <div style="text-align:center;margin-top:24px;">
              <p style="color:#6c757d;font-size:14px;margin-bottom:12px;">¿No tienes suscripción?</p>
              <a href="{landing_url}" target="_blank" style="
                display:inline-block;background:#E67E22;color:white;
                padding:12px 24px;border-radius:10px;text-decoration:none;
                font-weight:600;font-size:14px;">Suscribirme Ahora</a>
            </div>
        """, unsafe_allow_html=True)

    # ── PASO 2: ingresar código ────────────────────────────────────────────
    elif st.session_state.login_step == 'otp':
        email_tmp = st.session_state.login_email_tmp
        st.info(f"📧 Enviamos un código de 6 dígitos a **{email_tmp}**. Revisa tu bandeja de entrada.")

        with st.form("login_otp_form"):
            st.markdown("### Ingresa el código")
            otp    = st.text_input("Código de verificación", placeholder="123456", max_chars=6, label_visibility="collapsed")
            col1, col2 = st.columns(2)
            with col1:
                verificar = st.form_submit_button("Verificar →", use_container_width=True)
            with col2:
                volver = st.form_submit_button("← Cambiar email", use_container_width=True)

        if volver:
            for k in ('login_step', 'login_email_tmp', 'login_otp_code', 'login_otp_ts'):
                st.session_state.pop(k, None)
            st.rerun()

        if verificar:
            if not otp or not otp.strip().isdigit() or len(otp.strip()) != 6:
                st.error("El código debe tener exactamente 6 dígitos.")
                return

            # Verificar expiración
            elapsed = time.time() - st.session_state.get('login_otp_ts', 0)
            if elapsed > OTP_TTL_SECS:
                st.error("El código expiró. Vuelve al paso anterior y solicita uno nuevo.")
                st.session_state.login_step = 'email'
                return

            if otp.strip() == st.session_state.login_otp_code:
                # Código correcto → establecer sesión y guardar token en localStorage
                es_nuevo = False
                try:
                    from .historial import obtener_historial
                    es_nuevo = not obtener_historial(email_tmp, limit=1)
                except Exception:
                    pass
                _set_session(email_tmp)
                if es_nuevo:
                    nombre = st.session_state.get('user', {}).get('nombre', '')
                    _enviar_bienvenida(email_tmp, nombre)
                _token = generar_token(email_tmp)
                components.html(f"""<script>
                    window.parent.localStorage.setItem('yocreo_session', '{_token}');
                </script>""", height=0)
                # Limpiar estado de login
                for k in ('login_step', 'login_email_tmp', 'login_otp_code', 'login_otp_ts'):
                    st.session_state.pop(k, None)
                st.rerun()
            else:
                st.error("Código incorrecto. Intenta de nuevo o vuelve al paso anterior.")

        # Reenviar código
        st.markdown("<div style='text-align:center;margin-top:12px;'>", unsafe_allow_html=True)
        if st.button("Reenviar código", use_container_width=False):
            nuevo_codigo = _generar_codigo()
            with st.spinner("Reenviando..."):
                ok = _enviar_otp(email_tmp, nuevo_codigo)
            if ok:
                st.session_state.login_otp_code = nuevo_codigo
                st.session_state.login_otp_ts   = time.time()
                st.success("Código reenviado. Revisa tu correo.")
            else:
                st.error("No se pudo reenviar. Intenta de nuevo.")
        st.markdown("</div>", unsafe_allow_html=True)


def verificar_autenticacion():
    _restaurar_sesion_si_aplica()
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        return False
    if 'user_role' not in st.session_state:
        user = st.session_state.get('user')
        if user:
            st.session_state.user_role = obtener_rol_usuario(user['email'])
    return True


def obtener_usuario_actual():
    if st.session_state.get('authenticated'):
        return st.session_state.get('user')
    return None


def cerrar_sesion():
    components.html("""<script>
        window.parent.localStorage.removeItem('yocreo_session');
    </script>""", height=0)
    for key in ('authenticated', 'user', 'user_role', 'practica_sel',
                'login_step', 'login_email_tmp', 'login_otp_code', 'login_otp_ts'):
        st.session_state.pop(key, None)


def mostrar_info_usuario():
    user = obtener_usuario_actual()
    if not user:
        return
    status_text        = "Activa" if user.get('status') == 'active' else "Trial"
    user_role          = st.session_state.get('user_role', {})
    org_name           = user_role.get('organization_name')
    role_type          = user_role.get('tipo')
    stripe_customer_id = user.get('stripe_customer_id', '')

    role_badge = ""
    if role_type == 'empresa_admin':
        role_badge = f"<p style='color:#9B59B6;font-size:10px;margin:0;'>Admin: {org_name}</p>"
    elif role_type == 'empresa_member':
        role_badge = f"<p style='color:#3498DB;font-size:10px;margin:0;'>{org_name}</p>"

    st.markdown(f"""
        <div style="padding:10px;margin-top:20px;border-top:1px solid #4a4a4a;">
          <p style="color:#FFFFFF;font-size:11px;margin:0;">{user['email']}</p>
          <p style="color:#95A5A6;font-size:10px;margin:0;">Suscripción: {status_text}</p>
          {role_badge}
        </div>
    """, unsafe_allow_html=True)

    # Botón "Gestionar suscripción" vía Stripe Customer Portal
    if stripe_customer_id:
        if st.button("Gestionar suscripción", key="portal_btn", use_container_width=True):
            from .stripe_client import crear_portal_session
            landing_url = st.secrets.get("LANDING_URL", "https://yocreo-landing.vercel.app")
            portal_url  = crear_portal_session(stripe_customer_id, return_url=landing_url)
            if portal_url:
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={portal_url}">',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p style="color:#95A5A6;font-size:11px;text-align:center;">'
                    f'<a href="{portal_url}" target="_blank" style="color:#E67E22;">Abrir portal →</a></p>',
                    unsafe_allow_html=True,
                )
            else:
                st.warning("No se pudo abrir el portal. Verifica STRIPE_SECRET_KEY.")

    if st.button("Cerrar sesión", key="logout_btn", use_container_width=True):
        cerrar_sesion()
        st.rerun()


def mostrar_suscripcion_expirada():
    landing_url = obtener_url_suscripcion()
    st.markdown(f"""
        <div style="text-align:center;padding:40px;">
          <h2>Suscripción requerida</h2>
          <p style="color:#6c757d;margin-bottom:24px;">Para acceder a YoCreo Suite necesitas una suscripción activa.</p>
          <a href="{landing_url}" target="_blank" style="
            display:inline-block;background:#E67E22;color:white;
            padding:14px 28px;border-radius:10px;text-decoration:none;
            font-weight:600;font-size:16px;">Suscribirme Ahora — $10.000/mes</a>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Cerrar sesión", use_container_width=True):
        cerrar_sesion()
        st.rerun()
