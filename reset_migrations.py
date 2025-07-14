#!/usr/bin/env python
"""
Script para resetear completamente las migraciones
Soluciona problemas de dependencias rotas
"""

import os
import shutil
import sys
import glob

def reset_migrations():
    """Resetear todas las migraciones"""
    print("🔄 Reseteando migraciones...")
    
    # Apps a resetear
    apps = ['accounts', 'core']
    
    for app in apps:
        migrations_dir = f"{app}/migrations"
        
        if os.path.exists(migrations_dir):
            print(f"📁 Limpiando {migrations_dir}...")
            
            # Eliminar todos los archivos de migración excepto __init__.py
            for file in glob.glob(f"{migrations_dir}/*.py"):
                if not file.endswith('__init__.py'):
                    try:
                        os.remove(file)
                        print(f"   🗑️ Eliminado: {file}")
                    except Exception as e:
                        print(f"   ❌ Error eliminando {file}: {e}")
            
            # Asegurar que __init__.py existe
            init_file = f"{migrations_dir}/__init__.py"
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('# Migrations module\n')
                print(f"   ✅ Creado: {init_file}")
        else:
            # Crear directorio de migraciones si no existe
            os.makedirs(migrations_dir, exist_ok=True)
            with open(f"{migrations_dir}/__init__.py", 'w') as f:
                f.write('# Migrations module\n')
            print(f"   ✅ Creado directorio: {migrations_dir}")
    
    print("✅ Migraciones limpiadas")

def reset_database():
    """Eliminar base de datos SQLite"""
    print("\n🗄️ Reseteando base de datos...")
    
    db_files = ['db.sqlite3', 'database.db', 'db.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"   🗑️ Eliminado: {db_file}")
            except Exception as e:
                print(f"   ❌ Error eliminando {db_file}: {e}")
    
    print("✅ Base de datos eliminada")

def create_new_migrations():
    """Crear nuevas migraciones"""
    print("\n📝 Creando nuevas migraciones...")
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
        
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        # Crear migraciones para accounts primero
        print("   📋 Creando migraciones para accounts...")
        execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])
        
        # Crear migraciones para core
        print("   📋 Creando migraciones para core...")
        execute_from_command_line(['manage.py', 'makemigrations', 'core'])
        
        print("✅ Nuevas migraciones creadas")
        return True
        
    except Exception as e:
        print(f"❌ Error creando migraciones: {e}")
        return False

def apply_migrations():
    """Aplicar migraciones"""
    print("\n⚡ Aplicando migraciones...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
        
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        # Aplicar migraciones
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migraciones aplicadas")
        return True
        
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {e}")
        return False

def create_superuser():
    """Crear superusuario"""
    print("\n👤 Creando superusuario...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
        
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@redzoneacademy.com',
                password='admin123',
                first_name='Administrador',
                last_name='Red Zone Academy'
            )
            # Establecer user_type si el modelo lo tiene
            if hasattr(user, 'user_type'):
                user.user_type = 'admin'
                user.save()
            
            print("✅ Superusuario creado: admin / admin123")
        else:
            print("✅ Superusuario ya existe")
            
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")

def main():
    """Función principal"""
    print("🔥 Red Zone Academy - Reset de Migraciones")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ No se encuentra manage.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        return False
    
    print("⚠️  Este script eliminará todas las migraciones y la base de datos")
    print("¿Continuar? (s/n): ", end="")
    
    try:
        respuesta = input().lower().strip()
        if respuesta not in ['s', 'si', 'y', 'yes']:
            print("❌ Operación cancelada")
            return False
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada")
        return False
    
    # Paso 1: Resetear migraciones
    reset_migrations()
    
    # Paso 2: Resetear base de datos
    reset_database()
    
    # Paso 3: Crear nuevas migraciones
    if not create_new_migrations():
        print("\n❌ Error en la creación de migraciones")
        return False
    
    # Paso 4: Aplicar migraciones
    if not apply_migrations():
        print("\n❌ Error aplicando migraciones")
        return False
    
    # Paso 5: Crear superusuario
    create_superuser()
    
    print("\n🎉 ¡Reset completado exitosamente!")
    print("\n🚀 Para iniciar el servidor:")
    print("   python manage.py runserver")
    print("\n🌐 URLs:")
    print("   📱 App: http://127.0.0.1:8000/")
    print("   ⚙️  Admin: http://127.0.0.1:8000/admin/")
    print("\n👤 Credenciales:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    
    return True

if __name__ == '__main__':
    main()