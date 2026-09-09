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

# 7. Run migrations, start the RQ worker, and keep Gunicorn in the foreground
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py shell -c \"import os; from django.contrib.auth import get_user_model; User=get_user_model(); username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'); email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'); password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword'); user, created=User.objects.get_or_create(email=email, defaults={'username': username}); user.username=username; user.is_staff=True; user.is_superuser=True; user.is_active=True; user.set_password(password); user.save()\" && (python manage.py rqworker default &) && exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile - --log-level info"]
