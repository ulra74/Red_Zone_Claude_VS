#!/usr/bin/env python3
"""
Script simple para poblar la base de datos con datos básicos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
django.setup()

from accounts.models import CustomUser
from core.models import (
    Categoria, Oposicion, Tema, Apartado, Pregunta, 
    TemaOposicion, Respuesta
)

def crear_datos_basicos():
    """Crear datos básicos para pruebas"""
    print("🔥 Creando datos básicos...")
    
    # Obtener usuario admin
    admin_user = CustomUser.objects.get(username='admin')
    
    # Crear categorías
    print("📂 Creando categorías...")
    cat_normativa = Categoria.objects.get_or_create(
        nombre="Normativa",
        descripcion="Leyes y normativas relacionadas con bomberos"
    )[0]
    
    cat_tecnica = Categoria.objects.get_or_create(
        nombre="Técnica",
        descripcion="Aspectos técnicos y operativos"
    )[0]
    
    # Crear oposiciones
    print("📋 Creando oposiciones...")
    oposicion_bomberos = Oposicion.objects.get_or_create(
        nombre="Bomberos Comunidad de Madrid 2024",
        descripcion="Oposición para bomberos de la Comunidad de Madrid",
        fecha_convocatoria="2024-01-15"
    )[0]
    
    # Crear temas
    print("📖 Creando temas...")
    tema_normativa = Tema.objects.get_or_create(
        nombre="Normativa Básica de Bomberos",
        descripcion="Legislación básica aplicable al cuerpo de bomberos",
        orden=1
    )[0]
    
    tema_extincion = Tema.objects.get_or_create(
        nombre="Técnicas de Extinción",
        descripcion="Métodos y técnicas para la extinción de incendios",
        orden=2
    )[0]
    
    tema_rescate = Tema.objects.get_or_create(
        nombre="Rescate y Salvamento",
        descripcion="Técnicas de rescate en diferentes situaciones",
        orden=3
    )[0]
    
    # Asociar temas con oposiciones
    print("🔗 Asociando temas con oposiciones...")
    TemaOposicion.objects.get_or_create(
        tema=tema_normativa,
        oposicion=oposicion_bomberos,
        orden_en_oposicion=1,
        peso_en_oposicion=25
    )
    
    TemaOposicion.objects.get_or_create(
        tema=tema_extincion,
        oposicion=oposicion_bomberos,
        orden_en_oposicion=2,
        peso_en_oposicion=30
    )
    
    TemaOposicion.objects.get_or_create(
        tema=tema_rescate,
        oposicion=oposicion_bomberos,
        orden_en_oposicion=3,
        peso_en_oposicion=30
    )
    
    # Crear apartados
    print("📝 Creando apartados...")
    
    # Apartados para tema normativa
    apartado_ley = Apartado.objects.get_or_create(
        tema=tema_normativa,
        nombre="Ley 17/2015 del Sistema Nacional de Protección Civil",
        descripcion="Aspectos fundamentales de la ley",
        orden=1
    )[0]
    
    apartado_estatuto = Apartado.objects.get_or_create(
        tema=tema_normativa,
        nombre="Estatuto Básico del Empleado Público",
        descripcion="Derechos y deberes del empleado público",
        orden=2
    )[0]
    
    # Apartados para tema extinción
    apartado_agua = Apartado.objects.get_or_create(
        tema=tema_extincion,
        nombre="Extinción con Agua",
        descripcion="Técnicas de extinción utilizando agua",
        orden=1
    )[0]
    
    apartado_espuma = Apartado.objects.get_or_create(
        tema=tema_extincion,
        nombre="Extinción con Espuma",
        descripcion="Uso de espuma en la extinción de incendios",
        orden=2
    )[0]
    
    # Apartados para tema rescate
    apartado_altura = Apartado.objects.get_or_create(
        tema=tema_rescate,
        nombre="Rescate en Altura",
        descripcion="Técnicas de rescate en edificios y estructuras",
        orden=1
    )[0]
    
    apartado_vehiculos = Apartado.objects.get_or_create(
        tema=tema_rescate,
        nombre="Rescate en Vehículos",
        descripcion="Excarcelación y rescate en accidentes de tráfico",
        orden=2
    )[0]
    
    # Crear preguntas básicas
    print("❓ Creando preguntas básicas...")
    
    # Preguntas para normativa
    pregunta1 = Pregunta.objects.get_or_create(
        apartado=apartado_ley,
        enunciado="¿En qué año se aprobó la Ley 17/2015 del Sistema Nacional de Protección Civil?"
    )[0]
    
    # Respuestas para pregunta1
    Respuesta.objects.get_or_create(
        pregunta=pregunta1,
        texto="2015",
        es_correcta=True
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta1,
        texto="2014",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta1,
        texto="2016",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta1,
        texto="2013",
        es_correcta=False
    )
    
    pregunta2 = Pregunta.objects.get_or_create(
        apartado=apartado_estatuto,
        enunciado="¿Cuál es el principio fundamental que rige la actuación del empleado público?"
    )[0]
    
    # Respuestas para pregunta2
    Respuesta.objects.get_or_create(
        pregunta=pregunta2,
        texto="Servicio al interés general",
        es_correcta=True
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta2,
        texto="Eficiencia económica",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta2,
        texto="Rapidez en la gestión",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta2,
        texto="Jerarquía administrativa",
        es_correcta=False
    )
    
    # Preguntas para extinción
    pregunta3 = Pregunta.objects.get_or_create(
        apartado=apartado_agua,
        enunciado="¿Cuál es la principal ventaja del agua como agente extintor?"
    )[0]
    
    # Respuestas para pregunta3
    Respuesta.objects.get_or_create(
        pregunta=pregunta3,
        texto="Alto poder de enfriamiento",
        es_correcta=True
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta3,
        texto="Bajo coste",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta3,
        texto="Fácil transporte",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta3,
        texto="No es tóxica",
        es_correcta=False
    )
    
    pregunta4 = Pregunta.objects.get_or_create(
        apartado=apartado_espuma,
        enunciado="¿Qué tipo de espuma se utiliza para fuegos de hidrocarburos?"
    )[0]
    
    # Respuestas para pregunta4
    Respuesta.objects.get_or_create(
        pregunta=pregunta4,
        texto="Espuma AFFF",
        es_correcta=True
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta4,
        texto="Espuma proteínica",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta4,
        texto="Espuma sintética",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta4,
        texto="Espuma fluoroproteínica",
        es_correcta=False
    )
    
    # Preguntas para rescate
    pregunta5 = Pregunta.objects.get_or_create(
        apartado=apartado_altura,
        enunciado="¿Cuál es la altura mínima para considerar un trabajo en altura?"
    )[0]
    
    # Respuestas para pregunta5
    Respuesta.objects.get_or_create(
        pregunta=pregunta5,
        texto="2 metros",
        es_correcta=True
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta5,
        texto="1,5 metros",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta5,
        texto="3 metros",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta5,
        texto="2,5 metros",
        es_correcta=False
    )
    
    pregunta6 = Pregunta.objects.get_or_create(
        apartado=apartado_vehiculos,
        enunciado="¿Cuál es la primera medida de seguridad en un rescate vehicular?"
    )[0]
    
    # Respuestas para pregunta6
    Respuesta.objects.get_or_create(
        pregunta=pregunta6,
        texto="Estabilización del vehículo",
        es_correcta=True
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta6,
        texto="Cortar la corriente",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta6,
        texto="Romper el cristal",
        es_correcta=False
    )
    Respuesta.objects.get_or_create(
        pregunta=pregunta6,
        texto="Llamar a la ambulancia",
        es_correcta=False
    )
    
    # Crear más preguntas para tener suficientes para los exámenes
    print("📝 Creando preguntas adicionales...")
    
    # Más preguntas básicas
    for i in range(7, 21):
        apartado = apartado_ley if i % 2 == 0 else apartado_estatuto
        pregunta = Pregunta.objects.get_or_create(
            apartado=apartado,
            enunciado=f"Pregunta de normativa número {i}. ¿Cuál es la respuesta correcta?"
        )[0]
        
        # Respuestas
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta correcta {i}",
            es_correcta=True
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}A",
            es_correcta=False
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}B",
            es_correcta=False
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}C",
            es_correcta=False
        )
    
    # Más preguntas de extinción
    for i in range(21, 31):
        apartado = apartado_agua if i % 2 == 0 else apartado_espuma
        pregunta = Pregunta.objects.get_or_create(
            apartado=apartado,
            enunciado=f"Pregunta de extinción número {i}. ¿Cuál es la respuesta correcta?"
        )[0]
        
        # Respuestas
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta correcta {i}",
            es_correcta=True
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}A",
            es_correcta=False
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}B",
            es_correcta=False
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}C",
            es_correcta=False
        )
    
    # Más preguntas de rescate
    for i in range(31, 41):
        apartado = apartado_altura if i % 2 == 0 else apartado_vehiculos
        pregunta = Pregunta.objects.get_or_create(
            apartado=apartado,
            enunciado=f"Pregunta de rescate número {i}. ¿Cuál es la respuesta correcta?"
        )[0]
        
        # Respuestas
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta correcta {i}",
            es_correcta=True
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}A",
            es_correcta=False
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}B",
            es_correcta=False
        )
        Respuesta.objects.get_or_create(
            pregunta=pregunta,
            texto=f"Respuesta incorrecta {i}C",
            es_correcta=False
        )
    
    print("✅ Datos básicos creados exitosamente!")
    print(f"📂 Categorías: {Categoria.objects.count()}")
    print(f"📋 Oposiciones: {Oposicion.objects.count()}")
    print(f"📖 Temas: {Tema.objects.count()}")
    print(f"📝 Apartados: {Apartado.objects.count()}")
    print(f"❓ Preguntas: {Pregunta.objects.count()}")
    print(f"✅ Respuestas: {Respuesta.objects.count()}")

if __name__ == "__main__":
    try:
        crear_datos_basicos()
        print("\n🎉 Base de datos poblada correctamente!")
    except Exception as e:
        print(f"\n❌ Error al poblar la base de datos: {e}")
        import traceback
        traceback.print_exc()