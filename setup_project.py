#!/usr/bin/env python
"""
Script de configuración inicial para Red Zone Academy - VERSIÓN CORREGIDA
Maneja incompatibilidades de versiones de Python/Django
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def check_python_version():
    """Verificar versión de Python y mostrar advertencias"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro} detectado")
    
    if version >= (3, 13):
        print("⚠️  ADVERTENCIA: Python 3.13+ puede tener problemas de compatibilidad")
        print("   Recomendado: Python 3.11 o 3.12")
        print("   ¿Continuar de todos modos? (s/n): ", end="")
        
        try:
            respuesta = input().lower().strip()
            if respuesta not in ['s', 'si', 'y', 'yes']:
                print("❌ Instalación cancelada")
                print("\n💡 Soluciones recomendadas:")
                print("   1. Usar pyenv para instalar Python 3.12:")
                print("      pyenv install 3.12.0")
                print("      pyenv local 3.12.0")
                print("\n   2. Crear entorno virtual con Python 3.12:")
                print("      python3.12 -m venv venv")
                print("      source venv/bin/activate")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n❌ Instalación cancelada")
            sys.exit(1)
    elif version < (3, 8):
        print("❌ Python 3.8 o superior es requerido")
        print(f"   Tu versión: {version.major}.{version.minor}")
        sys.exit(1)
    else:
        print("✅ Versión de Python compatible")

def clean_django_cache():
    """Limpiar cache de Django que puede causar problemas"""
    print("🧹 Limpiando cache de Django...")
    
    # Eliminar archivos .pyc
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass
    
    # Eliminar directorios __pycache__
    for root, dirs, files in os.walk('.', topdown=False):
        for dirname in dirs:
            if dirname == '__pycache__':
                try:
                    import shutil
                    shutil.rmtree(os.path.join(root, dirname))
                except:
                    pass
    
    print("✅ Cache limpiado")

def install_django_compatible():
    """Instalar Django con versión compatible"""
    print("📦 Instalando Django compatible...")
    
    python_version = sys.version_info
    
    if python_version >= (3, 13):
        # Para Python 3.13, usar la versión más reciente disponible
        django_version = "Django>=5.0,<5.1"
        print(f"   Instalando Django 5.0 para Python {python_version.major}.{python_version.minor}")
    elif python_version >= (3, 11):
        django_version = "Django>=4.2,<5.1"
        print(f"   Instalando Django 4.2+ para Python {python_version.major}.{python_version.minor}")
    else:
        django_version = "Django>=4.2,<5.0"
        print(f"   Instalando Django 4.2 para Python {python_version.major}.{python_version.minor}")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            django_version, 'Pillow>=10.0.0', 'python-decouple>=3.8'
        ], check=True, capture_output=True)
        print("✅ Django instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando Django: {e}")
        return False

def run_django_command(command_list, description):
    """Ejecutar comando de Django con manejo de errores mejorado"""
    print(f"\n🔄 {description}...")
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
        
        # Importar Django y configurar
        import django
        django.setup()
        
        # Ejecutar comando
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py'] + command_list)
        
        print(f"✅ {description} completado")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación en {description}: {e}")
        print("💡 Intenta reinstalar Django:")
        print("   pip uninstall django")
        print("   pip install Django==4.2")
        return False
        
    except Exception as e:
        print(f"❌ Error en {description}: {e}")
        
        # Intentos alternativos para migraciones
        if 'makemigrations' in command_list:
            print("🔄 Intentando migración alternativa...")
            try:
                execute_from_command_line(['manage.py', 'makemigrations', '--empty', 'core'])
                execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])
                execute_from_command_line(['manage.py', 'makemigrations', 'core'])
                print("✅ Migraciones creadas con método alternativo")
                return True
            except Exception as e2:
                print(f"❌ Error en migración alternativa: {e2}")
        
        return False

def create_minimal_migration():
    """Crear migración mínima manualmente si hay problemas"""
    print("🔧 Creando migración manual...")
    
    migration_content = '''# Generated manually for compatibility
from django.db import migrations

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = []
'''
    
    # Crear directorio de migraciones si no existe
    os.makedirs('core/migrations', exist_ok=True)
    os.makedirs('accounts/migrations', exist_ok=True)
    
    # Crear archivos __init__.py
    for app in ['core', 'accounts']:
        init_file = f'{app}/migrations/__init__.py'
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')
    
    print("✅ Estructura de migraciones creada")

def setup_project():
    """Configuración principal del proyecto con manejo robusto de errores"""
    print("🔥 Red Zone Academy - Setup Inicial (Versión Corregida)")
    print("=" * 60)
    
    # Verificar directorio
    if not os.path.exists('manage.py'):
        print("❌ Error: No se encuentra manage.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Verificar Python
    check_python_version()
    
    # Limpiar cache
    clean_django_cache()
    
    # Instalar Django compatible
    if not install_django_compatible():
        return False
    
    # Configurar entorno Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
    
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False
    
    # Crear estructura de migraciones
    create_minimal_migration()
    
    # 1. Crear migraciones
    if not run_django_command(['makemigrations'], 'Creando migraciones'):
        print("⚠️ Continuando sin migraciones nuevas...")
    
    # 2. Aplicar migraciones
    if not run_django_command(['migrate'], 'Aplicando migraciones'):
        print("❌ Error crítico en migraciones")
        return False
    
    # 3. Crear superusuario
    print("\n3️⃣ Creando superusuario...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@redzoneacademy.com',
                password='admin123',
                first_name='Administrador',
                last_name='RZA',
                user_type='admin'
            )
            print("✅ Superusuario creado: admin / admin123")
        else:
            print("✅ Superusuario ya existe")
    except Exception as e:
        print(f"⚠️ Error creando superusuario: {e}")
    
    # 4. Crear contenido inicial
    print("\n4️⃣ Creando contenido inicial...")
    try:
        from core.models import Categoria
        
        categorias = [
            {'nombre': 'Legislación', 'color': '#dc3545', 'orden': 1},
            {'nombre': 'Técnicas de Intervención', 'color': '#fd7e14', 'orden': 2},
            {'nombre': 'Primeros Auxilios', 'color': '#198754', 'orden': 3},
        ]
        
        for cat_data in categorias:
            Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
        
        print("✅ Contenido inicial creado")
    except Exception as e:
        print(f"⚠️ Error creando contenido: {e}")
    
    return True

def show_final_instructions():
    """Mostrar instrucciones finales"""
    print("\n" + "=" * 60)
    print("🎉 ¡Configuración completada!")
    print("\n📋 Credenciales:")
    print("   👤 Admin: admin / admin123")
    print("\n🚀 Para iniciar:")
    print("   python manage.py runserver")
    print("\n🌐 URLs:")
    print("   📱 App: http://127.0.0.1:8000/")
    print("   ⚙️  Admin: http://127.0.0.1:8000/admin/")
    
    print("\n💡 Si hay problemas:")
    print("   1. Verifica que el servidor funcione")
    print("   2. Accede al admin para crear contenido")
    print("   3. Revisa los logs en la consola")

def show_troubleshooting():
    """Mostrar guía de solución de problemas"""
    print("\n🔧 SOLUCIÓN DE PROBLEMAS:")
    print("\n1. Problemas de Python 3.13:")
    print("   - Usar Python 3.11 o 3.12")
    print("   - pyenv install 3.12.0")
    print("   - pyenv local 3.12.0")
    
    print("\n2. Reinstalar Django:")
    print("   - pip uninstall django")
    print("   - pip install Django==4.2")
    
    print("\n3. Limpiar y resetear:")
    print("   - rm -rf core/migrations/*")
    print("   - rm -rf accounts/migrations/*")
    print("   - rm db.sqlite3")
    print("   - python manage.py makemigrations")
    print("   - python manage.py migrate")

if __name__ == '__main__':
    try:
        if setup_project():
            show_final_instructions()
        else:
            print("\n❌ Configuración falló")
            show_troubleshooting()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        show_troubleshooting()
        sys.exit(1)