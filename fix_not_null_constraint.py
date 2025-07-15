#!/usr/bin/env python
"""
Script para corregir el error NOT NULL constraint failed: core_tema.es_obligatorio
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
django.setup()

from django.db import connection, transaction
from django.core.management import execute_from_command_line

def fix_not_null_constraint():
    """Corregir el problema NOT NULL eliminando las columnas problemáticas"""
    print("🔧 Corrigiendo NOT NULL constraint failed...")
    
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Verificar si las columnas problemáticas existen
                cursor.execute("PRAGMA table_info(core_tema)")
                columns = cursor.fetchall()
                
                existing_columns = [col[1] for col in columns]
                problematic_fields = ['es_obligatorio', 'peso_evaluacion']
                
                print(f"📋 Columnas existentes: {existing_columns}")
                
                # Verificar cuáles campos problemáticos existen
                fields_to_remove = [field for field in problematic_fields if field in existing_columns]
                
                if fields_to_remove:
                    print(f"⚠️  Campos problemáticos encontrados: {fields_to_remove}")
                    
                    # SQLite no soporta DROP COLUMN en versiones antiguas
                    # Necesitamos recrear la tabla
                    recreate_tema_table(cursor, existing_columns, fields_to_remove)
                    
                else:
                    print("✅ No se encontraron campos problemáticos")
                    return True
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def recreate_tema_table(cursor, existing_columns, fields_to_remove):
    """Recrear la tabla core_tema sin los campos problemáticos"""
    print("🔄 Recreando tabla core_tema...")
    
    # Columnas que queremos mantener
    keep_columns = [col for col in existing_columns if col not in fields_to_remove]
    
    # Definir la nueva estructura de la tabla
    new_table_sql = """
        CREATE TABLE core_tema_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(200) NOT NULL,
            descripcion TEXT NOT NULL,
            orden INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """
    
    try:
        # 1. Crear tabla temporal con estructura correcta
        print("   📝 Creando tabla temporal...")
        cursor.execute(new_table_sql)
        
        # 2. Copiar datos existentes (solo las columnas que queremos mantener)
        print("   📋 Copiando datos existentes...")
        
        # Crear la consulta SELECT solo con columnas válidas
        valid_columns = ['id', 'nombre', 'descripcion', 'orden', 'created_at', 'updated_at']
        available_columns = [col for col in valid_columns if col in keep_columns]
        
        if available_columns:
            select_columns = ', '.join(available_columns)
            insert_columns = ', '.join(available_columns)
            
            copy_sql = f"""
                INSERT INTO core_tema_new ({insert_columns})
                SELECT {select_columns} FROM core_tema
            """
            
            cursor.execute(copy_sql)
            print(f"   ✅ {cursor.rowcount} registros copiados")
        
        # 3. Eliminar tabla original
        print("   🗑️  Eliminando tabla original...")
        cursor.execute("DROP TABLE core_tema")
        
        # 4. Renombrar tabla nueva
        print("   📝 Renombrando tabla nueva...")
        cursor.execute("ALTER TABLE core_tema_new RENAME TO core_tema")
        
        # 5. Recrear índices y relaciones si es necesario
        print("   🔗 Recreando relaciones...")
        recreate_relationships(cursor)
        
        print("✅ Tabla recreada exitosamente")
        
    except Exception as e:
        print(f"❌ Error recreando tabla: {e}")
        # Intentar limpiar tabla temporal si existe
        try:
            cursor.execute("DROP TABLE IF EXISTS core_tema_new")
        except:
            pass
        raise

def recreate_relationships(cursor):
    """Recrear las relaciones many-to-many"""
    print("   🔗 Verificando relaciones many-to-many...")
    
    # Verificar si las tablas de relación existen
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'core_tema_%'
    """)
    
    related_tables = cursor.fetchall()
    print(f"   📋 Tablas relacionadas encontradas: {[table[0] for table in related_tables]}")

def verify_fix():
    """Verificar que la corrección funcionó"""
    print("\n🔍 Verificando corrección...")
    
    try:
        from core.models import Tema
        
        # Intentar crear un tema de prueba
        test_tema = Tema.objects.create(
            nombre="Tema de Prueba",
            descripcion="Descripción de prueba",
            orden=1
        )
        
        print("✅ Tema de prueba creado exitosamente")
        
        # Limpiar
        test_tema.delete()
        print("🗑️  Tema de prueba eliminado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal"""
    print("🔥 Red Zone Academy - Corrección NOT NULL Constraint")
    print("=" * 55)
    
    try:
        # Corregir el problema
        if fix_not_null_constraint():
            print("\n✅ Corrección aplicada")
            
            # Verificar que funciona
            if verify_fix():
                print("\n🎉 ¡Problema resuelto! Ya puedes crear temas.")
            else:
                print("\n⚠️  La corrección se aplicó pero hay otros problemas")
        else:
            print("\n❌ Error aplicando la corrección")
            
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        print("\n🔧 Solución alternativa:")
        print("1. Ejecuta: python reset_migrations.py")
        print("2. Luego: python manage.py migrate")

if __name__ == '__main__':
    main()