from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TipoLogro(models.TextChoices):
    ESTUDIO = 'estudio', 'Estudio'
    FISICO = 'fisico', 'Físico'
    EXAMENES = 'examenes', 'Exámenes'
    CONSTANCIA = 'constancia', 'Constancia'
    SOCIAL = 'social', 'Social'
    ESPECIAL = 'especial', 'Especial'


class Logro(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    icono = models.CharField(max_length=50, help_text="Icono de Bootstrap Icons")
    color = models.CharField(max_length=7, default="#007bff", help_text="Color hexadecimal")
    tipo = models.CharField(max_length=20, choices=TipoLogro.choices)
    
    # Criterios para desbloquear
    criterio_json = models.JSONField(help_text="Criterios en formato JSON")
    puntos = models.IntegerField(default=100)
    
    # Configuración
    es_secreto = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Logro"
        verbose_name_plural = "Logros"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class LogroUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logros_obtenidos')
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_obtenido = models.DateTimeField(auto_now_add=True)
    progreso_actual = models.JSONField(default=dict)
    notificado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Logro de Usuario"
        verbose_name_plural = "Logros de Usuario"
        unique_together = ['usuario', 'logro']
        ordering = ['-fecha_obtenido']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.logro.nombre}"


class DesafioSemanal(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    icono = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#ffc107")
    
    # Fechas
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Criterios
    criterio_json = models.JSONField()
    recompensa_puntos = models.IntegerField(default=50)
    recompensa_descripcion = models.CharField(max_length=500)
    
    # Configuración
    activo = models.BooleanField(default=True)
    max_participantes = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Desafío Semanal"
        verbose_name_plural = "Desafíos Semanales"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio} - {self.fecha_fin})"
    
    @property
    def esta_activo(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.activo and self.fecha_inicio <= hoy <= self.fecha_fin


class ParticipacionDesafio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    desafio = models.ForeignKey(DesafioSemanal, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    progreso_actual = models.JSONField(default=dict)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    puntos_obtenidos = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Participación en Desafío"
        verbose_name_plural = "Participaciones en Desafíos"
        unique_together = ['usuario', 'desafio']
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.desafio.nombre}"


class PuntuacionUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='puntuacion')
    puntos_totales = models.IntegerField(default=0)
    puntos_mes_actual = models.IntegerField(default=0)
    puntos_semana_actual = models.IntegerField(default=0)
    
    # Desglose por categoría
    puntos_estudio = models.IntegerField(default=0)
    puntos_examenes = models.IntegerField(default=0)
    puntos_fisico = models.IntegerField(default=0)
    puntos_constancia = models.IntegerField(default=0)
    puntos_social = models.IntegerField(default=0)
    
    # Estadísticas
    racha_dias_consecutivos = models.IntegerField(default=0)
    racha_maxima = models.IntegerField(default=0)
    ultimo_dia_actividad = models.DateField(null=True, blank=True)
    
    # Nivel y experiencia
    nivel = models.IntegerField(default=1)
    experiencia_actual = models.IntegerField(default=0)
    experiencia_siguiente_nivel = models.IntegerField(default=100)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Puntuación de Usuario"
        verbose_name_plural = "Puntuaciones de Usuario"
        ordering = ['-puntos_totales']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.puntos_totales} puntos (Nivel {self.nivel})"
    
    def agregar_puntos(self, puntos, categoria='general'):
        """Agrega puntos y actualiza nivel si es necesario"""
        self.puntos_totales += puntos
        self.puntos_mes_actual += puntos
        self.puntos_semana_actual += puntos
        
        # Agregar a categoría específica
        if hasattr(self, f'puntos_{categoria}'):
            setattr(self, f'puntos_{categoria}', getattr(self, f'puntos_{categoria}') + puntos)
        
        # Verificar subida de nivel
        self.verificar_subida_nivel()
        self.save()
    
    def verificar_subida_nivel(self):
        """Verifica si el usuario debe subir de nivel"""
        while self.experiencia_actual >= self.experiencia_siguiente_nivel:
            self.experiencia_actual -= self.experiencia_siguiente_nivel
            self.nivel += 1
            self.experiencia_siguiente_nivel = self.calcular_experiencia_siguiente_nivel()
    
    def calcular_experiencia_siguiente_nivel(self):
        """Calcula la experiencia necesaria para el siguiente nivel"""
        return 100 * (self.nivel * 1.5)
