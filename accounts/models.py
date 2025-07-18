
from django.contrib.auth.models import AbstractUser
from django.db import models
import os

def user_profile_picture_path(instance, filename):
    """Función para generar la ruta de la imagen de perfil"""
    # Obtener la extensión del archivo
    ext = filename.split('.')[-1]
    # Crear un nombre único basado en el ID del usuario
    filename = f'profile_{instance.id}.{ext}'
    # Retornar la ruta completa
    return os.path.join('profile_pictures', filename)

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('admin', 'Administrador'),
        ('student', 'Alumno'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        help_text="Imagen de perfil del usuario"
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_student(self):
        return self.user_type == 'student'
    
    def get_profile_picture_url(self):
        """Obtiene la URL de la imagen de perfil o una por defecto"""
        if self.profile_picture:
            return self.profile_picture.url
        # Retornar una imagen por defecto basada en el tipo de usuario
        return None

    def get_activity_stats(self):
        """Obtiene estadísticas de actividad del usuario"""
        if not self.is_student():
            return None
        
        try:
            activity, created = UserActivityStats.objects.get_or_create(user=self)
            return activity
        except:
            return None
    
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
            (0, 2.99, "Portador de Cubo", "🪣", "#8B4513"),
            (3, 7.99, "Aprendiz del Humo", "💨", "#696969"),
            (8, 13.99, "Recolector de Cenizas", "🌫️", "#778899"),
            (14, 20.99, "Vigilante de la Llama", "🔥", "#FF4500"),
            (21, 30.99, "Guardia de la Manguera", "🚒", "#DC143C"),
            (31, 40.99, "Explorador de Incendios", "🔍", "#FF6347"),
            (41, 50.99, "Cazafuegos Novato", "🎯", "#FF8C00"),
            (51, 58.99, "Domador de Brasas", "⚡", "#DAA520"),
            (59, 66.99, "Capitán del Vapor", "👨‍🚒", "#B8860B"),
            (67, 74.99, "Señor del Agua a Presión", "💧", "#4682B4"),
            (75, 82.99, "Custodio del Infierno Apagado", "🛡️", "#4169E1"),
            (83, 89.99, "Destructor de Llamas Eternas", "⚔️", "#8A2BE2"),
            (90, 95.99, "Maestro del Cuerpo Ígneo", "🔮", "#9932CC"),
            (96, 99.99, "General de la Brigada Mítica", "👑", "#FF1493"),
            (100, 100, "Apagafuegos Legendario", "🏆", "#FFD700")
        ]
        
        for i, (min_pct, max_pct, nombre, icono, color) in enumerate(rangos):
            if min_pct <= porcentaje <= max_pct:
                return {
                    'nivel': i + 1,
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

    def get_enhanced_ranking_score(self):
        """Calcula el puntaje mejorado para el ranking incluyendo actividad y streaks"""
        if not self.is_student():
            return 0
        
        # Importar aquí para evitar import circular
        from core.models import ExamenTestResultado
        from django.db.models import Avg
        
        # Obtener puntuación base como la MEDIA de todos los exámenes
        resultados = ExamenTestResultado.objects.filter(estudiante=self)
        
        if not resultados.exists():
            return 0.0
        
        # Calcular media de todos los exámenes
        media_resultado = resultados.aggregate(media=Avg('porcentaje_acierto'))['media']
        base_score = float(media_resultado) if media_resultado else 0.0
        
        # Obtener estadísticas de actividad
        activity_stats = self.get_activity_stats()
        if not activity_stats:
            return base_score
        
        # Calcular bonificaciones y penalizaciones
        streak_bonus = min(activity_stats.current_streak * 2.0, 20.0)  # Max 20% bonus
        consistency_bonus = min(activity_stats.total_exams_completed * 0.5, 15.0)  # Max 15% bonus
        
        # Bonificación por tiempo de respuesta rápido (usando la media de todos los exámenes)
        speed_bonus = 0.0
        if resultados.exists():
            # Calcular tiempo promedio por pregunta de TODOS los exámenes
            total_tiempo = sum(r.tiempo_total_segundos for r in resultados)
            total_preguntas = sum(r.preguntas_correctas + r.preguntas_incorrectas + r.preguntas_sin_responder for r in resultados)
            
            if total_preguntas > 0 and total_tiempo > 0:
                tiempo_promedio_por_pregunta = total_tiempo / total_preguntas
                # Bonificación si responde en menos de 30 segundos por pregunta
                if tiempo_promedio_por_pregunta < 30:
                    speed_bonus = min((30 - tiempo_promedio_por_pregunta) * 0.3, 10.0)  # Max 10% bonus
        
        # Penalización por inactividad
        from django.utils import timezone
        from datetime import timedelta
        
        days_inactive = (timezone.now().date() - activity_stats.last_exam_date).days if activity_stats.last_exam_date else 999
        inactivity_penalty = 0.0
        
        if days_inactive > 7:
            inactivity_penalty = min(days_inactive * 0.5, 30.0)  # Max 30% penalty
        
        # Calcular puntaje final
        final_score = base_score + streak_bonus + consistency_bonus + speed_bonus - inactivity_penalty
        return max(0, min(100, final_score))  # Mantener entre 0-100


class UserActivityStats(models.Model):
    """Modelo para rastrear la actividad y streaks de los usuarios"""
    
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='activity_stats',
        limit_choices_to={'user_type': 'student'}
    )
    
    # Estadísticas de exámenes
    total_exams_completed = models.PositiveIntegerField(default=0)
    total_exams_retaken = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    
    # Fechas importantes
    last_exam_date = models.DateField(null=True, blank=True)
    streak_start_date = models.DateField(null=True, blank=True)
    last_activity_date = models.DateField(auto_now=True)
    
    # Bonificaciones y penalizaciones
    streak_bonus_points = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    consistency_bonus_points = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    inactivity_penalty_points = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estadísticas de Actividad"
        verbose_name_plural = "Estadísticas de Actividad"
    
    def __str__(self):
        return f"{self.user.username} - Racha: {self.current_streak} días"
    
    def update_exam_completed(self, exam_date=None):
        """Actualiza las estadísticas cuando se completa un examen"""
        from django.utils import timezone
        
        if exam_date is None:
            exam_date = timezone.now().date()
        
        # Actualizar contadores
        self.total_exams_completed += 1
        self.last_exam_date = exam_date
        
        # Actualizar streak
        if self.last_exam_date and self.last_exam_date != exam_date:
            days_diff = (exam_date - self.last_exam_date).days
            if days_diff <= 1:  # Mismo día o día siguiente
                if self.current_streak == 0:
                    self.streak_start_date = exam_date
                self.current_streak += 1
                self.best_streak = max(self.best_streak, self.current_streak)
            else:
                # Racha rota
                self.current_streak = 1
                self.streak_start_date = exam_date
        elif not self.last_exam_date:
            # Primer examen
            self.current_streak = 1
            self.streak_start_date = exam_date
        
        # Calcular bonificaciones
        self._calculate_bonuses()
        self.save()
    
    def update_exam_retaken(self):
        """Actualiza las estadísticas cuando se repite un examen"""
        self.total_exams_retaken += 1
        self.save()
    
    def check_streak_broken(self):
        """Verifica si la racha se ha roto por inactividad"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.last_exam_date:
            return False
        
        days_since_last = (timezone.now().date() - self.last_exam_date).days
        # Cambiar a 3 días para romper la racha (más razonable)
        if days_since_last > 3:
            self.current_streak = 0
            self.streak_start_date = None
            self._calculate_bonuses()
            self.save()
            return True
        return False
    
    def _calculate_bonuses(self):
        """Calcula bonificaciones y penalizaciones"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Bonificación por racha
        self.streak_bonus_points = min(self.current_streak * 2, 20)
        
        # Bonificación por consistencia
        self.consistency_bonus_points = min(self.total_exams_completed * 0.5, 15)
        
        # Penalización por inactividad
        if self.last_exam_date:
            days_inactive = (timezone.now().date() - self.last_exam_date).days
            if days_inactive > 7:
                self.inactivity_penalty_points = min(days_inactive * 0.5, 30)
            else:
                self.inactivity_penalty_points = 0
        else:
            self.inactivity_penalty_points = 0
    
    def get_activity_level(self):
        """Determina el nivel de actividad del usuario"""
        from django.utils import timezone
        
        # Verificar si el usuario ha hecho exámenes recientemente
        if self.last_exam_date:
            days_since_last = (timezone.now().date() - self.last_exam_date).days
            # Solo marcar como inactivo si no ha hecho exámenes en más de 7 días
            if days_since_last > 7:
                return {'level': 'inactive', 'name': 'Inactivo', 'color': '#696969', 'icon': '😴'}
        elif self.total_exams_completed == 0:
            # Usuario nuevo que nunca ha hecho exámenes
            return {'level': 'newcomer', 'name': 'Nuevo', 'color': '#87CEEB', 'icon': '🆕'}
        
        # Lógica basada en racha actual
        if self.current_streak >= 30:
            return {'level': 'legendary', 'name': 'Legendario', 'color': '#FFD700', 'icon': '🏆'}
        elif self.current_streak >= 14:
            return {'level': 'expert', 'name': 'Experto', 'color': '#9932CC', 'icon': '⭐'}
        elif self.current_streak >= 7:
            return {'level': 'advanced', 'name': 'Avanzado', 'color': '#FF6347', 'icon': '🔥'}
        elif self.current_streak >= 3:
            return {'level': 'active', 'name': 'Activo', 'color': '#32CD32', 'icon': '💪'}
        elif self.current_streak >= 1:
            return {'level': 'beginner', 'name': 'Principiante', 'color': '#4169E1', 'icon': '🌟'}
        else:
            # Usuario que ha hecho exámenes pero no tiene racha activa
            return {'level': 'casual', 'name': 'Casual', 'color': '#FFA500', 'icon': '🎯'}
    
    def get_streak_milestone_message(self):
        """Obtiene mensaje de felicitación por milestone alcanzado"""
        milestones = {
            3: "¡Excelente! Has completado 3 días seguidos. ¡Sigue así! 🔥",
            7: "¡Increíble! Una semana completa de dedicación. ¡Eres imparable! ⭐",
            14: "¡Extraordinario! Dos semanas de constancia. ¡Eres un verdadero bombero! 🚒",
            30: "¡LEGENDARIO! Un mes entero de dedicación. ¡Eres una inspiración! 🏆",
            60: "¡ÉPICO! Dos meses de constancia absoluta. ¡Eres una leyenda! 👑",
            90: "¡MÍTICO! Tres meses de perfección. ¡Eres el mejor bombero de la academia! 🌟"
        }
        
        return milestones.get(self.current_streak, None)