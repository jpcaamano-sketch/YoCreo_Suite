"""
Panel de Administración para Plan Empresa
Gestiona miembros directamente en suite_usuarios (sin Stripe)
"""

import streamlit as st
import pandas as pd
import re
from core.database import get_supabase

BILLING_ENABLED = False


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def render():
    """Renderiza el Panel de Administración."""

    user_role = st.session_state.get('user_role', {})

    # Verificar acceso
    if user_role.get('tipo') != 'empresa_admin':
        st.error("Acceso denegado. Solo los administradores pueden acceder a este panel.")
        return

    admin_email = st.session_state.get('user', {}).get('email', '')
    empresa = user_role.get('organization_name', '')

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
                            supabase.table('suite_usuarios').update(
                                {'activo': False}
                            ).eq('id', member_ids[idx]).execute()
                            eliminados += 1
                        except Exception as e:
                            st.error(f"Error eliminando miembro: {e}")

                    if eliminados > 0:
                        st.success(f"{eliminados} miembro(s) eliminado(s). Han perdido acceso a la plataforma.")
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
                        st.success(f"Miembro {new_email_clean} agregado exitosamente.")
                        st.rerun()
                    except Exception as e:
                        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                            st.error("Este correo ya existe en el sistema.")
                        else:
                            st.error(f"Error al agregar miembro: {e}")
