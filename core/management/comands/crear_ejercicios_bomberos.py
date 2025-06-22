from django.core.management.base import BaseCommand
from core.models_preparacion_fisica import EjercicioFisico
from datetime import timedelta


class Command(BaseCommand):
    help = 'Crea ejercicios físicos estándar para bomberos'

    def handle(self, *args, **options):
        ejercicios_bomberos = [
            {
                'nombre': 'Carrera de 100 metros lisos',
                'categoria': 'velocidad',
                'descripcion': 'Sprint de 100 metros en pista de atletismo',
                'instrucciones': 'Salida en posición de pie. Correr la distancia lo más rápido posible.',
                'tiempo_objetivo_hombre': timedelta(seconds=16),
                'tiempo_objetivo_mujer': timedelta(seconds=18),
                'baremo_excelente': '< 14 seg (H) / < 16 seg (M)',
                'baremo_bueno': '14-15 seg (H) / 16-17 seg (M)',
                'baremo_aceptable': '15-16 seg (H) / 17-18 seg (M)',
                'baremo_insuficiente': '> 16 seg (H) / > 18 seg (M)',
                'es_obligatorio_bomberos': True,
                'orden': 1
            },
            {
                'nombre': 'Carrera de resistencia 1000m',
                'categoria': 'resistencia',
                'descripcion': 'Carrera de resistencia de 1000 metros',
                'instrucciones': 'Mantener un ritmo constante durante toda la distancia.',
                'tiempo_objetivo_hombre': timedelta(minutes=4, seconds=30),
                'tiempo_objetivo_mujer': timedelta(minutes=5),
                'baremo_excelente': '< 3:45 (H) / < 4:15 (M)',
                'baremo_bueno': '3:45-4:15 (H) / 4:15-4:45 (M)',
                'baremo_aceptable': '4:15-4:30 (H) / 4:45-5:00 (M)',
                'baremo_insuficiente': '> 4:30 (H) / > 5:00 (M)',
                'es_obligatorio_bomberos': True,
                'orden': 2
            },
            {
                'nombre': 'Natación 50 metros',
                'categoria': 'natacion',
                'descripcion': 'Natación libre de 50 metros en piscina',
                'instrucciones': 'Estilo libre. Salida desde dentro del agua.',
                'tiempo_objetivo_hombre': timedelta(seconds=50),
                'tiempo_objetivo_mujer': timedelta(seconds=60),
                'baremo_excelente': '< 40 seg (H) / < 50 seg (M)',
                'baremo_bueno': '40-45 seg (H) / 50-55 seg (M)',
                'baremo_aceptable': '45-50 seg (H) / 55-60 seg (M)',
                'baremo_insuficiente': '> 50 seg (H) / > 60 seg (M)',
                'es_obligatorio_bomberos': True,
                'orden': 3
            },
            {
                'nombre': 'Subida de escalera con peso',
                'categoria': 'fuerza',
                'descripcion': 'Subida de torre de prácticas con lastre de 15kg',
                'instrucciones': 'Subir 5 plantas con mochila de 15kg. No correr, mantener ritmo constante.',
                'tiempo_objetivo_hombre': timedelta(minutes=2),
                'tiempo_objetivo_mujer': timedelta(minutes=2, seconds=30),
                'peso_objetivo': 15.0,
                'baremo_excelente': '< 1:30 (H) / < 2:00 (M)',
                'baremo_bueno': '1:30-1:45 (H) / 2:00-2:15 (M)',
                'baremo_aceptable': '1:45-2:00 (H) / 2:15-2:30 (M)',
                'baremo_insuficiente': '> 2:00 (H) / > 2:30 (M)',
                'es_obligatorio_bomberos': True,
                'orden': 4
            },
            {
                'nombre': 'Dominadas',
                'categoria': 'fuerza',
                'descripcion': 'Máximo número de dominadas sin tiempo límite',
                'instrucciones': 'Agarre prono, brazos completamente extendidos. Barbilla por encima de la barra.',
                'repeticiones_objetivo': 10,
                'baremo_excelente': '> 15 reps (H) / > 8 reps (M)',
                'baremo_bueno': '12-15 reps (H) / 6-8 reps (M)',
                'baremo_aceptable': '8-12 reps (H) / 4-6 reps (M)',
                'baremo_insuficiente': '< 8 reps (H) / < 4 reps (M)',
                'es_obligatorio_bomberos': True,
                'orden': 5
            },
            {
                'nombre': 'Flexiones de pecho',
                'categoria': 'fuerza',
                'descripcion': 'Máximo número de flexiones en 2 minutos',
                'instrucciones': 'Posición de plancha. Bajar hasta tocar pecho al suelo, subir hasta brazos extendidos.',
                'repeticiones_objetivo': 25,
                'tiempo_objetivo_hombre': timedelta(minutes=2),
                'tiempo_objetivo_mujer': timedelta(minutes=2),
                'baremo_excelente': '> 35 reps (H) / > 20 reps (M)',
                'baremo_bueno': '30-35 reps (H) / 15-20 reps (M)',
                'baremo_aceptable': '25-30 reps (H) / 10-15 reps (M)',
                'baremo_insuficiente': '< 25 reps (H) / < 10 reps (M)',
                'es_obligatorio_bomberos': True,
                'orden': 6
            },
            {
                'nombre': 'Circuito de agilidad',
                'categoria': 'agilidad',
                'descripcion': 'Circuito con conos, slalom y saltos',
                'instrucciones': 'Completar el circuito marcado sin derribar elementos.',
                'tiempo_objetivo_hombre': timedelta(seconds=30),
                'tiempo_objetivo_mujer': timedelta(seconds=35),
                'baremo_excelente': '< 25 seg (H) / < 30 seg (M)',
                'baremo_bueno': '25-28 seg (H) / 30-33 seg (M)',
                'baremo_aceptable': '28-30 seg (H) / 33-35 seg (M)',
                'baremo_insuficiente': '> 30 seg (H) / > 35 seg (M)',
                'es_obligatorio_bomberos': True,
                'orden': 7
            },
            {
                'nombre': 'Transporte de víctima',
                'categoria': 'fuerza',
                'descripcion': 'Transporte de maniquí de 70kg en 50 metros',
                'instrucciones': 'Arrastrar maniquí de 70kg por terreno llano durante 50 metros.',
                'tiempo_objetivo_hombre': timedelta(seconds=45),
                'tiempo_objetivo_mujer': timedelta(seconds=60),
                'peso_objetivo': 70.0,
                'distancia_objetivo': 50.0,
                'baremo_excelente': '< 35 seg (H) / < 50 seg (M)',
                'baremo_bueno': '35-40 seg (H) / 50-55 seg (M)',
                'baremo_aceptable': '40-45 seg (H) / 55-60 seg (M)',
                'baremo_insuficiente': '> 45 seg (H) / > 60 seg (M)',
                'es_obligatorio_bomberos': True,
                'orden': 8
            }
        ]
        
        for ejercicio_data in ejercicios_bomberos:
            ejercicio, created = EjercicioFisico.objects.get_or_create(
                nombre=ejercicio_data['nombre'],
                defaults=ejercicio_data
            )
            if created:
                self.stdout.write(f'✅ Creado ejercicio: {ejercicio.nombre}')
            else:
                self.stdout.write(f'⚠️  Ya existe: {ejercicio.nombre}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Sistema de ejercicios físicos creado!\n'
                f'Total ejercicios: {EjercicioFisico.objects.count()}'
            )
        )
