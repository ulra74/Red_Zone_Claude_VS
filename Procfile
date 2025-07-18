web: gunicorn red_zone_academy.wsgi:application --bind 0.0.0.0:$PORT --settings=red_zone_academy.settings_production
release: python manage.py migrate --settings=red_zone_academy.settings_production