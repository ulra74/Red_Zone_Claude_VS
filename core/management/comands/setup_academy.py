# core/management/commands/setup_academy.py - ACTUALIZADO

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from core.models import Categoria, Oposicion, Tema, TemaOposicion

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura la estructura inicial de Red Zone Academy con relaciones Tema-Oposición'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Crear un superusuario automáticamente',
        )
        parser.add_argument(
            '--with-demo-data',
            action='store_true',
            help='Crear datos de demostración completos',
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
        
        # Crear datos de demostración si se solicita
        if options['with_demo_data']:
            self.create_demo_data()
        
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
        
        # Crear oposiciones de ejemplo
        oposiciones_ejemplo = [
            {
                'nombre': 'Bombero/a - Ayuntamiento Madrid 2024',
                'descripcion': 'Oposición para el cuerpo de bomberos del Ayuntamiento de Madrid. '
                              'Incluye temas de legislación, técnicas de intervención, '
                              'primeros auxilios y preparación física.',
                'fecha_convocatoria': '2024-12-01'
            },
            {
                'nombre': 'Bombero/a - Generalitat Catalunya 2024',
                'descripcion': 'Convocatoria para bomberos de la Generalitat de Catalunya. '
                              'Especialización en incendios forestales y rescate en montaña.',
                'fecha_convocatoria': '2024-11-15'
            },
            {
                'nombre': 'Bombero Conductor - Diputación Valencia 2024',
                'descripcion': 'Oposición específica para bomberos conductores. '
                              'Incluye conocimientos de conducción de vehículos pesados.',
                'fecha_convocatoria': '2025-01-20'
            }
        ]
        
        oposiciones_creadas = []
        for op_data in oposiciones_ejemplo:
            oposicion, created = Oposicion.objects.get_or_create(
                nombre=op_data['nombre'],
                defaults=op_data
            )
            if created:
                self.stdout.write(f'🎯 Creada oposición: {oposicion.nombre}')
            oposiciones_creadas.append(oposicion)

        # Crear temas de ejemplo con descripción
        temas_ejemplo = [
            {
                'nombre': 'Legislación de Emergencias',
                'descripcion': 'Marco legal de los servicios de emergencia, normativas autonómicas y municipales.',
                'orden': 1,
                'es_obligatorio': True,
                'peso_evaluacion': 8
            },
            {
                'nombre': 'Técnicas de Rescate Urbano',
                'descripcion': 'Procedimientos y técnicas para rescates en entornos urbanos.',
                'orden': 2,
                'es_obligatorio': True,
                'peso_evaluacion': 10
            },
            {
                'nombre': 'Primeros Auxilios Avanzados',
                'descripcion': 'Atención sanitaria de emergencia y soporte vital básico.',
                'orden': 3,
                'es_obligatorio': True,
                'peso_evaluacion': 9
            },
            {
                'nombre': 'Prevención de Incendios Forestales',
                'descripcion': 'Estrategias de prevención y extinción de incendios en entornos naturales.',
                'orden': 4,
                'es_obligatorio': True,
                'peso_evaluacion': 8
            },
            {
                'nombre': 'Preparación Física para Bomberos',
                'descripcion': 'Entrenamiento físico específico y pruebas de aptitud física.',
                'orden': 5,
                'es_obligatorio': True,
                'peso_evaluacion': 7
            },
            {
                'nombre': 'Química del Fuego',
                'descripcion': 'Principios científicos de la combustión, tipos de fuego y agentes extintores.',
                'orden': 6,
                'es_obligatorio': True,
                'peso_evaluacion': 6
            },
            {
                'nombre': 'Materiales y Equipos',
                'descripcion': 'Conocimiento de herramientas, maquinaria y equipos de protección.',
                'orden': 7,
                'es_obligatorio': True,
                'peso_evaluacion': 7
            },
            {
                'nombre': 'Rescate en Altura',
                'descripcion': 'Técnicas específicas para rescates en edificios altos y estructuras.',
                'orden': 8,
                'es_obligatorio': False,
                'peso_evaluacion': 5
            },
            {
                'nombre': 'Rescate Acuático',
                'descripcion': 'Procedimientos de rescate en medios acuáticos.',
                'orden': 9,
                'es_obligatorio': False,
                'peso_evaluacion': 4
            },
            {
                'nombre': 'Comunicaciones de Emergencia',
                'descripcion': 'Sistemas de comunicación y coordinación en emergencias.',
                'orden': 10,
                'es_obligatorio': True,
                'peso_evaluacion': 6
            }
        ]
        
        temas_creados = []
        for tema_data in temas_ejemplo:
            tema, created = Tema.objects.get_or_create(
                nombre=tema_data['nombre'],
                defaults=tema_data
            )
            if created:
                self.stdout.write(f'📖 Creado tema: {tema.nombre}')
            temas_creados.append(tema)
        
        return oposiciones_creadas, temas_creados

    def create_tema_oposicion_relations(self):
        """Crear relaciones entre temas y oposiciones"""
        self.stdout.write('🔗 Creando relaciones tema-oposición...')
        
        try:
            # Obtener oposiciones y temas
            oposicion_madrid = Oposicion.objects.filter(nombre__icontains='Madrid').first()
            oposicion_catalunya = Oposicion.objects.filter(nombre__icontains='Catalunya').first()
            oposicion_valencia = Oposicion.objects.filter(nombre__icontains='Valencia').first()
            
            # Temas comunes a todas las oposiciones
            temas_comunes = [
                'Legislación de Emergencias',
                'Técnicas de Rescate Urbano', 
                'Primeros Auxilios Avanzados',
                'Preparación Física para Bomberos',
                'Química del Fuego',
                'Materiales y Equipos',
                'Comunicaciones de Emergencia'
            ]
            
            # Asignar temas comunes a todas las oposiciones
            for oposicion in [oposicion_madrid, oposicion_catalunya, oposicion_valencia]:
                if oposicion:
                    for nombre_tema in temas_comunes:
                        tema = Tema.objects.filter(nombre=nombre_tema).first()
                        if tema:
                            oposicion.temas.add(tema)
                    
                    self.stdout.write(f'   ✅ Asignados {len(temas_comunes)} temas comunes a {oposicion.nombre}')
            
            # Temas específicos para Catalunya (incendios forestales)
            if oposicion_catalunya:
                tema_forestal = Tema.objects.filter(nombre='Prevención de Incendios Forestales').first()
                tema_altura = Tema.objects.filter(nombre='Rescate en Altura').first()
                if tema_forestal:
                    oposicion_catalunya.temas.add(tema_forestal)
                if tema_altura:
                    oposicion_catalunya.temas.add(tema_altura)
                self.stdout.write(f'   ✅ Asignados temas específicos a {oposicion_catalunya.nombre}')
            
            # Temas específicos para Valencia (rescate acuático)
            if oposicion_valencia:
                tema_acuatico = Tema.objects.filter(nombre='Rescate Acuático').first()
                if tema_acuatico:
                    oposicion_valencia.temas.add(tema_acuatico)
                self.stdout.write(f'   ✅ Asignados temas específicos a {oposicion_valencia.nombre}')
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Error creando relaciones: {e}'))

    def create_demo_data(self):
        """Crear datos de demostración adicionales"""
        self.stdout.write('🎭 Creando datos de demostración...')
        
        # Crear usuario estudiante de ejemplo
        if not User.objects.filter(username='estudiante').exists():
            estudiante = User.objects.create_user(
                username='estudiante',
                email='estudiante@redzoneacademy.com',
                password='estudiante123',
                first_name='Juan',
                last_name='Pérez',
                user_type='student'
            )
            
            # Asignar acceso a todas las oposiciones y temas
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
    
    def show_relations_summary(self):
        """Mostrar resumen de las relaciones creadas"""
        self.stdout.write('\n📊 RESUMEN DE RELACIONES:')
        self.stdout.write('=' * 50)
        
        for oposicion in Oposicion.objects.all():
            self.stdout.write(f'\n🎯 {oposicion.nombre}:')
            temas = oposicion.temas.all()
            for tema in temas:
                self.stdout.write(f'   📖 {tema.nombre} (Orden: {tema.orden}, Obligatorio: {"Sí" if tema.es_obligatorio else "No"})')
            
            if not temas:
                self.stdout.write('   (Sin temas asignados)')
        
        self.stdout.write(f'\n📈 ESTADÍSTICAS:')
        self.stdout.write(f'   Oposiciones: {Oposicion.objects.count()}')
        self.stdout.write(f'   Temas: {Tema.objects.count()}')
        self.stdout.write(f'   Categorías: {Categoria.objects.count()}')
        
        # Mostrar relaciones many-to-many
        total_relaciones = 0
        for oposicion in Oposicion.objects.all():
            total_relaciones += oposicion.temas.count()
        self.stdout.write(f'   Relaciones Tema-Oposición: {total_relaciones}')
        
        self.stdout.write('\n✅ Configuración completada exitosamente!')
        
        # Llamar al resumen al final del comando
        self.show_relations_summary()