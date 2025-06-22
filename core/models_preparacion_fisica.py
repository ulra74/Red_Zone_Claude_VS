from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class TipoEjercicio(models.TextChoices):
    RESISTENCIA = 'resistencia', 'Resistencia'
    FUERZA = 'fuerza', 'Fuerza'
    VELOCIDAD = 'velocidad', 'Velocidad'
    AGILIDAD = 'agilidad', 'Agilidad'
    FLEXIBILIDAD = 'flexibilidad', 'Flexibilidad'
    NATACION = 'natacion', 'Natación'
    ESCALADA = 'escalada', 'Escalada'


class EjercicioFisico(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=TipoEjercicio.choices)
    descripcion = models.TextField()
    instrucciones = models.TextField(blank=True)
    video_demostrativo = models.FileField(upload_to='ejercicios/videos/', blank=True, null=True)
    imagen = models.ImageField(upload_to='ejercicios/imagenes/', blank=True, null=True)
    
    # Objetivos estándar para bomberos
    tiempo_objetivo_hombre = models.DurationField(null=True, blank=True)
    tiempo_objetivo_mujer = models.DurationField(null=True, blank=True)
    repeticiones_objetivo = models.IntegerField(null=True, blank=True)
    distancia_objetivo = models.FloatField(null=True, blank=True, help_text="En metros")
    peso_objetivo = models.FloatField(null=True, blank=True, help_text="En kg")
    
    # Baremos de puntuación
    baremo_excelente = models.CharField(max_length=100, blank=True)
    baremo_bueno = models.CharField(max_length=100, blank=True)
    baremo_aceptable = models.CharField(max_length=100, blank=True)
    baremo_insuficiente = models.CharField(max_length=100, blank=True)
    
    es_obligatorio_bomberos = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ejercicio Físico"
        verbose_name_plural = "Ejercicios Físicos"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"
    
    def get_objetivo_por_genero(self, es_mujer=False):
        """Devuelve el objetivo según el género"""
        if self.tiempo_objetivo_hombre and self.tiempo_objetivo_mujer:
            return self.tiempo_objetivo_mujer if es_mujer else self.tiempo_objetivo_hombre
        return None


class PlanEntrenamiento(models.Model):
    TIPOS_PLAN = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('precompeticion', 'Pre-competición'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    FASES_ENTRENAMIENTO = [
        ('base', 'Fase Base'),
        ('desarrollo', 'Fase de Desarrollo'),
        ('pico', 'Pico de Forma'),
        ('mantenimiento', 'Mantenimiento'),
        ('recuperacion', 'Recuperación'),
    ]
    
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planes_entrenamiento')
    nombre = models.CharField(max_length=200)
    tipo_plan = models.CharField(max_length=20, choices=TIPOS_PLAN, default='principiante')
    fase_actual = models.CharField(max_length=20, choices=FASES_ENTRENAMIENTO, default='base')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_examen_objetivo = models.DateField(null=True, blank=True)
    
    # Configuración del plan
    dias_entrenamiento_semana = models.IntegerField(default=5)
    duracion_sesion_minutos = models.IntegerField(default=90)
    
    # Objetivos específicos
    objetivo_principal = models.TextField()
    objetivos_secundarios = models.TextField(blank=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    completado = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plan de Entrenamiento"
        verbose_name_plural = "Planes de Entrenamiento"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nombre} - {self.estudiante.username}"
    
    @property
    def duracion_total(self):
        return (self.fecha_fin - self.fecha_inicio).days
    
    @property
    def dias_restantes(self):
        if self.fecha_examen_objetivo:
            return (self.fecha_examen_objetivo - timezone.now().date()).days
        return (self.fecha_fin - timezone.now().date()).days
    
    @property
    def porcentaje_completado(self):
        total_dias = (self.fecha_fin - self.fecha_inicio).days
        dias_transcurridos = (timezone.now().date() - self.fecha_inicio).days
        return min(100, max(0, (dias_transcurridos / total_dias) * 100))


class SesionEntrenamiento(models.Model):
    plan = models.ForeignKey(PlanEntrenamiento, on_delete=models.CASCADE, related_name='sesiones')
    fecha = models.DateField()
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    ejercicios = models.ManyToManyField(EjercicioFisico, through='EjercicioSesion')
    
    # Estado de la sesión
    completada = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    tiempo_total = models.DurationField(null=True, blank=True)
    
    # Evaluación subjetiva
    nivel_esfuerzo = models.IntegerField(
        null=True, blank=True, 
        choices=[(i, str(i)) for i in range(1, 11)],
        help_text="Del 1 al 10"
    )
    nivel_energia_post = models.IntegerField(
        null=True, blank=True,
        choices=[(i, str(i)) for i in range(1, 11)],
        help_text="Del 1 al 10"
    )
    
    notas_entrenador = models.TextField(blank=True)
    notas_estudiante = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sesión de Entrenamiento"
        verbose_name_plural = "Sesiones de Entrenamiento"
        ordering = ['fecha']
        unique_together = ['plan', 'fecha']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha}"
    
    def marcar_completada(self):
        """Marca la sesión como completada"""
        self.completada = True
        self.fecha_completado = timezone.now()
        self.save()


class EjercicioSesion(models.Model):
    sesion = models.ForeignKey(SesionEntrenamiento, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(EjercicioFisico, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    
    # Planificación
    series_planificadas = models.IntegerField(default=1)
    repeticiones_planificadas = models.IntegerField(null=True, blank=True)
    tiempo_planificado = models.DurationField(null=True, blank=True)
    peso_planificado = models.FloatField(null=True, blank=True)
    descanso_entre_series = models.DurationField(null=True, blank=True)
    
    # Ejecución real
    series_realizadas = models.IntegerField(default=0)
    repeticiones_realizadas = models.IntegerField(null=True, blank=True)
    tiempo_realizado = models.DurationField(null=True, blank=True)
    peso_utilizado = models.FloatField(null=True, blank=True)
    
    # Evaluación
    resultado_satisfactorio = models.BooleanField(default=False)
    mejora_respecto_anterior = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Ejercicio en Sesión"
        verbose_name_plural = "Ejercicios en Sesión"
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.ejercicio.nombre} - {self.sesion.nombre}"
    
    def calcular_puntuacion_baremo(self):
        """Calcula puntuación según baremos de bomberos"""
        # Implementar lógica de baremos según el ejercicio
        pass


class RegistroMarcas(models.Model):
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marcas_personales')
    ejercicio = models.ForeignKey(EjercicioFisico, on_delete=models.CASCADE)
    fecha = models.DateField()
    
    # Marca registrada
    tiempo_marca = models.DurationField(null=True, blank=True)
    repeticiones_marca = models.IntegerField(null=True, blank=True)
    peso_marca = models.FloatField(null=True, blank=True)
    distancia_marca = models.FloatField(null=True, blank=True)
    
    # Contexto
    es_marca_personal = models.BooleanField(default=False)
    es_objetivo_cumplido = models.BooleanField(default=False)
    mejora_respecto_anterior = models.BooleanField(default=False)
    porcentaje_mejora = models.FloatField(null=True, blank=True)
    
    # Puntuación según baremos oficiales
    puntuacion_baremo = models.FloatField(null=True, blank=True)
    nivel_baremo = models.CharField(
        max_length=20,
        choices=[
            ('excelente', 'Excelente'),
            ('bueno', 'Bueno'),
            ('aceptable', 'Aceptable'),
            ('insuficiente', 'Insuficiente'),
        ],
        null=True, blank=True
    )
    
    observaciones = models.TextField(blank=True)
    validado_por_entrenador = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Registro de Marca"
        verbose_name_plural = "Registro de Marcas"
        ordering = ['-fecha', '-created_at']
        unique_together = ['estudiante', 'ejercicio', 'fecha']
    
    def __str__(self):
        marca = ""
        if self.tiempo_marca:
            marca = str(self.tiempo_marca)
        elif self.repeticiones_marca:
            marca = f"{self.repeticiones_marca} reps"
        elif self.peso_marca:
            marca = f"{self.peso_marca} kg"
        elif self.distancia_marca:
            marca = f"{self.distancia_marca} m"
        
        return f"{self.estudiante.username} - {self.ejercicio.nombre}: {marca}"
