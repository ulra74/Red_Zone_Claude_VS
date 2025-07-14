# core/management/commands/setup_academy.py

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from core.models import Categoria, Oposicion, Tema

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura la estructura inicial de Red Zone Academy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Crear un superusuario automáticamente',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔥 Configurando Red Zone Academy...'))
        
        # Crear directorios necesarios
        self.create_directories()
        
        # Crear categorías por defecto
        self.create_default_categories()
        
        # Crear contenido de ejemplo
        self.create_sample_content()
        
        # Crear superusuario si se solicita
        if options['create_superuser']:
            self.create_superuser()
        
        self.stdout.write(
            self.style.SUCCESS(
                '✅ Red Zone Academy configurada correctamente.\n'
                '   Puedes ejecutar el servidor con: python manage.py runserver\n'
                '   Accede al admin en: http://127.0.0.1:8000/admin/'
            )
        )

    def create_directories(self):
        """Crear directorios necesarios"""
        directories = [
            settings.MEDIA_ROOT,
            os.path.join(settings.MEDIA_ROOT, 'oposiciones'),
            os.path.join(settings.MEDIA_ROOT, 'temas'),
            os.path.join(settings.MEDIA_ROOT, 'preguntas', 'imagenes'),
            os.path.join(settings.MEDIA_ROOT, 'ejercicios', 'videos'),
            os.path.join(settings.MEDIA_ROOT, 'ejercicios', 'imagenes'),
            os.path.join(settings.BASE_DIR, 'logs'),
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                self.stdout.write(f'📁 Creado directorio: {directory}')

    def create_default_categories(self):
        """Crear categorías por defecto para exámenes"""
        categorias_default = [
            {
                'nombre': 'Legislación',
                'descripcion': 'Leyes y normativas relacionadas con bomberos',
                'color': '#dc3545',
                'orden': 1
            },
            {
                'nombre': 'Técnicas de Intervención',
                'descripcion': 'Procedimientos y técnicas de rescate',
                'color': '#fd7e14',
                'orden': 2
            },
            {
                'nombre': 'Primeros Auxilios',
                'descripcion': 'Atención médica de emergencia',
                'color': '#198754',
                'orden': 3
            },
            {
                'nombre': 'Prevención de Incendios',
                'descripcion': 'Sistemas de prevención y protección',
                'color': '#0d6efd',
                'orden': 4
            },
            {
                'nombre': 'Materiales y Equipos',
                'descripcion': 'Conocimiento de herramientas y equipamiento',
                'color': '#6f42c1',
                'orden': 5
            },
            {
                'nombre': 'Química del Fuego',
                'descripcion': 'Principios científicos de la combustión',
                'color': '#d63384',
                'orden': 6
            },
            {
                'nombre': 'Construcción',
                'descripcion': 'Elementos estructurales y materiales',
                'color': '#6c757d',
                'orden': 7
            },
            {
                'nombre': 'Comunicaciones',
                'descripcion': 'Sistemas de comunicación de emergencia',
                'color': '#20c997',
                'orden': 8
            }
        ]
        
        for cat_data in categorias_default:
            categoria, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'📚 Creada categoría: {categoria.nombre}')

    def create_sample_content(self):
        """Crear contenido de ejemplo"""
        # Crear oposición de ejemplo
        oposicion_bomberos, created = Oposicion.objects.get_or_create(
            nombre='Bombero/a - Ayuntamiento 2024',
            defaults={
                'descripcion': 'Oposición para el cuerpo de bomberos del ayuntamiento. '
                              'Incluye temas de legislación, técnicas de intervención, '
                              'primeros auxilios y preparación física.',
                'fecha_convocatoria': '2024-12-01'
            }
        )
        if created:
            self.stdout.write(f'🎯 Creada oposición: {oposicion_bomberos.nombre}')

        # Crear temas de ejemplo
        temas_ejemplo = [
            'Legislación de Emergencias',
            'Técnicas de Rescate Urbano',
            'Primeros Auxilios Avanzados',
            'Prevención de Incendios Forestales',
            'Preparación Física para Bomberos'
        ]
        
        for tema_nombre in temas_ejemplo:
            tema, created = Tema.objects.get_or_create(
                nombre=tema_nombre
            )
            if created:
                self.stdout.write(f'📖 Creado tema: {tema.nombre}')

    def create_superuser(self):
        """Crear superusuario por defecto"""
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@redzoneacademy.com',
                password='admin123',
                first_name='Administrador',
                last_name='RZA',
                user_type='admin'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    '👤 Superusuario creado:\n'
                    '   Usuario: admin\n'
                    '   Contraseña: admin123\n'
                    '   ⚠️  Recuerda cambiar la contraseña en producción'
                )
            )
        else:
            self.stdout.write('👤 Ya existe un superusuario')

    def create_sample_user(self):
        """Crear usuario estudiante de ejemplo"""
        if not User.objects.filter(username='estudiante').exists():
            estudiante = User.objects.create_user(
                username='estudiante',
                email='estudiante@redzoneacademy.com',
                password='estudiante123',
                first_name='Juan',
                last_name='Pérez',
                user_type='student'
            )
            
            # Asignar acceso a contenido
            for oposicion in Oposicion.objects.all():
                oposicion.alumnos_con_acceso.add(estudiante)
            
            for tema in Tema.objects.all():
                tema.alumnos_con_acceso.add(estudiante)
            
            self.stdout.write(
                self.style.SUCCESS(
                    '🎓 Usuario estudiante creado:\n'
                    '   Usuario: estudiante\n'
                    '   Contraseña: estudiante123'
                )
            )