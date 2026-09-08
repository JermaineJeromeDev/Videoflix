# 1. Nutze ein offizielles Python-Image, das perfekt zu deinen Requirements passt
FROM python:3.12-slim

# 2. Setze Umgebungsvariablen für Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Setze den Arbeitsordner im Container
WORKDIR /app

# 4. Installiere System-Pakete (Zwingend notwendig für ffmpeg und PostgreSQL!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Kopiere die requirements.txt und installiere alle Python-Pakete
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Kopiere den gesamten restlichen Code in den Container
COPY . /app/

# 7. Der Befehl, den Render zum Starten ausführt (Migrationen + Server-Start)
CMD python manage.py migrate && gunicorn core.wsgi:application
