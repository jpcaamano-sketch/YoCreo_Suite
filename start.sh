#!/bin/bash
# Genera secrets.toml desde variables de entorno de Railway
mkdir -p .streamlit

cat > .streamlit/secrets.toml << EOF
GOOGLE_API_KEY    = "${GOOGLE_API_KEY}"
SESSION_SECRET    = "${SESSION_SECRET}"

SUPABASE_URL      = "${SUPABASE_URL}"
SUPABASE_ANON_KEY = "${SUPABASE_ANON_KEY}"
LANDING_URL       = "${LANDING_URL}"

SMTP_USER         = "${SMTP_USER}"
SMTP_PASSWORD     = "${SMTP_PASSWORD}"

STRIPE_SECRET_KEY      = "${STRIPE_SECRET_KEY}"
STRIPE_WEBHOOK_SECRET  = "${STRIPE_WEBHOOK_SECRET}"
LANDING_API_URL        = "${LANDING_API_URL}"
LANDING_API_KEY        = "${LANDING_API_KEY}"
EOF

exec streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
