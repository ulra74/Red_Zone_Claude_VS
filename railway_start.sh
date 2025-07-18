#!/bin/bash

# Railway startup script for Red Zone Academy

echo "🚀 Starting Red Zone Academy..."

# Set Django settings
export DJANGO_SETTINGS_MODULE=red_zone_academy.settings_production

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo "👤 Setting up admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@redzone.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️ Superuser already exists')
EOF

# Start Gunicorn
echo "🌐 Starting web server..."
exec gunicorn red_zone_academy.wsgi:application --bind 0.0.0.0:$PORT