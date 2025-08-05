FROM python:3.10-slim
# 3.10.11 era la version anterior y sin el comando RUN de abajo. Seguir probando esta configuración

# Instalar dependencias del sistema operativo necesarias para compilar paquetes de Python.
#    - build-essential: para compiladores genéricos (gcc, etc.).
#    - libpq-dev: específicamente para compilar psycopg2 (el conector de PostgreSQL).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "torax_ai.wsgi:application"]
