-- Migración 004: Columnas Stripe en suite_usuarios
-- Ejecutar en Supabase SQL Editor

-- Columnas para vincular con Stripe
ALTER TABLE suite_usuarios
    ADD COLUMN IF NOT EXISTS stripe_customer_id    TEXT,
    ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT,
    ADD COLUMN IF NOT EXISTS organization_id        TEXT;

-- Índice para búsquedas por stripe_customer_id (webhook)
CREATE INDEX IF NOT EXISTS idx_suite_usuarios_stripe_cid
    ON suite_usuarios (stripe_customer_id)
    WHERE stripe_customer_id IS NOT NULL;

-- Tabla de configuración empresa (logo, etc.)  ← de la migración anterior
CREATE TABLE IF NOT EXISTS suite_empresa_config (
    id          BIGSERIAL   PRIMARY KEY,
    empresa     TEXT        NOT NULL UNIQUE,
    logo_b64    TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE suite_empresa_config ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "anon_all_empresa_config" ON suite_empresa_config
    FOR ALL TO anon USING (true) WITH CHECK (true);
