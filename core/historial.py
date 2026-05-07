"""
Historial de generaciones - YoCreo Suite
Guarda y recupera las últimas generaciones del usuario.

-- SQL para crear la tabla (ejecutar en Supabase SQL Editor):
CREATE TABLE IF NOT EXISTS suite_historial (
    id         BIGSERIAL   PRIMARY KEY,
    email      TEXT        NOT NULL,
    practica   TEXT        NOT NULL,
    titulo     TEXT,
    contenido  TEXT        NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_historial_email ON suite_historial (email, created_at DESC);
ALTER TABLE suite_historial ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_insert_historial" ON suite_historial FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_select_historial" ON suite_historial FOR SELECT TO anon USING (true);
"""

import logging
import streamlit as st
from .database import get_supabase

logger = logging.getLogger(__name__)

PRACTICA_NOMBRES = {
    "priorizador_tareas":       "Priorizador de Tareas",
    "planificador_reuniones":   "Planificador de Reuniones",
    "pedidos_impecables":       "Pedidos Impecables",
    "delegacion_situacional":   "Delegación Situacional",
    "correos_diplomaticos":     "Correos Diplomáticos",
    "seguimiento_compromisos":  "Seguimiento de Compromisos",
    "escucha_activa":           "Escucha Activa",
    "feedback_constructivo":    "Feedback Constructivo",
    "evaluacion_desempeno":     "Evaluación de Desempeño",
    "negociador_harvard":       "Negociador Harvard",
    "presentacion_inspiradora": "Presentación Inspiradora",
    "preguntas_desafiantes":    "Preguntas Desafiantes",
    "definicion_objetivos":     "Definición de Objetivos",
    "disculpas_efectivas":      "Disculpas Efectivas",
}


def guardar_generacion(practica: str, contenido: str, titulo: str = None) -> bool:
    """Guarda una generación en suite_historial. Falla silenciosamente."""
    try:
        user = st.session_state.get('user', {})
        email = user.get('email', '')
        if not email or not contenido:
            return False
        supabase = get_supabase()
        supabase.table('suite_historial').insert({
            'email':    email,
            'practica': practica,
            'titulo':   titulo or PRACTICA_NOMBRES.get(practica, practica),
            'contenido': contenido[:5000],
        }).execute()
        return True
    except Exception as e:
        logger.warning("No se pudo guardar en historial: %s", e)
        return False


def obtener_historial(email: str, limit: int = 10) -> list:
    """Retorna las últimas `limit` generaciones del usuario."""
    try:
        supabase = get_supabase()
        resp = (
            supabase.table('suite_historial')
            .select('id, practica, titulo, contenido, created_at')
            .eq('email', email)
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data if resp.data else []
    except Exception as e:
        logger.warning("No se pudo obtener historial: %s", e)
        return []
