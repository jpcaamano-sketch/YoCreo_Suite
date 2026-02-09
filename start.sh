#!/bin/bash
# Genera secrets.toml desde variables de entorno de Railway
mkdir -p .streamlit

cat > .streamlit/secrets.toml << EOF
GOOGLE_API_KEY = "${GOOGLE_API_KEY}"
SUPABASE_URL = "${SUPABASE_URL}"
SUPABASE_ANON_KEY = "${SUPABASE_ANON_KEY}"
LANDING_URL = "${LANDING_URL}"
EOF

exec streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
