from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Oposicion, Tema, Apartado, Pregunta, Respuesta
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Genera datos de ejemplo para temas, apartados y preguntas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos existentes antes de generar nuevos',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando datos existentes...')
            Respuesta.objects.all().delete()
            Pregunta.objects.all().delete()
            Apartado.objects.all().delete()
            Tema.objects.all().delete()
            Oposicion.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Datos eliminados correctamente'))

        # Crear oposiciones
        self.stdout.write('Creando oposiciones...')
        oposiciones = self.create_oposiciones()
        
        # Crear temas
        self.stdout.write('Creando temas...')
        temas = self.create_temas(oposiciones)
        
        # Crear apartados
        self.stdout.write('Creando apartados...')
        apartados = self.create_apartados(temas)
        
        # Crear preguntas y respuestas
        self.stdout.write('Creando preguntas y respuestas...')
        self.create_preguntas_y_respuestas(apartados)
        
        # Asignar accesos a estudiantes
        self.stdout.write('Asignando accesos a estudiantes...')
        self.assign_student_access(oposiciones, temas)
        
        self.stdout.write(self.style.SUCCESS('Datos de ejemplo generados exitosamente'))

    def create_oposiciones(self):
        oposiciones_data = [
            {
                'nombre': 'Bombero Conductor',
                'descripcion': 'Oposición para bombero conductor de vehículos de emergencia',
                'fecha_convocatoria': date.today() + timedelta(days=60)
            },
            {
                'nombre': 'Bombero Especialista',
                'descripcion': 'Oposición para bombero especialista en rescate y salvamento',
                'fecha_convocatoria': date.today() + timedelta(days=90)
            },
            {
                'nombre': 'Suboficial de Bomberos',
                'descripcion': 'Oposición para acceso a suboficial del cuerpo de bomberos',
                'fecha_convocatoria': date.today() + timedelta(days=120)
            }
        ]
        
        oposiciones = []
        for data in oposiciones_data:
            oposicion, created = Oposicion.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            oposiciones.append(oposicion)
            if created:
                self.stdout.write(f'  - Creada: {oposicion.nombre}')
        
        return oposiciones

    def create_temas(self, oposiciones):
        temas_data = [
            {
                'nombre': 'Prevención de Incendios',
                'descripcion': 'Medidas preventivas y sistemas de detección de incendios',
                'orden': 1
            },
            {
                'nombre': 'Extinción de Incendios',
                'descripcion': 'Técnicas y equipos para la extinción de diferentes tipos de incendios',
                'orden': 2
            },
            {
                'nombre': 'Rescate y Salvamento',
                'descripcion': 'Técnicas de rescate en emergencias y catástrofes',
                'orden': 3
            },
            {
                'nombre': 'Primeros Auxilios',
                'descripcion': 'Atención médica básica en emergencias',
                'orden': 4
            },
            {
                'nombre': 'Legislación de Emergencias',
                'descripcion': 'Marco legal y normativo del servicio de bomberos',
                'orden': 5
            },
            {
                'nombre': 'Materiales Peligrosos',
                'descripcion': 'Identificación y manejo de sustancias peligrosas',
                'orden': 6
            },
            {
                'nombre': 'Comunicaciones de Emergencia',
                'descripcion': 'Sistemas de comunicación y coordinación en emergencias',
                'orden': 7
            },
            {
                'nombre': 'Construcción y Estructuras',
                'descripcion': 'Conocimientos sobre construcción para intervenciones',
                'orden': 8
            }
        ]
        
        temas = []
        for data in temas_data:
            tema, created = Tema.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            
            # Asignar temas a oposiciones (algunos temas a múltiples oposiciones)
            if tema.nombre in ['Prevención de Incendios', 'Extinción de Incendios', 'Primeros Auxilios']:
                tema.oposiciones.add(*oposiciones)  # Todas las oposiciones
            elif tema.nombre in ['Rescate y Salvamento', 'Materiales Peligrosos']:
                tema.oposiciones.add(oposiciones[1], oposiciones[2])  # Especialista y Suboficial
            elif tema.nombre in ['Legislación de Emergencias', 'Comunicaciones de Emergencia']:
                tema.oposiciones.add(oposiciones[2])  # Solo Suboficial
            else:
                tema.oposiciones.add(random.choice(oposiciones))  # Asignación aleatoria
            
            temas.append(tema)
            if created:
                self.stdout.write(f'  - Creado: {tema.nombre}')
        
        return temas

    def create_apartados(self, temas):
        apartados_data = {
            'Prevención de Incendios': [
                'Sistemas de detección automática',
                'Sistemas de extinción fijos',
                'Normativa de prevención',
                'Inspección de instalaciones'
            ],
            'Extinción de Incendios': [
                'Teoría del fuego',
                'Agentes extintores',
                'Equipos de extinción',
                'Técnicas de extinción'
            ],
            'Rescate y Salvamento': [
                'Rescate en altura',
                'Rescate acuático',
                'Rescate en espacios confinados',
                'Rescate en accidentes de tráfico'
            ],
            'Primeros Auxilios': [
                'Evaluación primaria',
                'Reanimación cardiopulmonar',
                'Tratamiento de heridas',
                'Inmovilización y transporte'
            ],
            'Legislación de Emergencias': [
                'Ley de protección civil',
                'Normativa de seguridad',
                'Responsabilidades legales',
                'Procedimientos administrativos'
            ],
            'Materiales Peligrosos': [
                'Identificación de sustancias',
                'Equipos de protección',
                'Procedimientos de actuación',
                'Descontaminación'
            ],
            'Comunicaciones de Emergencia': [
                'Sistemas de radio',
                'Protocolos de comunicación',
                'Coordinación con otros servicios',
                'Tecnologías de localización'
            ],
            'Construcción y Estructuras': [
                'Materiales de construcción',
                'Comportamiento estructural',
                'Riesgos de colapso',
                'Técnicas de apuntalamiento'
            ]
        }
        
        apartados = []
        for tema in temas:
            if tema.nombre in apartados_data:
                for i, apartado_nombre in enumerate(apartados_data[tema.nombre], 1):
                    apartado, created = Apartado.objects.get_or_create(
                        tema=tema,
                        nombre=apartado_nombre,
                        defaults={
                            'descripcion': f'Apartado sobre {apartado_nombre.lower()}',
                            'orden': i
                        }
                    )
                    apartados.append(apartado)
                    if created:
                        self.stdout.write(f'    - Creado: {tema.nombre} > {apartado.nombre}')
        
        return apartados

    def create_preguntas_y_respuestas(self, apartados):
        # Plantillas de preguntas por tema
        preguntas_templates = {
            'Prevención de Incendios': [
                {
                    'enunciado': '¿Cuál es la temperatura de autoignición del papel?',
                    'respuesta_correcta': 'Aproximadamente 230°C',
                    'respuestas_incorrectas': ['150°C', '300°C', '400°C'],
                    'aclaracion': 'La temperatura de autoignición es la temperatura mínima a la que una sustancia se inflama sin necesidad de una fuente externa de ignición.'
                },
                {
                    'enunciado': '¿Qué tipo de detector es más eficaz para fuegos lentos con mucho humo?',
                    'respuesta_correcta': 'Detector óptico de humos',
                    'respuestas_incorrectas': ['Detector térmico', 'Detector de llama', 'Detector de gases'],
                    'aclaracion': 'Los detectores ópticos son especialmente sensibles a partículas de humo visibles.'
                },
                {
                    'enunciado': '¿Cuál es la distancia mínima entre hidrantes según la normativa?',
                    'respuesta_correcta': '200 metros',
                    'respuestas_incorrectas': ['100 metros', '300 metros', '500 metros'],
                    'aclaracion': 'La distancia máxima entre hidrantes no debe superar los 200 metros en zonas urbanas.'
                }
            ],
            'Extinción de Incendios': [
                {
                    'enunciado': '¿Qué agente extintor NO se debe usar en fuegos de clase D?',
                    'respuesta_correcta': 'Agua',
                    'respuestas_incorrectas': ['Polvo especial', 'Arena seca', 'Grafito'],
                    'aclaracion': 'El agua reacciona violentamente con metales ardiendo, aumentando el peligro.'
                },
                {
                    'enunciado': '¿Cuál es el mecanismo de extinción del CO2?',
                    'respuesta_correcta': 'Sofocación',
                    'respuestas_incorrectas': ['Enfriamiento', 'Inhibición', 'Emulsión'],
                    'aclaracion': 'El CO2 desplaza el oxígeno, creando una atmósfera inerte que sofoca el fuego.'
                },
                {
                    'enunciado': '¿Qué presión debe tener una línea de 45mm para ser efectiva?',
                    'respuesta_correcta': '7 bares',
                    'respuestas_incorrectas': ['3 bares', '5 bares', '10 bares'],
                    'aclaracion': 'La presión óptima para líneas de 45mm es de 7 bares para garantizar alcance y caudal.'
                }
            ],
            'Rescate y Salvamento': [
                {
                    'enunciado': '¿Cuál es la resistencia mínima de una cuerda de rescate?',
                    'respuesta_correcta': '22 kN',
                    'respuestas_incorrectas': ['15 kN', '18 kN', '25 kN'],
                    'aclaracion': 'Las cuerdas de rescate deben tener una resistencia mínima de 22 kN según normativa EN 1891.'
                },
                {
                    'enunciado': '¿Qué técnica se usa para rescate en espacios confinados?',
                    'respuesta_correcta': 'Trípode y polipasto',
                    'respuestas_incorrectas': ['Escalera de gancho', 'Plataforma elevadora', 'Cuerda directa'],
                    'aclaracion': 'El trípode proporciona estabilidad y el polipasto permite izar con ventaja mecánica.'
                },
                {
                    'enunciado': '¿Cuál es la primera acción en rescate acuático?',
                    'respuesta_correcta': 'Asegurar la propia seguridad',
                    'respuestas_incorrectas': ['Lanzar salvavidas', 'Entrar al agua', 'Llamar a la víctima'],
                    'aclaracion': 'La regla fundamental es no convertirse en otra víctima. Siempre evaluar la seguridad primero.'
                }
            ],
            'Primeros Auxilios': [
                {
                    'enunciado': '¿Cuál es la frecuencia correcta de compresiones en RCP?',
                    'respuesta_correcta': '100-120 por minuto',
                    'respuestas_incorrectas': ['80-100 por minuto', '60-80 por minuto', '120-140 por minuto'],
                    'aclaracion': 'Las guías internacionales establecen 100-120 compresiones por minuto para RCP efectiva.'
                },
                {
                    'enunciado': '¿Qué profundidad deben tener las compresiones en adultos?',
                    'respuesta_correcta': '5-6 centímetros',
                    'respuestas_incorrectas': ['3-4 centímetros', '2-3 centímetros', '7-8 centímetros'],
                    'aclaracion': 'La profundidad de 5-6 cm es necesaria para generar flujo sanguíneo efectivo.'
                },
                {
                    'enunciado': '¿Cuál es la posición de seguridad para una persona inconsciente?',
                    'respuesta_correcta': 'Posición lateral de seguridad',
                    'respuestas_incorrectas': ['Boca arriba', 'Boca abajo', 'Sentado'],
                    'aclaracion': 'La posición lateral previene la aspiración y mantiene la vía aérea permeable.'
                }
            ]
        }
        
        contador_preguntas = 0
        for apartado in apartados:
            tema_nombre = apartado.tema.nombre
            
            # Buscar plantillas para este tema
            templates = preguntas_templates.get(tema_nombre, [])
            
            # Si no hay plantillas específicas, crear preguntas genéricas
            if not templates:
                templates = [
                    {
                        'enunciado': f'¿Cuál es el procedimiento básico en {apartado.nombre.lower()}?',
                        'respuesta_correcta': f'Seguir protocolos establecidos para {apartado.nombre.lower()}',
                        'respuestas_incorrectas': ['Actuar sin protocolo', 'Esperar órdenes', 'Improvisar'],
                        'aclaracion': f'Es fundamental seguir los protocolos establecidos en {apartado.nombre.lower()}.'
                    },
                    {
                        'enunciado': f'¿Qué equipo es esencial para {apartado.nombre.lower()}?',
                        'respuesta_correcta': f'Equipo especializado en {apartado.nombre.lower()}',
                        'respuestas_incorrectas': ['Equipo básico', 'Sin equipo especial', 'Equipo improvisado'],
                        'aclaracion': f'El equipo especializado es crucial para la seguridad en {apartado.nombre.lower()}.'
                    }
                ]
            
            # Crear preguntas para este apartado
            preguntas_apartado = templates * 2  # Duplicar para tener más preguntas
            
            for i, pregunta_data in enumerate(preguntas_apartado[:5]):  # Máximo 5 preguntas por apartado
                pregunta, created = Pregunta.objects.get_or_create(
                    apartado=apartado,
                    enunciado=pregunta_data['enunciado'],
                    defaults={
                        'texto_aclaratorio': pregunta_data.get('aclaracion', ''),
                        'veces_preguntada': random.randint(10, 50),
                        'veces_acertada': random.randint(5, 40)
                    }
                )
                
                if created:
                    contador_preguntas += 1
                    
                    # Crear respuestas
                    # Respuesta correcta
                    Respuesta.objects.create(
                        pregunta=pregunta,
                        texto=pregunta_data['respuesta_correcta'],
                        es_correcta=True
                    )
                    
                    # Respuestas incorrectas
                    for respuesta_incorrecta in pregunta_data['respuestas_incorrectas']:
                        Respuesta.objects.create(
                            pregunta=pregunta,
                            texto=respuesta_incorrecta,
                            es_correcta=False
                        )
                    
                    self.stdout.write(f'      - Creada pregunta: {pregunta.enunciado[:50]}...')
        
        self.stdout.write(f'Total de preguntas creadas: {contador_preguntas}')

    def assign_student_access(self, oposiciones, temas):
        # Obtener estudiantes existentes
        estudiantes = User.objects.filter(user_type='student')
        
        if not estudiantes.exists():
            self.stdout.write(self.style.WARNING('No hay estudiantes en el sistema. Creando usuario de prueba...'))
            estudiante = User.objects.create_user(
                username='estudiante1',
                email='estudiante1@ejemplo.com',
                password='password123',
                user_type='student',
                first_name='Juan',
                last_name='Pérez'
            )
            estudiantes = [estudiante]
        
        # Asignar acceso a oposiciones y temas
        for estudiante in estudiantes:
            # Asignar a todas las oposiciones
            for oposicion in oposiciones:
                oposicion.alumnos_con_acceso.add(estudiante)
            
            # Asignar a todos los temas
            for tema in temas:
                tema.alumnos_con_acceso.add(estudiante)
        
        self.stdout.write(f'Acceso asignado a {len(estudiantes)} estudiantes')