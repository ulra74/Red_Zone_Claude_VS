web: gunicorn red_zone_academy.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate --settings=red_zone_academy.settings_production