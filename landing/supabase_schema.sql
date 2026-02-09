-- Tabla de suscripciones para YoCreo Suite
-- Ejecutar en Supabase SQL Editor

CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  customer_id TEXT NOT NULL,
  subscription_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_subscriptions_email ON subscriptions(email);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer_id ON subscriptions(customer_id);

-- Habilitar Row Level Security
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Política para permitir lectura desde la API (con anon key)
CREATE POLICY "Allow read access for valid subscriptions" ON subscriptions
  FOR SELECT
  USING (true);

-- Política para permitir inserciones desde el webhook
CREATE POLICY "Allow insert from webhook" ON subscriptions
  FOR INSERT
  WITH CHECK (true);

-- Política para permitir actualizaciones desde el webhook
CREATE POLICY "Allow update from webhook" ON subscriptions
  FOR UPDATE
  USING (true);
