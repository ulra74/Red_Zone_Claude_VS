#!/usr/bin/env python
"""
Script para configurar la base de datos de producción en PostgreSQL
"""

import os
import sys
import django
from pathlib import Path

# Añadir el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings_production')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from core.models import Oposicion, Tema, Apartado, Pregunta, BancoPregunta

def setup_database():
    """Configura la base de datos desde cero"""
    
    print("🔥 Red Zone Academy - Configuración de Base de Datos PostgreSQL")
    print("=" * 60)
    
    # 1. Ejecutar migraciones
    print("📦 Ejecutando migraciones...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # 2. Crear superusuario
    print("👤 Creando superusuario...")
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@redzone.com',
            password='admin123',
            first_name='Administrador',
            last_name='Red Zone',
            user_type='admin'
        )
        print(f"✅ Superusuario creado: admin/admin123")
    else:
        print("ℹ️ El superusuario admin ya existe")
    
    # 3. Crear usuarios estudiantes de ejemplo
    print("👥 Creando estudiantes de ejemplo...")
    estudiantes_data = [
        {'username': 'jperez', 'first_name': 'Juan', 'last_name': 'Pérez García', 'email': 'juan.perez@email.com'},
        {'username': 'mlopez', 'first_name': 'María', 'last_name': 'López Rodríguez', 'email': 'maria.lopez@email.com'},
        {'username': 'arojas', 'first_name': 'Antonio', 'last_name': 'Rojas Martín', 'email': 'antonio.rojas@email.com'},
        {'username': 'cgomez', 'first_name': 'Carmen', 'last_name': 'Gómez Santos', 'email': 'carmen.gomez@email.com'},
        {'username': 'dgarcia', 'first_name': 'David', 'last_name': 'García Fernández', 'email': 'david.garcia@email.com'},
    ]
    
    for data in estudiantes_data:
        if not User.objects.filter(username=data['username']).exists():
            User.objects.create_user(
                username=data['username'],
                password='estudiante123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                user_type='student'
            )
            print(f"✅ Estudiante creado: {data['first_name']} {data['last_name']} ({data['username']})")
    
    # 4. Crear oposición de ejemplo
    print("🔥 Creando oposición de ejemplo...")
    oposicion, created = Oposicion.objects.get_or_create(
        nombre="Bombero/a - Ayuntamiento 2024",
        defaults={
            'descripcion': 'Oposición para el cuerpo de bomberos del ayuntamiento. Incluye temario completo y ejercicios prácticos.',
            'fecha_convocatoria': '2024-06-15'
        }
    )
    
    if created:
        # Asignar todos los estudiantes a la oposición
        estudiantes = User.objects.filter(user_type='student')
        oposicion.alumnos_con_acceso.set(estudiantes)
        print(f"✅ Oposición creada: {oposicion.nombre}")
    
    # 5. Crear temas de ejemplo
    print("📚 Creando temas de ejemplo...")
    temas_data = [
        {
            'nombre': 'Legislación sobre Prevención de Riesgos Laborales',
            'descripcion': 'Marco normativo de prevención de riesgos laborales aplicado al cuerpo de bomberos.',
            'orden': 1
        },
        {
            'nombre': 'Técnicas de Extinción de Incendios',
            'descripcion': 'Métodos y técnicas para la extinción de diferentes tipos de incendios.',
            'orden': 2
        },
        {
            'nombre': 'Rescate en Altura y Espacios Confinados',
            'descripción': 'Procedimientos de rescate en situaciones de altura y espacios confinados.',
            'orden': 3
        },
        {
            'nombre': 'Primeros Auxilios y RCP',
            'descripcion': 'Técnicas de primeros auxilios y reanimación cardiopulmonar.',
            'orden': 4
        }
    ]
    
    for tema_data in temas_data:
        tema, created = Tema.objects.get_or_create(
            nombre=tema_data['nombre'],
            defaults=tema_data
        )
        
        if created:
            tema.oposiciones.add(oposicion)
            tema.alumnos_con_acceso.set(estudiantes)
            print(f"✅ Tema creado: {tema.nombre}")
            
            # Crear apartados para cada tema
            apartados_data = [
                {'nombre': f'Introducción a {tema.nombre}', 'orden': 1},
                {'nombre': f'Normativa y Regulación', 'orden': 2},
                {'nombre': f'Procedimientos Prácticos', 'orden': 3},
                {'nombre': f'Casos Prácticos', 'orden': 4}
            ]
            
            for apartado_data in apartados_data:
                apartado, created = Apartado.objects.get_or_create(
                    tema=tema,
                    nombre=apartado_data['nombre'],
                    defaults=apartado_data
                )
                
                if created:
                    # Crear preguntas de ejemplo para cada apartado
                    for i in range(1, 6):  # 5 preguntas por apartado
                        pregunta_data = {
                            'texto': f'¿Cuál es el procedimiento correcto en {apartado.nombre.lower()} - Pregunta {i}?',
                            'opcion_a': f'Opción A para pregunta {i}',
                            'opcion_b': f'Opción B para pregunta {i}',
                            'opcion_c': f'Opción C para pregunta {i}',
                            'respuesta_correcta': 'A',
                            'aclaracion': f'La respuesta correcta es A porque explica el procedimiento estándar según la normativa vigente.',
                            'activa': True
                        }
                        
                        Pregunta.objects.get_or_create(
                            apartado=apartado,
                            texto=pregunta_data['texto'],
                            defaults=pregunta_data
                        )
    
    print("✅ Base de datos configurada exitosamente!")
    print("\n" + "=" * 60)
    print("🎯 DATOS DE ACCESO:")
    print("Admin: admin / admin123")
    print("Estudiantes: jperez, mlopez, arojas, cgomez, dgarcia / estudiante123")
    print("=" * 60)

if __name__ == '__main__':
    setup_database()