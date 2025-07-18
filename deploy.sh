#!/bin/bash

# Red Zone Academy - Script de Despliegue
# Este script automatiza el proceso de despliegue en producción

set -e  # Salir si cualquier comando falla

echo "🚀 Red Zone Academy - Iniciando despliegue..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    print_error "Error: No se encontró manage.py. Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar variables de entorno
if [ ! -f ".env" ]; then
    print_warning "Archivo .env no encontrado. Copia .env.example a .env y configúralo."
    print_warning "cp .env.example .env"
    exit 1
fi

print_status "Verificando dependencias..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado."
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 no está instalado."
    exit 1
fi

print_status "Instalando dependencias de Python..."
pip3 install -r requirements.txt

print_status "Verificando configuración de base de datos..."

# Verificar si PostgreSQL está disponible (opcional)
if command -v psql &> /dev/null; then
    print_status "PostgreSQL detectado. Asegúrate de que la base de datos esté configurada."
else
    print_warning "PostgreSQL no detectado. Se usará SQLite."
fi

print_status "Ejecutando migraciones de base de datos..."
python3 manage.py migrate --settings=red_zone_academy.settings_production

print_status "Recolectando archivos estáticos..."
python3 manage.py collectstatic --noinput --settings=red_zone_academy.settings_production

print_status "Verificando configuración del proyecto..."
python3 manage.py check --settings=red_zone_academy.settings_production

# Crear directorio de logs si no existe
mkdir -p logs

print_status "Creando superusuario (si no existe)..."
python3 manage.py shell --settings=red_zone_academy.settings_production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@redzone.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('El superusuario ya existe')
EOF

print_status "Verificando permisos de archivos..."
chmod +x deploy.sh

echo ""
print_status "🎉 Despliegue completado exitosamente!"
echo ""
echo "Próximos pasos:"
echo "1. Configura tu servidor web (Nginx/Apache)"
echo "2. Configura un proceso manager como systemd o supervisor"
echo "3. Configura SSL/TLS"
echo "4. Configura backups automáticos"
echo ""
echo "Para ejecutar en desarrollo:"
echo "python3 manage.py runserver --settings=red_zone_academy.settings"
echo ""
echo "Para ejecutar en producción:"
echo "gunicorn red_zone_academy.wsgi:application --settings=red_zone_academy.settings_production"
echo ""
print_warning "Recuerda cambiar las credenciales por defecto del superusuario!"
echo ""