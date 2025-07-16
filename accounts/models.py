
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('admin', 'Administrador'),
        ('student', 'Alumno'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_student(self):
        return self.user_type == 'student'
    
    def get_rango_firefighter(self):
        """Obtiene el rango del bombero según su mejor porcentaje de acierto"""
        if not self.is_student():
            return None
            
        # Importar aquí para evitar import circular
        from core.models import ExamenTestResultado
        
        # Obtener el mejor resultado del estudiante
        mejor_resultado = ExamenTestResultado.objects.filter(
            examen__estudiante=self,
            examen__estudiante__user_type='student'
        ).order_by('-porcentaje_acierto').first()
        
        if not mejor_resultado:
            return self._get_rango_data(0)  # Sin exámenes = 0%
        
        return self._get_rango_data(mejor_resultado.porcentaje_acierto)
    
    def _get_rango_data(self, porcentaje):
        """Determina el rango según el porcentaje de acierto"""
        rangos = [
            (0, 2, "Portador de Cubo", "🪣", "#8B4513"),
            (3, 7, "Aprendiz del Humo", "💨", "#696969"),
            (8, 13, "Recolector de Cenizas", "🌫️", "#778899"),
            (14, 20, "Vigilante de la Llama", "🔥", "#FF4500"),
            (21, 30, "Guardia de la Manguera", "🚒", "#DC143C"),
            (31, 40, "Explorador de Incendios", "🔍", "#FF6347"),
            (41, 50, "Cazafuegos Novato", "🎯", "#FF8C00"),
            (51, 58, "Domador de Brasas", "⚡", "#DAA520"),
            (59, 66, "Capitán del Vapor", "👨‍🚒", "#B8860B"),
            (67, 74, "Señor del Agua a Presión", "💧", "#4682B4"),
            (75, 82, "Custodio del Infierno Apagado", "🛡️", "#4169E1"),
            (83, 89, "Destructor de Llamas Eternas", "⚔️", "#8A2BE2"),
            (90, 95, "Maestro del Cuerpo Ígneo", "🔮", "#9932CC"),
            (96, 99, "General de la Brigada Mítica", "👑", "#FF1493"),
            (100, 100, "Apagafuegos Legendario", "🏆", "#FFD700")
        ]
        
        for min_pct, max_pct, nombre, icono, color in rangos:
            if min_pct <= porcentaje <= max_pct:
                return {
                    'nivel': rangos.index((min_pct, max_pct, nombre, icono, color)) + 1,
                    'nombre': nombre,
                    'icono': icono,
                    'color': color,
                    'porcentaje_min': min_pct,
                    'porcentaje_max': max_pct,
                    'porcentaje_actual': porcentaje
                }
        
        # Por defecto, el primer rango
        return {
            'nivel': 1,
            'nombre': "Portador de Cubo",
            'icono': "🪣",
            'color': "#8B4513",
            'porcentaje_min': 0,
            'porcentaje_max': 2,
            'porcentaje_actual': porcentaje
        }