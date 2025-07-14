#!/usr/bin/env python
"""
Script de configuración inicial para Red Zone Academy
Ejecutar después de clonar el proyecto para configurar todo automáticamente
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔄 {description}...")
    try:
        if isinstance(command, list):
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(e.stderr)
        return False

def setup_project():
    """Configuración principal del proyecto"""
    print("🔥 Red Zone Academy - Setup Inicial")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ Error: No se encuentra manage.py. Ejecuta este script desde el directorio raíz del proyecto.")
        sys.exit(1)
    
    # Configurar DJANGO_SETTINGS_MODULE
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
    
    # 1. Crear migraciones iniciales
    print("\n1️⃣ Creando migraciones...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✅ Migraciones creadas")
    except Exception as e:
        print(f"❌ Error creando migraciones: {e}")
        return False
    
    # 2. Aplicar migraciones
    print("\n2️⃣ Aplicando migraciones...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones aplicadas")
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {e}")
        return False
    
    # 3. Ejecutar comando de setup personalizado
    print("\n3️⃣ Configurando estructura inicial...")
    try:
        execute_from_command_line(['manage.py', 'setup_academy', '--create-superuser'])
        print("✅ Estructura inicial configurada")
    except Exception as e:
        print(f"❌ Error configurando estructura: {e}")
        return False
    
    # 4. Crear archivos estáticos
    print("\n4️⃣ Recolectando archivos estáticos...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Archivos estáticos recolectados")
    except Exception as e:
        print(f"⚠️ Advertencia recolectando estáticos: {e}")
    
    # Mostrar información final
    print("\n" + "=" * 50)
    print("🎉 Red Zone Academy configurada correctamente!")
    print("\n📋 Credenciales de acceso:")
    print("   🔗 URL: http://127.0.0.1:8000/")
    print("   👤 Admin: admin / admin123")
    print("   🎓 Estudiante: estudiante / estudiante123")
    print("\n🚀 Para iniciar el servidor:")
    print("   python manage.py runserver")
    print("\n📚 URLs importantes:")
    print("   🏠 Inicio: http://127.0.0.1:8000/")
    print("   ⚙️  Admin: http://127.0.0.1:8000/admin/")
    print("   📊 Dashboard: http://127.0.0.1:8000/dashboard/")
    print("   📝 Exámenes: http://127.0.0.1:8000/examenes/")
    
    return True

def create_env_file():
    """Crear archivo .env de ejemplo si no existe"""
    env_file = '.env'
    if not os.path.exists(env_file):
        env_content = """# Red Zone Academy - Variables de Entorno
DEBUG=True
SECRET_KEY=django-insecure-*@hcv9g+qw(a*fkjh^^0@^*21**nu*d3b1b(9kiwes3&nu$xq^
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (SQLite por defecto)
DATABASE_URL=sqlite:///db.sqlite3

# Email (para desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Media y Static
MEDIA_ROOT=media/
STATIC_ROOT=staticfiles/
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Archivo {env_file} creado")

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 o superior es requerido")
        print(f"   Tu versión: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detectado")

def install_requirements():
    """Instalar dependencias"""
    if os.path.exists('requirements.txt'):
        print("\n📦 Instalando dependencias...")
        return run_command(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            "Instalación de dependencias"
        )
    else:
        print("⚠️ No se encontró requirements.txt")
        # Instalar dependencias básicas
        packages = [
            'Django>=4.2,<5.0',
            'Pillow',  # Para ImageField
            'python-decouple',  # Para variables de entorno
        ]
        for package in packages:
            run_command(
                [sys.executable, '-m', 'pip', 'install', package],
                f"Instalando {package}"
            )
    return True

if __name__ == '__main__':
    print("🔥 Red Zone Academy - Configuración Automática")
    print("=" * 60)
    
    # Verificaciones previas
    check_python_version()
    
    # Crear archivo de entorno
    create_env_file()
    
    # Instalar dependencias
    install_requirements()
    
    # Configurar proyecto Django
    if setup_project():
        print("\n🎉 ¡Configuración completada exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   1. python manage.py runserver")
        print("   2. Abre http://127.0.0.1:8000 en tu navegador")
        print("   3. ¡Comienza a usar Red Zone Academy!")
    else:
        print("\n❌ Hubo errores en la configuración")
        print("   Revisa los mensajes anteriores para más detalles")
        sys.exit(1)