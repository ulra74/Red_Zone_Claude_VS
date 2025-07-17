#!/usr/bin/env python
"""
Script to clear Django sessions - Run this to fix login issues
"""
import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_zone_academy.settings')
django.setup()

def clear_sessions():
    """Clear all Django sessions"""
    try:
        from django.contrib.sessions.models import Session
        
        # Delete all sessions
        session_count = Session.objects.count()
        Session.objects.all().delete()
        
        print(f"✅ Eliminadas {session_count} sesiones")
        print("✅ Todas las sesiones han sido limpiadas")
        print("✅ Ahora puedes acceder a la aplicación nuevamente")
        
    except Exception as e:
        print(f"❌ Error al limpiar sesiones: {e}")

if __name__ == "__main__":
    clear_sessions()