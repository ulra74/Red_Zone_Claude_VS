# core/management/commands/setup_academy_simple.py - ACTUALIZADO sin peso_evaluacion y es_obligatorio

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from core.models import Categoria, Oposicion, Tema, TemaOposicion

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura la estructura inicial de Red Zone Academy (simplificada)'

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
        
        # Crear relaciones entre temas y oposiciones
        self.create_tema_oposicion_relations()
        
        # Crear superusuario si se solicita
        if options['create_superuser']:
            self.create_superuser()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Red Zone Academy configurada exitosamente!')
        )

    def create_directories(self):
        """Crear directorios necesarios"""
        directories = [
            'media/oposiciones',
            'media/temas',
            'media/preguntas/imagenes',
            'media/ejercicios/videos',
            'media/ejercicios/imagenes',
            'logs',
            'static/uploads'
        ]
        
        for directory in directories:
            full_path = os.path.join(settings.BASE_DIR, directory)
            os.makedirs(full_path, exist_ok=True)
            self.stdout.write(f'📁 Creado directorio: {directory}')

    def create_default_categories(self):
        """Crear categorías por defecto"""
        categorias = [
            {
                'nombre': 'Legislación y Normativa',
                'descripcion': 'Leyes, decretos y normativas relacionadas con el servicio de bomberos',
                'color': '#dc3545',
                'orden': 1
            },
            {
                'nombre': 'Técnicas de Intervención',
                'descripcion': 'Procedimientos y técnicas operativas',
                'color': '#fd7e14',
                'orden': 2
            },
            {
                'nombre': 'Primeros Auxilios',
                'descripcion': 'Atención sanitaria básica y primeros auxilios',
                'color': '#198754',
                'orden': 3
            },
            {
                'nombre': 'Prevención de Incendios',
                'descripcion': 'Medidas preventivas y sistemas de protección',
                'color': '#0d6efd',
                'orden': 4
            },
            {
                'nombre': 'Materiales y Equipos',
                'descripcion': 'Conocimiento de herramientas y equipos de trabajo',
                'color': '#6610f2',
                'orden': 5
            }
        ]
        
        self.stdout.write('\n📚 Creando categorías...')
        for cat_data in categorias:
            categoria, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            status = '✅ Creada' if created else '🔄 Actualizada'
            self.stdout.write(f'   {status}: {categoria.nombre}')

    def create_sample_content(self):
        """Crear contenido de ejemplo"""
        self.stdout.write('\n🎯 Creando oposiciones de ejemplo...')
        
        # Crear oposiciones
        oposiciones_data = [
            {
                'nombre': 'Bombero Generalista 2024',
                'descripcion': 'Oposición para bomberos con conocimientos generales',
                'fecha_convocatoria': '2024-06-15'
            },
            {
                'nombre': 'Bombero Especialista - Rescate',
                'descripcion': 'Especialización en técnicas de rescate y salvamento',
                'fecha_convocatoria': '2024-09-20'
            },
            {
                'nombre': 'Cabo de Bomberos',
                'descripcion': 'Promoción a cabo con responsabilidades de coordinación',
                'fecha_convocatoria': '2024-11-30'
            }
        ]
        
        for opos_data in oposiciones_data:
            oposicion, created = Oposicion.objects.get_or_create(
                nombre=opos_data['nombre'],
                defaults=opos_data
            )
            status = '✅ Creada' if created else '🔄 Actualizada'
            self.stdout.write(f'   {status}: {oposicion.nombre}')
        
        # Crear temas
        self.stdout.write('\n📖 Creando temas de ejemplo...')
        
        temas_data = [
            {
                'nombre': 'Legislación Básica de Bomberos',
                'descripcion': 'Conocimientos fundamentales sobre la normativa que regula el servicio de bomberos',
                'orden': 1
            },
            {
                'nombre': 'Técnicas de Extinción',
                'descripcion': 'Métodos y procedimientos para la extinción de incendios',
                'orden': 2
            },
            {
                'nombre': 'Primeros Auxilios Básicos',
                'descripcion': 'Atención sanitaria inicial y soporte vital básico',
                'orden': 3
            },
            {
                'nombre': 'Rescate en Altura',
                'descripcion': 'Técnicas específicas para rescates en espacios elevados',
                'orden': 4
            },
            {
                'nombre': 'Materiales y Herramientas',
                'descripcion': 'Conocimiento del equipamiento básico del bombero',
                'orden': 5
            },
            {
                'nombre': 'Comunicaciones y Coordinación',
                'descripcion': 'Sistemas de comunicación y protocolos de coordinación',
                'orden': 6
            },
            {
                'nombre': 'Prevención de Riesgos',
                'descripción': 'Identificación y prevención de situaciones de riesgo',
                'orden': 7
            },
            {
                'nombre': 'Rescate Acuático',
                'descripcion': 'Técnicas específicas para emergencias en medio acuático',
                'orden': 8
            },
            {
                'nombre': 'Hazmat - Materiales Peligrosos',
                'descripcion': 'Intervención en emergencias con materiales peligrosos',
                'orden': 9
            },
            {
                'nombre': 'Liderazgo y Gestión de Equipos',
                'descripcion': 'Habilidades de coordinación y liderazgo para cabos',
                'orden': 10
            }
        ]
        
        for tema_data in temas_data:
            tema, created = Tema.objects.get_or_create(
                nombre=tema_data['nombre'],
                defaults=tema_data
            )
            status = '✅ Creado' if created else '🔄 Actualizado'
            self.stdout.write(f'   {status}: {tema.nombre}')

    def create_tema_oposicion_relations(self):
        """Crear relaciones entre temas y oposiciones"""
        self.stdout.write('\n🔗 Creando relaciones tema-oposición...')
        
        # Obtener oposiciones y temas
        try:
            bombero_generalista = Oposicion.objects.get(nombre__icontains='Bombero Generalista')
            bombero_especialista = Oposicion.objects.get(nombre__icontains='Especialista')
            cabo_bomberos = Oposicion.objects.get(nombre__icontains='Cabo')
        except Oposicion.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ No se encontraron las oposiciones necesarias'))
            return
        
        # Relaciones para Bombero Generalista (temas básicos)
        temas_generalista = [
            'Legislación Básica de Bomberos',
            'Técnicas de Extinción',
            'Primeros Auxilios Básicos',
            'Materiales y Herramientas',
            'Comunicaciones y Coordinación',
            'Prevención de Riesgos'
        ]
        
        self.assign_temas_to_oposicion(bombero_generalista, temas_generalista)
        
        # Relaciones para Bombero Especialista (temas avanzados)
        temas_especialista = [
            'Rescate en Altura',
            'Rescate Acuático',
            'Hazmat - Materiales Peligrosos',
            'Técnicas de Extinción',
            'Primeros Auxilios Básicos'
        ]
        
        self.assign_temas_to_oposicion(bombero_especialista, temas_especialista)
        
        # Relaciones para Cabo (temas de liderazgo + técnicos)
        temas_cabo = [
            'Liderazgo y Gestión de Equipos',
            'Legislación Básica de Bomberos',
            'Comunicaciones y Coordinación',
            'Prevención de Riesgos',
            'Técnicas de Extinción'
        ]
        
        self.assign_temas_to_oposicion(cabo_bomberos, temas_cabo)

    def assign_temas_to_oposicion(self, oposicion, tema_names):
        """Asignar temas a una oposición específica"""
        self.stdout.write(f'\n   📋 Asignando temas a: {oposicion.nombre}')
        
        for i, tema_name in enumerate(tema_names, 1):
            try:
                tema = Tema.objects.get(nombre=tema_name)
                
                # Crear relación many-to-many
                oposicion.temas.add(tema)
                
                # Crear registro en tabla intermedia con datos adicionales
                tema_oposicion, created = TemaOposicion.objects.get_or_create(
                    tema=tema,
                    oposicion=oposicion,
                    defaults={
                        'orden_en_oposicion': i,
                        'es_obligatorio_en_oposicion': True,
                        'peso_en_oposicion': 1
                    }
                )
                
                status = '✅ Asignado' if created else '🔄 Actualizado'
                self.stdout.write(f'      {status}: {tema.nombre} (Orden: {i})')
                
            except Tema.DoesNotExist:
                self.stdout.write(f'      ❌ No se encontró el tema: {tema_name}')

    def create_superuser(self):
        """Crear superusuario por defecto"""
        self.stdout.write('\n👤 Creando superusuario...')
        
        if not User.objects.filter(is_superuser=True).exists():
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
            
            self.stdout.write('✅ Superusuario creado: admin / admin123')
        else:
            self.stdout.write('🔄 Superusuario ya existe')

    def show_summary(self):
        """Mostrar resumen del contenido creado"""
        self.stdout.write('\n📊 RESUMEN DE CONTENIDO CREADO:')
        self.stdout.write(f'   📚 Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'   🎯 Oposiciones: {Oposicion.objects.count()}')
        self.stdout.write(f'   📖 Temas: {Tema.objects.count()}')
        self.stdout.write(f'   🔗 Relaciones Tema-Oposición: {TemaOposicion.objects.count()}')
        
        # Mostrar detalle de oposiciones
        self.stdout.write('\n🎯 OPOSICIONES CREADAS:')
        for oposicion in Oposicion.objects.all():
            self.stdout.write(f'   🔥 {oposicion.nombre}')
            for tema in oposicion.temas.all():
                self.stdout.write(f'      📖 {tema.nombre} (Orden: {tema.orden})')