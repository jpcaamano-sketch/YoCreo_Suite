"""
Panel de Administración para Plan Empresa
Permite gestionar miembros de la organización
"""

import streamlit as st
import pandas as pd
from core.database import get_supabase
import re


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

    org_id = user_role.get('organization_id')
    org_name = user_role.get('organization_name', 'Mi Empresa')

    if not org_id:
        st.error("No se encontró la organización.")
        return

    supabase = get_supabase()

    # Obtener información de la organización
    try:
        org_response = supabase.table('organizations').select('*').eq('id', org_id).single().execute()
        org_data = org_response.data if org_response.data else {}
        max_members = org_data.get('max_members', 10)
    except Exception as e:
        st.error(f"Error obteniendo información de organización: {e}")
        max_members = 10
        org_data = {}

    # Obtener miembros actuales
    try:
        members_response = supabase.table('organization_members').select('*').eq('organization_id', org_id).eq('status', 'active').order('added_at').execute()
        members = members_response.data if members_response.data else []
    except Exception as e:
        st.error(f"Error obteniendo miembros: {e}")
        members = []

    # Calcular estadísticas
    miembros_activos = len(members)
    disponibles = max_members - miembros_activos

    # ==================== TÍTULO PÁGINA ====================
    st.markdown("## Panel de Administración")

    # ==================== CAJA 1: DESCRIPCIÓN ====================
    with st.container(border=True):
        st.markdown("**Gestiona los miembros de tu organización.**")

        with st.expander("Ayuda: Gestión de Miembros"):
            st.write("""
            Desde este panel puedes administrar los miembros de tu organización:

            - **Agregar miembros:** Ingresa nombre y correo para dar acceso a la plataforma.
            - **Eliminar miembros:** Marca la casilla y presiona eliminar. Perderán acceso inmediatamente.
            - **Límite:** Tu plan permite hasta 10 miembros activos.
            """)

    # ==================== CAJA 2: EMPRESA ====================
    with st.container(border=True):
        st.markdown("**Empresa**")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.text_input("Nombre Empresa", value=org_name, disabled=True, key="admin_empresa_nombre")

        with col2:
            st.text_input("Miembros Activos", value=str(miembros_activos), disabled=True, key="admin_miembros_activos")

        with col3:
            st.text_input("Límite", value=str(max_members), disabled=True, key="admin_limite")

        with col4:
            st.text_input("Disponibles", value=str(disponibles), disabled=True, key="admin_disponibles")

        with st.expander("Más información"):
            st.markdown(f"""
            - **ID Organización:** `{org_id}`
            - **Estado:** {org_data.get('status', 'N/A')}
            - **Fecha creación:** {org_data.get('created_at', 'N/A')[:10] if org_data.get('created_at') else 'N/A'}
            """)

    # ==================== CAJA 3: MIEMBROS DEL EQUIPO ====================
    with st.container(border=True):
        st.markdown("**Miembros del Equipo**")

        if not members:
            st.info("No hay miembros en la organización todavía.")
        else:
            # Separar admin de miembros
            admin_members = [m for m in members if m.get('role') == 'admin']
            regular_members = [m for m in members if m.get('role') != 'admin']

            # Mostrar admin (sin checkbox)
            if admin_members:
                st.caption("Administrador")
                admin_data = []
                for member in admin_members:
                    admin_data.append({
                        "Nombre": member.get('name', '') or '—',
                        "Correo": member.get('email', ''),
                        "Rol": "Admin"
                    })
                df_admin = pd.DataFrame(admin_data)
                st.dataframe(
                    df_admin,
                    use_container_width=True,
                    hide_index=True
                )

            # Mostrar miembros (con checkbox para eliminar)
            if regular_members:
                st.caption("Miembros")
                df_data = []
                member_ids = []

                for member in regular_members:
                    df_data.append({
                        "Nombre": member.get('name', '') or '—',
                        "Correo": member.get('email', ''),
                        "Rol": "Miembro",
                        "Eliminar": False
                    })
                    member_ids.append(member.get('id'))

                df = pd.DataFrame(df_data)

                edited_df = st.data_editor(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    disabled=["Nombre", "Correo", "Rol"],
                    column_config={
                        "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
                        "Correo": st.column_config.TextColumn("Correo", width="large"),
                        "Rol": st.column_config.TextColumn("Rol", width="small"),
                        "Eliminar": st.column_config.CheckboxColumn("Eliminar", width="small", default=False),
                    },
                    key="admin_members_table"
                )

                # Botón eliminar
                if st.button("Eliminar seleccionados", type="secondary"):
                    indices_eliminar = edited_df[edited_df["Eliminar"] == True].index.tolist()

                    if not indices_eliminar:
                        st.warning("No hay miembros seleccionados para eliminar")
                    else:
                        eliminados = 0
                        for idx in indices_eliminar:
                            try:
                                supabase.table('organization_members').delete().eq('id', member_ids[idx]).execute()
                                eliminados += 1
                            except Exception as e:
                                st.error(f"Error eliminando: {e}")

                        if eliminados > 0:
                            st.success(f"{eliminados} miembro(s) eliminado(s)")
                            st.rerun()

    # ==================== CAJA 4: AGREGAR NUEVO MIEMBRO ====================
    with st.container(border=True):
        st.markdown("**Agregar Nuevo Miembro**")

        if miembros_activos >= max_members:
            st.warning(f"Has alcanzado el límite de {max_members} miembros.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input(
                    "Nombre",
                    placeholder="Ej: Juan Pérez",
                    key="admin_new_name"
                )

            with col2:
                new_email = st.text_input(
                    "Correo electrónico",
                    placeholder="Ej: juan@empresa.com",
                    key="admin_new_email"
                )

            if st.button("Agregar Miembro", use_container_width=True, type="primary"):
                if not new_email:
                    st.error("El correo es obligatorio")
                elif not validar_email(new_email.strip()):
                    st.error("Formato de correo inválido")
                else:
                    new_email_clean = new_email.strip().lower()
                    new_name_clean = new_name.strip() if new_name else None

                    # Verificar si ya es miembro
                    existing = [m for m in members if m.get('email', '').lower() == new_email_clean]
                    if existing:
                        st.error("Este correo ya es miembro de la organización")
                    else:
                        try:
                            supabase.table('organization_members').insert({
                                'organization_id': org_id,
                                'name': new_name_clean,
                                'email': new_email_clean,
                                'role': 'member',
                                'status': 'active'
                            }).execute()

                            st.success(f"Miembro {new_email_clean} agregado")
                            st.rerun()

                        except Exception as e:
                            if 'duplicate' in str(e).lower():
                                st.error("Este correo ya es miembro de la organización")
                            else:
                                st.error(f"Error: {e}")
