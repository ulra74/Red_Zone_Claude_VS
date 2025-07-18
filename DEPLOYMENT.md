# Red Zone Academy - Guía de Despliegue

## 📋 Requisitos Previos

### Sistema Operativo
- Ubuntu 20.04+ / CentOS 8+ / macOS
- Python 3.8+
- PostgreSQL 12+ (recomendado) o SQLite
- Nginx (recomendado para producción)

### Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql postgresql-server nginx
```

## 🚀 Despliegue Rápido

### 1. Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd red_zone_academy
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
# Edita .env con tus configuraciones
```

### 3. Ejecutar Script de Despliegue
```bash
chmod +x deploy.sh
./deploy.sh
```

## ⚙️ Configuración Manual

### 1. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE red_zone_academy;
CREATE USER red_zone_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE red_zone_academy TO red_zone_user;
\q
```

### 4. Configurar Variables de Entorno
Edita el archivo `.env`:
```env
DJANGO_SECRET_KEY=tu-clave-secreta-super-segura
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DB_NAME=red_zone_academy
DB_USER=red_zone_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Ejecutar Migraciones
```bash
python manage.py migrate --settings=red_zone_academy.settings_production
```

### 6. Recopilar Archivos Estáticos
```bash
python manage.py collectstatic --noinput --settings=red_zone_academy.settings_production
```

### 7. Crear Superusuario
```bash
python manage.py createsuperuser --settings=red_zone_academy.settings_production
```

## 🌐 Configuración del Servidor Web

### Nginx
Crear archivo de configuración en `/etc/nginx/sites-available/red_zone_academy`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /ruta/a/tu/proyecto/red_zone_academy;
    }
    
    location /media/ {
        root /ruta/a/tu/proyecto/red_zone_academy;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/ruta/a/tu/proyecto/red_zone_academy/red_zone_academy.sock;
    }
}
```

Activar la configuración:
```bash
sudo ln -s /etc/nginx/sites-available/red_zone_academy /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Gunicorn con Systemd
Crear archivo `/etc/systemd/system/red_zone_academy.service`:

```ini
[Unit]
Description=Red Zone Academy Django Application
After=network.target

[Service]
User=tu-usuario
Group=www-data
WorkingDirectory=/ruta/a/tu/proyecto/red_zone_academy
Environment="PATH=/ruta/a/tu/proyecto/red_zone_academy/venv/bin"
EnvironmentFile=/ruta/a/tu/proyecto/red_zone_academy/.env
ExecStart=/ruta/a/tu/proyecto/red_zone_academy/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/ruta/a/tu/proyecto/red_zone_academy/red_zone_academy.sock \
          red_zone_academy.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl start red_zone_academy
sudo systemctl enable red_zone_academy
sudo systemctl status red_zone_academy
```

## 🔐 SSL/TLS con Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

## 📊 Monitoreo y Logs

### Ver Logs de la Aplicación
```bash
# Logs de Django
tail -f logs/django.log

# Logs de Gunicorn
sudo journalctl -u red_zone_academy -f

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Monitoreo del Sistema
```bash
# Estado del servicio
sudo systemctl status red_zone_academy

# Uso de recursos
htop

# Espacio en disco
df -h
```

## 🔄 Actualizaciones

Para actualizar la aplicación:

```bash
# 1. Hacer backup de la base de datos
pg_dump red_zone_academy > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Actualizar código
git pull origin main

# 4. Instalar nuevas dependencias
pip install -r requirements.txt

# 5. Ejecutar migraciones
python manage.py migrate --settings=red_zone_academy.settings_production

# 6. Recopilar archivos estáticos
python manage.py collectstatic --noinput --settings=red_zone_academy.settings_production

# 7. Reiniciar servicios
sudo systemctl restart red_zone_academy
sudo systemctl reload nginx
```

## 🛠️ Solución de Problemas

### Error de Permisos
```bash
# Dar permisos correctos a los archivos
sudo chown -R tu-usuario:www-data /ruta/a/tu/proyecto
sudo chmod -R 755 /ruta/a/tu/proyecto
```

### Error de Base de Datos
```bash
# Verificar conexión a PostgreSQL
psql -h localhost -U red_zone_user -d red_zone_academy

# Revisar configuración en .env
cat .env
```

### Error 502 Bad Gateway
```bash
# Verificar estado de Gunicorn
sudo systemctl status red_zone_academy

# Verificar logs
sudo journalctl -u red_zone_academy -f
```

## 📈 Optimización de Rendimiento

### Cache Redis (Opcional)
```bash
sudo apt install redis-server
```

Añadir a `settings_production.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Configuración de PostgreSQL
```sql
-- Optimizaciones básicas para PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();
```

## 🔒 Seguridad

### Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Backups Automáticos
Crear script de backup en `/usr/local/bin/backup_red_zone.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/red_zone_academy"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de base de datos
pg_dump red_zone_academy > $BACKUP_DIR/db_backup_$DATE.sql

# Backup de archivos media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/

# Limpiar backups antiguos (mantener 7 días)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Añadir a crontab:
```bash
# Backup diario a las 2:00 AM
0 2 * * * /usr/local/bin/backup_red_zone.sh
```

## 📞 Soporte

Para problemas específicos del despliegue:
1. Revisar logs de la aplicación
2. Verificar configuración de variables de entorno
3. Comprobar estado de servicios del sistema
4. Consultar la documentación de Django para producción

## 🎯 URLs Importantes Post-Despliegue

- Aplicación principal: `https://tu-dominio.com/`
- Panel de administración: `https://tu-dominio.com/admin/`
- Dashboard: `https://tu-dominio.com/dashboard/`

**¡Recuerda cambiar las credenciales por defecto del superusuario!**