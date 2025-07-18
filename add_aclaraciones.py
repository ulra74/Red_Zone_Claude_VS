#!/usr/bin/env python3
"""
Script para añadir aclaraciones a las preguntas existentes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
django.setup()

from core.models import Pregunta, Respuesta

def main():
    print("🔄 Añadiendo aclaraciones a preguntas existentes...")
    
    # Obtener todas las preguntas
    preguntas = Pregunta.objects.all()
    total_preguntas = preguntas.count()
    
    if total_preguntas == 0:
        print("❌ No hay preguntas en la base de datos")
        return
    
    print(f"📊 Se encontraron {total_preguntas} preguntas")
    
    # Contador de preguntas actualizadas
    actualizadas = 0
    
    # Aclaraciones por tema
    aclaraciones_por_tema = {
        'normativa': [
            "La Ley 17/2015 del Sistema Nacional de Protección Civil se aprobó el 9 de julio de 2015, estableciendo el marco normativo para la protección civil en España.",
            "El principio de servicio al interés general es fundamental en la actuación pública, priorizando el bien común sobre intereses particulares.",
            "La normativa de protección civil establece los mecanismos de coordinación entre las diferentes administraciones públicas.",
            "Los empleados públicos tienen deberes específicos establecidos en el Estatuto Básico del Empleado Público.",
            "La legislación en materia de emergencias ha evolucionado para adaptarse a los nuevos riesgos y amenazas."
        ],
        'extincion': [
            "El agua es el agente extintor más utilizado debido a su capacidad de enfriamiento y disponibilidad.",
            "La espuma AFFF (Aqueous Film Forming Foam) es especialmente efectiva en fuegos de hidrocarburos.",
            "La selección del agente extintor debe considerar el tipo de combustible y las condiciones del incendio.",
            "La aplicación correcta del agua requiere conocer las técnicas de ataque directo e indirecto.",
            "Los sistemas de extinción por espuma requieren equipos especializados y personal entrenado."
        ],
        'rescate': [
            "El trabajo en altura requiere equipos de protección individual certificados y personal especializado.",
            "La seguridad del rescatista es prioritaria para evitar incrementar el número de víctimas.",
            "Las técnicas de rescate vehicular han evolucionado con los nuevos materiales de los vehículos.",
            "El triaje es fundamental para optimizar los recursos en situaciones de múltiples víctimas.",
            "La coordinación entre equipos es esencial en operaciones de rescate complejas."
        ]
    }
    
    # Explicaciones para respuestas
    explicaciones_respuesta = {
        'correcta': [
            "Esta es la respuesta correcta según la normativa vigente.",
            "Respuesta acertada. Esta información se encuentra en el manual oficial.",
            "Correcto. Esta es la práctica recomendada por los protocolos.",
            "Exacto. Esta respuesta refleja el procedimiento estándar.",
            "Muy bien. Esta es la opción que establece la legislación."
        ],
        'incorrecta': [
            "Esta opción no es correcta según la normativa actual.",
            "Respuesta incorrecta. Esta información no se ajusta a los protocolos.",
            "Esta alternativa no es la adecuada según los procedimientos.",
            "Opción errónea. No corresponde con la práctica recomendada.",
            "Esta respuesta no es válida según la reglamentación."
        ]
    }
    
    for pregunta in preguntas:
        # Determinar tema basado en el apartado
        tema_key = 'normativa'  # Por defecto
        if 'extinc' in pregunta.apartado.nombre.lower():
            tema_key = 'extincion'
        elif 'rescate' in pregunta.apartado.nombre.lower():
            tema_key = 'rescate'
        
        # Añadir aclaración a la pregunta si no la tiene
        if not pregunta.texto_aclaratorio:
            index = (pregunta.id - 1) % len(aclaraciones_por_tema[tema_key])
            pregunta.texto_aclaratorio = aclaraciones_por_tema[tema_key][index]
            pregunta.save()
            actualizadas += 1
            print(f"✅ Pregunta {pregunta.id}: Aclaración añadida")
        
        # Añadir explicaciones a las respuestas
        respuestas = pregunta.respuestas.all()
        for respuesta in respuestas:
            if not respuesta.explicacion:
                if respuesta.es_correcta:
                    index = (respuesta.id - 1) % len(explicaciones_respuesta['correcta'])
                    respuesta.explicacion = explicaciones_respuesta['correcta'][index]
                else:
                    index = (respuesta.id - 1) % len(explicaciones_respuesta['incorrecta'])
                    respuesta.explicacion = explicaciones_respuesta['incorrecta'][index]
                respuesta.save()
                print(f"  📝 Respuesta {respuesta.id}: Explicación añadida")
    
    print(f"\n🎉 Proceso completado:")
    print(f"   📚 {actualizadas} preguntas actualizadas con aclaraciones")
    print(f"   💡 Todas las respuestas ahora tienen explicaciones")
    print(f"   🔄 Total de preguntas procesadas: {total_preguntas}")

if __name__ == "__main__":
    main()