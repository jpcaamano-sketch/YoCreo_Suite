-- Migración: Sistema de Suscripciones Individual y Empresa
-- Ejecutar en Supabase SQL Editor

-- 1. Tabla de organizaciones
CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  admin_email TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  subscription_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  max_members INTEGER DEFAULT 10,
  seat_count INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Tabla de miembros de organización
CREATE TABLE IF NOT EXISTS organization_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'member', -- 'admin' o 'member'
  status TEXT NOT NULL DEFAULT 'active',
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(organization_id, email)
);

-- 3. Agregar columna plan_type a subscriptions existente
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS plan_type TEXT DEFAULT 'individual';

-- 4. Índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_organizations_admin_email ON organizations(admin_email);
CREATE INDEX IF NOT EXISTS idx_organizations_status ON organizations(status);
CREATE INDEX IF NOT EXISTS idx_organization_members_email ON organization_members(email);
CREATE INDEX IF NOT EXISTS idx_organization_members_org_id ON organization_members(organization_id);

-- 5. Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Políticas RLS (Row Level Security) - Ajustar según necesidad
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;

-- Política para lectura pública (el webhook necesita acceso)
CREATE POLICY "Allow public read for organizations" ON organizations
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert for organizations" ON organizations
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update for organizations" ON organizations
    FOR UPDATE USING (true);

CREATE POLICY "Allow public read for organization_members" ON organization_members
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert for organization_members" ON organization_members
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public delete for organization_members" ON organization_members
    FOR DELETE USING (true);
