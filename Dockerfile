FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /code

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . /code/

# Crear directorio para logs
RUN mkdir -p /code/logs

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput --settings=red_zone_academy.settings_production

# Crear usuario no-root
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /code
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "red_zone_academy.wsgi:application", "--bind", "0.0.0.0:8000"]