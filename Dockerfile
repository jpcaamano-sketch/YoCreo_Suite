FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para reportlab y bcrypt
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Script de arranque (genera secrets.toml desde env vars)
RUN chmod +x start.sh

# Puerto por defecto de Streamlit
EXPOSE 8501

# Healthcheck para monitoreo
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["./start.sh"]
