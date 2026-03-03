-- Sistema de Usuarios Propio para YoCreo Suite
-- Ejecutar en Supabase SQL Editor

CREATE TABLE IF NOT EXISTS suite_usuarios (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    rol         TEXT NOT NULL DEFAULT 'suscrito'
                    CHECK (rol IN ('suscrito', 'administrador')),
    plan        TEXT NOT NULL DEFAULT 'individual'
                    CHECK (plan IN ('individual', 'empresa')),
    empresa     TEXT,
    activo      BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE suite_usuarios ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "suite_usuarios_all" ON suite_usuarios;
CREATE POLICY "suite_usuarios_all" ON suite_usuarios FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_suite_usuarios_email ON suite_usuarios(email);
CREATE INDEX IF NOT EXISTS idx_suite_usuarios_empresa ON suite_usuarios(empresa);

-- Ejemplos para probar:
-- Admin empresa:
-- INSERT INTO suite_usuarios (nombre, email, rol, plan, empresa) VALUES ('Juan', 'admin@test.com', 'administrador', 'empresa', 'ACME');
-- Suscrito individual:
-- INSERT INTO suite_usuarios (nombre, email, rol, plan) VALUES ('Pedro', 'pedro@test.com', 'suscrito', 'individual');
