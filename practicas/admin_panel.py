"""
Panel de Administración para Plan Empresa
Gestiona miembros en suite_usuarios y sincroniza seats con Stripe.

-- SQL para crear la tabla de auditoría (ejecutar en Supabase SQL Editor):
CREATE TABLE IF NOT EXISTS suite_audit_log (
    id         BIGSERIAL   PRIMARY KEY,
    admin_email TEXT        NOT NULL,
    accion     TEXT        NOT NULL,
    target_email TEXT,
    detalles   JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_admin ON suite_audit_log (admin_email);
"""

import logging
import base64
import streamlit as st
import pandas as pd
import re
from core.database import get_supabase, get_empresa_config, save_empresa_logo
from core.stripe_client import actualizar_seats_empresa

logger = logging.getLogger(__name__)


def registrar_auditoria(admin_email: str, accion: str, target_email: str = None, detalles: dict = None):
    """Inserta un registro en suite_audit_log. Falla silenciosamente si la tabla no existe."""
    try:
        supabase = get_supabase()
        supabase.table('suite_audit_log').insert({
            'admin_email':   admin_email,
            'accion':        accion,
            'target_email':  target_email,
            'detalles':      detalles or {},
        }).execute()
    except Exception as e:
        logger.warning("No se pudo registrar auditoría: %s", e)


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _sync_stripe_seats(organization_id: str, miembros_activos: int) -> None:
    """Sincroniza la cantidad de seats en Stripe (admin + miembros = total)."""
    if not organization_id:
        return
    total = miembros_activos + 1  # +1 por el admin
    ok = actualizar_seats_empresa(organization_id, total)
    if ok:
        logger.info("Stripe seats actualizados a %d para org %s", total, organization_id)


def render():
    """Renderiza el Panel de Administración."""

    user_role = st.session_state.get('user_role', {})

    # Verificar acceso
    if user_role.get('tipo') != 'empresa_admin':
        st.error("Acceso denegado. Solo los administradores pueden acceder a este panel.")
        return

    admin_user      = st.session_state.get('user', {})
    admin_email     = admin_user.get('email', '')
    organization_id = admin_user.get('organization_id', '')
    empresa         = user_role.get('organization_name', '')

    if not empresa:
        st.error("No se encontró la empresa del administrador.")
        return

    supabase = get_supabase()

    # Obtener miembros activos de la empresa (excluye al propio admin)
    try:
        members_response = (
            supabase.table('suite_usuarios')
            .select('id, nombre, email, rol, plan, activo')
            .eq('empresa', empresa)
            .neq('email', admin_email)
            .eq('activo', True)
            .order('nombre')
            .execute()
        )
        members = members_response.data if members_response.data else []
    except Exception as e:
        st.error(f"Error obteniendo miembros: {e}")
        members = []

    miembros_activos = len(members)

    # ==================== TÍTULO ====================
    st.markdown("## Panel de Administración")

    # ==================== CAJA 1: INFO EMPRESA ====================
    with st.container(border=True):
        st.markdown("**Empresa**")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nombre Empresa", value=empresa, disabled=True, key="admin_empresa_nombre")
        with col2:
            st.text_input("Suscritos activos", value=str(miembros_activos), disabled=True, key="admin_miembros_activos")

    # ==================== CAJA 2: MIEMBROS ====================
    with st.container(border=True):
        st.markdown("**Miembros del Equipo**")

        if not members:
            st.info("No hay miembros en la empresa todavía.")
        else:
            df_data = []
            member_ids = []

            for member in members:
                df_data.append({
                    "Nombre": member.get('nombre', '') or '—',
                    "Correo": member.get('email', ''),
                    "Eliminar": False
                })
                member_ids.append(member.get('id'))

            df = pd.DataFrame(df_data)

            edited_df = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                disabled=["Nombre", "Correo"],
                column_config={
                    "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
                    "Correo": st.column_config.TextColumn("Correo", width="large"),
                    "Eliminar": st.column_config.CheckboxColumn("Eliminar", width="small", default=False),
                },
                key="admin_members_table"
            )

            if st.button("Eliminar seleccionados", type="secondary"):
                indices_eliminar = edited_df[edited_df["Eliminar"] == True].index.tolist()

                if not indices_eliminar:
                    st.warning("No hay miembros seleccionados para eliminar.")
                else:
                    eliminados = 0
                    for idx in indices_eliminar:
                        try:
                            email_eliminado = members[idx].get('email', '')
                            supabase.table('suite_usuarios').update(
                                {'activo': False}
                            ).eq('id', member_ids[idx]).execute()
                            registrar_auditoria(
                                admin_email=admin_email,
                                accion='eliminar_miembro',
                                target_email=email_eliminado,
                                detalles={'empresa': empresa},
                            )
                            eliminados += 1
                        except Exception as e:
                            st.error(f"Error eliminando miembro: {e}")

                    if eliminados > 0:
                        st.success(f"{eliminados} miembro(s) eliminado(s). Han perdido acceso a la plataforma.")
                        nuevos_activos = miembros_activos - eliminados
                        _sync_stripe_seats(organization_id, nuevos_activos)
                        st.rerun()

    # ==================== CAJA 3: AGREGAR NUEVO MIEMBRO ====================
    with st.container(border=True):
        st.markdown("**Agregar Nuevo Miembro**")

        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Nombre", placeholder="Ej: María González", key="admin_new_name")
        with col2:
            new_email = st.text_input("Correo electrónico", placeholder="Ej: maria@empresa.com", key="admin_new_email")

        if st.button("Agregar Miembro", use_container_width=True, type="primary"):
            if not new_name or not new_name.strip():
                st.error("El nombre es obligatorio.")
            elif not new_email or not new_email.strip():
                st.error("El correo es obligatorio.")
            elif not validar_email(new_email.strip()):
                st.error("Formato de correo inválido.")
            else:
                new_email_clean = new_email.strip().lower()
                new_name_clean = new_name.strip()

                # Verificar si ya existe en la empresa
                ya_existe = [m for m in members if m.get('email', '').lower() == new_email_clean]
                if ya_existe:
                    st.error("Este correo ya es miembro de la empresa.")
                else:
                    try:
                        supabase.table('suite_usuarios').insert({
                            'nombre': new_name_clean,
                            'email': new_email_clean,
                            'rol': 'suscrito',
                            'plan': 'empresa',
                            'empresa': empresa,
                            'activo': True
                        }).execute()
                        registrar_auditoria(
                            admin_email=admin_email,
                            accion='agregar_miembro',
                            target_email=new_email_clean,
                            detalles={'nombre': new_name_clean, 'empresa': empresa},
                        )
                        _sync_stripe_seats(organization_id, miembros_activos + 1)
                        st.success(f"Miembro {new_email_clean} agregado. La suscripción Stripe se actualizó automáticamente.")
                        st.rerun()
                    except Exception as e:
                        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                            st.error("Este correo ya existe en el sistema.")
                        else:
                            st.error(f"Error al agregar miembro: {e}")

    # ==================== CAJA 4: MARCA BLANCA — LOGO EMPRESA ====================
    with st.container(border=True):
        st.markdown("**Logo para PDFs (Marca Blanca)**")

        config_actual = get_empresa_config(empresa)
        logo_actual_b64 = (config_actual or {}).get('logo_b64')

        col_logo, col_upload = st.columns([1, 2])
        with col_logo:
            if logo_actual_b64:
                try:
                    st.markdown("**Logo actual:**")
                    st.image(base64.b64decode(logo_actual_b64), width=140)
                except Exception:
                    st.caption("(logo guardado, no se puede previsualizar)")
            else:
                st.caption("Sin logo configurado")

        with col_upload:
            uploaded = st.file_uploader(
                "Cargar nuevo logo (PNG/JPG, máx 250 KB)",
                type=["png", "jpg", "jpeg"],
                key="admin_logo_upload"
            )
            if uploaded:
                if uploaded.size > 250 * 1024:
                    st.error("El archivo supera los 250 KB. Usa una imagen más pequeña.")
                else:
                    nuevo_b64 = base64.b64encode(uploaded.read()).decode()
                    if st.button("Guardar logo", key="admin_logo_save"):
                        if save_empresa_logo(empresa, nuevo_b64):
                            st.session_state.empresa_logo = nuevo_b64
                            st.success("Logo guardado. Aparecerá en los próximos PDFs generados.")
                            st.rerun()
                        else:
                            st.error("No se pudo guardar el logo. Verifica que la tabla suite_empresa_config exista en Supabase.")

        if logo_actual_b64:
            if st.button("Eliminar logo", key="admin_logo_delete", type="secondary"):
                if save_empresa_logo(empresa, ""):
                    st.session_state.empresa_logo = None
                    st.success("Logo eliminado.")
                    st.rerun()

    # ==================== CAJA 5: DASHBOARD DE USO ====================
    with st.expander("Dashboard de Uso del Equipo"):
        try:
            eventos_response = (
                supabase.table('practice_events')
                .select('practica, email, created_at')
                .order('created_at', desc=True)
                .limit(500)
                .execute()
            )
            eventos = eventos_response.data if eventos_response.data else []

            # Filtrar sólo emails de la empresa
            emails_empresa = {m.get('email', '').lower() for m in members}
            emails_empresa.add(admin_email.lower())
            eventos_empresa = [e for e in eventos if e.get('email', '').lower() in emails_empresa]

            if not eventos_empresa:
                st.info("Sin actividad registrada todavía para el equipo.")
            else:
                # Conteo por práctica
                from collections import Counter
                conteo = Counter(e['practica'] for e in eventos_empresa)
                df_uso = pd.DataFrame([
                    {"Práctica": k, "Generaciones": v}
                    for k, v in sorted(conteo.items(), key=lambda x: -x[1])
                ])
                st.markdown("**Generaciones por práctica (todo el equipo)**")
                st.dataframe(df_uso, use_container_width=True, hide_index=True)

                # Conteo por usuario
                conteo_user = Counter(e['email'] for e in eventos_empresa)
                df_user = pd.DataFrame([
                    {"Usuario": k, "Generaciones": v}
                    for k, v in sorted(conteo_user.items(), key=lambda x: -x[1])
                ])
                st.markdown("**Generaciones por usuario**")
                st.dataframe(df_user, use_container_width=True, hide_index=True)
        except Exception as e:
            st.info(f"Dashboard no disponible: {e}")

    # ==================== CAJA 6: LOG DE AUDITORÍA ====================
    with st.expander("Registro de Auditoría"):
        try:
            log_response = (
                supabase.table('suite_audit_log')
                .select('created_at, accion, target_email, admin_email')
                .eq('admin_email', admin_email)
                .order('created_at', desc=True)
                .limit(50)
                .execute()
            )
            log_data = log_response.data if log_response.data else []
            if not log_data:
                st.info("Sin actividad registrada todavía.")
            else:
                df_log = pd.DataFrame([{
                    "Fecha":   item['created_at'][:19].replace('T', ' '),
                    "Acción":  item['accion'],
                    "Correo afectado": item.get('target_email', '—'),
                } for item in log_data])
                st.dataframe(df_log, use_container_width=True, hide_index=True)
        except Exception:
            st.info("El registro de auditoría no está disponible. Ejecuta el SQL del encabezado de este archivo en Supabase.")
