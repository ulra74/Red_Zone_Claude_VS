#!/usr/bin/env python
"""
Script para corregir problemas con las migraciones de Tema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def check_database_state():
    """Verificar el estado actual de la base de datos"""
    print("🔍 Verificando estado de la base de datos...")
    
    with connection.cursor() as cursor:
        # Verificar si la tabla core_tema existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='core_tema'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ La tabla core_tema no existe")
            return False
        
        # Verificar qué columnas existen
        cursor.execute("PRAGMA table_info(core_tema)")
        columns = cursor.fetchall()
        
        print("\n📋 Columnas actuales en core_tema:")
        column_names = []
        for column in columns:
            column_name = column[1]
            column_names.append(column_name)
            print(f"   - {column_name}")
        
        # Verificar si los campos problemáticos existen
        problematic_fields = ['peso_evaluacion', 'es_obligatorio']
        existing_problematic = [field for field in problematic_fields if field in column_names]
        
        if existing_problematic:
            print(f"\n⚠️  Campos problemáticos encontrados: {existing_problematic}")
            return existing_problematic
        else:
            print("\n✅ No se encontraron campos problemáticos")
            return []

def fix_migration():
    """Corregir el problema de migración"""
    print("\n🔧 Aplicando corrección...")
    
    # Verificar estado
    problematic_fields = check_database_state()
    
    if problematic_fields:
        print(f"🚨 Eliminando campos problemáticos: {problematic_fields}")
        
        with connection.cursor() as cursor:
            for field in problematic_fields:
                try:
                    print(f"   🗑️  Eliminando columna: {field}")
                    cursor.execute(f"ALTER TABLE core_tema DROP COLUMN {field}")
                    print(f"   ✅ Columna {field} eliminada")
                except Exception as e:
                    print(f"   ⚠️  Error eliminando {field}: {e}")
                    # En SQLite, DROP COLUMN no está disponible en versiones antiguas
                    # Necesitamos recrear la tabla
                    recreate_table_without_fields(cursor, problematic_fields)
                    break
    
    # Verificar el estado final
    print("\n🔍 Verificando estado final...")
    check_database_state()

def recreate_table_without_fields(cursor, fields_to_remove):
    """Recrear la tabla sin los campos problemáticos (para SQLite)"""
    print("🔄 Recreando tabla sin campos problemáticos...")
    
    try:
        # Obtener la estructura actual
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='core_tema'")
        original_sql = cursor.fetchone()[0]
        
        # Crear tabla temporal
        cursor.execute("""
            CREATE TABLE core_tema_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT NOT NULL,
                orden INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Copiar datos (excluyendo campos problemáticos)
        cursor.execute("""
            INSERT INTO core_tema_temp (id, nombre, descripcion, orden, created_at, updated_at)
            SELECT id, nombre, descripcion, orden, created_at, updated_at
            FROM core_tema
        """)
        
        # Eliminar tabla original
        cursor.execute("DROP TABLE core_tema")
        
        # Renombrar tabla temporal
        cursor.execute("ALTER TABLE core_tema_temp RENAME TO core_tema")
        
        print("✅ Tabla recreada exitosamente")
        
    except Exception as e:
        print(f"❌ Error recreando tabla: {e}")
        raise

def main():
    """Función principal"""
    print("🔥 Red Zone Academy - Corrección de Migraciones")
    print("=" * 50)
    
    try:
        fix_migration()
        print("\n✅ Corrección completada exitosamente")
        print("\n💡 Ahora puedes intentar crear temas nuevamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la corrección: {e}")
        print("\n🔧 Solución alternativa:")
        print("1. Ejecuta: python reset_migrations.py")
        print("2. Luego ejecuta: python manage.py migrate")

if __name__ == '__main__':
    main()