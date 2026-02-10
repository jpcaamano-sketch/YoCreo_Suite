-- Migración 002: Corregir schema de organizations
-- Ejecutar en Supabase SQL Editor
-- Problema: faltaba columna seat_count y max_members era NOT NULL

-- 1. Agregar columna seat_count
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS seat_count INTEGER DEFAULT 1;

-- 2. Permitir NULL en max_members (el webhook envía null para empresas sin límite)
ALTER TABLE organizations ALTER COLUMN max_members DROP NOT NULL;
