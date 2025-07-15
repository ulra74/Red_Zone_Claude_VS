#!/usr/bin/env python
"""
Script para diagnosticar el error específico al crear temas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
django.setup()

from core.models import Tema
from core.views import TemaForm
from django.db import connection

def test_tema_creation():
    """Probar la creación de un tema"""
    print("🧪 Probando creación de tema...")
    
    # Datos de prueba
    test_data = {
        'nombre': 'Tema de Prueba',
        'descripcion': 'Descripción de prueba',
        'orden': 1
    }
    
    try:
        # Probar con el formulario
        print("\n📝 Probando formulario...")
        form = TemaForm(data=test_data)
        print(f"   Formulario válido: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"   ❌ Errores del formulario: {form.errors}")
            return False
        
        # Probar creación directa
        print("\n🔧 Probando creación directa...")
        tema = Tema.objects.create(**test_data)
        print(f"   ✅ Tema creado: {tema.nombre}")
        
        # Limpiar
        tema.delete()
        print("   🗑️  Tema de prueba eliminado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_model_fields():
    """Verificar los campos del modelo Tema"""
    print("\n🔍 Verificando campos del modelo Tema...")
    
    # Obtener campos del modelo
    fields = Tema._meta.get_fields()
    
    print("   Campos encontrados:")
    for field in fields:
        print(f"   - {field.name}: {type(field).__name__}")
    
    # Verificar campos problemáticos
    problematic_fields = ['peso_evaluacion', 'es_obligatorio']
    for field_name in problematic_fields:
        try:
            field = Tema._meta.get_field(field_name)
            print(f"   ⚠️  Campo problemático encontrado: {field_name}")
        except:
            print(f"   ✅ Campo {field_name} no encontrado (correcto)")

def check_database_schema():
    """Verificar esquema de la base de datos"""
    print("\n🗄️  Verificando esquema de la base de datos...")
    
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(core_tema)")
        columns = cursor.fetchall()
        
        print("   Columnas en la tabla:")
        for column in columns:
            print(f"   - {column[1]}: {column[2]}")

def main():
    """Función principal de diagnóstico"""
    print("🔥 Red Zone Academy - Diagnóstico de Error en Temas")
    print("=" * 55)
    
    try:
        # Verificar modelo
        check_model_fields()
        
        # Verificar base de datos
        check_database_schema()
        
        # Probar creación
        success = test_tema_creation()
        
        if success:
            print("\n✅ Diagnóstico completado - No se encontraron errores")
        else:
            print("\n❌ Se encontraron errores en la creación de temas")
            print("\n🔧 Soluciones recomendadas:")
            print("1. Ejecutar: python fix_tema_migration.py")
            print("2. O ejecutar: python reset_migrations.py")
            print("3. Luego: python manage.py migrate")
        
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()