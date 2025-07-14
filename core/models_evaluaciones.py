from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class TipoEvaluacion(models.TextChoices):
    TEST = 'test', 'Test de Opción Múltiple'
    SIMULACRO = 'simulacro', 'Simulacro de Examen'
    PRACTICA = 'practica', 'Práctica Libre'
    EVALUACION = 'evaluacion', 'Evaluación Oficial'


class DificultadPregunta(models.TextChoices):
    FACIL = 'facil', 'Fácil'
    MEDIO = 'medio', 'Medio'
    DIFICIL = 'dificil', 'Difícil'


class Categoria(models.Model):
    """Categorías para organizar preguntas por materias"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Color hexadecimal")
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class BancoPregunta(models.Model):
    """Banco de preguntas para los exámenes"""
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='preguntas')
    oposicion = models.ForeignKey('core.Oposicion', on_delete=models.CASCADE, blank=True, null=True)
    tema = models.ForeignKey('core.Tema', on_delete=models.CASCADE, blank=True, null=True)
    
    # Contenido de la pregunta
    enunciado = models.TextField(help_text="Texto de la pregunta")
    imagen = models.ImageField(upload_to='preguntas/imagenes/', blank=True, null=True)
    explicacion = models.TextField(blank=True, help_text="Explicación de la respuesta correcta")
    
    # Metadatos
    dificultad = models.CharField(max_length=10, choices=DificultadPregunta.choices, default=DificultadPregunta.MEDIO)
    puntos = models.PositiveIntegerField(default=1, help_text="Puntos que vale la pregunta")
    tiempo_estimado = models.PositiveIntegerField(default=60, help_text="Tiempo estimado en segundos")
    
    # Estado
    activa = models.BooleanField(default=True)
    aprobada = models.BooleanField(default=False, help_text="Pregunta revisada y aprobada")
    
    # Estadísticas
    veces_preguntada = models.PositiveIntegerField(default=0)
    veces_acertada = models.PositiveIntegerField(default=0)
    
    # Auditoría
    creada_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preguntas_creadas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Banco de Preguntas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.enunciado[:50]}..."
    
    @property
    def porcentaje_acierto(self):
        """Calcula el porcentaje de acierto"""
        if self.veces_preguntada == 0:
            return 0
        return (self.veces_acertada / self.veces_preguntada) * 100
    
    @property
    def es_dificil(self):
        """Determina si la pregunta es difícil basado en estadísticas"""
        return self.porcentaje_acierto < 50 if self.veces_preguntada > 10 else False


class RespuestaPregunta(models.Model):
    """Opciones de respuesta para cada pregunta"""
    pregunta = models.ForeignKey(BancoPregunta, on_delete=models.CASCADE, related_name='respuestas')
    texto = models.TextField()
    es_correcta = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    explicacion = models.TextField(blank=True, help_text="Explicación de por qué es correcta/incorrecta")
    
    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
        ordering = ['orden']
        unique_together = ['pregunta', 'orden']
    
    def __str__(self):
        correcta = "✓" if self.es_correcta else "✗"
        return f"{correcta} {self.texto[:30]}..."


class Examen(models.Model):
    """Configuración de exámenes"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Relaciones
    oposicion = models.ForeignKey('core.Oposicion', on_delete=models.CASCADE, blank=True, null=True)
    tema = models.ForeignKey('core.Tema', on_delete=models.CASCADE, blank=True, null=True)
    categorias = models.ManyToManyField(Categoria, blank=True)
    
    # Configuración del examen
    tipo = models.CharField(max_length=20, choices=TipoEvaluacion.choices, default=TipoEvaluacion.TEST)
    numero_preguntas = models.PositiveIntegerField(default=20)
    tiempo_limite = models.PositiveIntegerField(help_text="Tiempo en minutos", default=30)
    puntuacion_maxima = models.PositiveIntegerField(default=100)
    nota_minima_aprobado = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Opciones avanzadas
    preguntas_aleatorias = models.BooleanField(default=True)
    respuestas_aleatorias = models.BooleanField(default=True)
    mostrar_resultados_inmediatos = models.BooleanField(default=False)
    permitir_revision = models.BooleanField(default=True)
    intentos_maximos = models.PositiveIntegerField(default=1)
    
    # Fechas de disponibilidad
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    
    # Estado
    activo = models.BooleanField(default=False)
    publicado = models.BooleanField(default=False)
    
    # Auditoría
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='examenes_creados')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.titulo
    
    @property
    def esta_disponible(self):
        """Verifica si el examen está disponible"""
        if not self.activo or not self.publicado:
            return False
        
        ahora = timezone.now()
        if self.fecha_inicio and ahora < self.fecha_inicio:
            return False
        if self.fecha_fin and ahora > self.fecha_fin:
            return False
        return True
    
    def generar_preguntas(self, excluir_ids=None):
        """Genera las preguntas para el examen"""
        if excluir_ids is None:
            excluir_ids = []
        
        # Obtener preguntas según configuración
        preguntas_query = BancoPregunta.objects.filter(activa=True, aprobada=True)
        
        if self.oposicion:
            preguntas_query = preguntas_query.filter(oposicion=self.oposicion)
        if self.tema:
            preguntas_query = preguntas_query.filter(tema=self.tema)
        if self.categorias.exists():
            preguntas_query = preguntas_query.filter(categoria__in=self.categorias.all())
        
        # Excluir preguntas ya usadas
        preguntas_query = preguntas_query.exclude(id__in=excluir_ids)
        
        # Seleccionar preguntas
        if self.preguntas_aleatorias:
            preguntas = list(preguntas_query.order_by('?')[:self.numero_preguntas])
        else:
            preguntas = list(preguntas_query[:self.numero_preguntas])
        
        return preguntas


class IntentosExamen(models.Model):
    """Registro de intentos de examen por estudiante"""
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intentos_examenes')
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='intentos')
    
    # Estado del intento
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    tiempo_empleado = models.DurationField(blank=True, null=True)
    completado = models.BooleanField(default=False)
    
    # Resultados
    puntuacion_obtenida = models.FloatField(default=0)
    porcentaje = models.FloatField(default=0)
    aprobado = models.BooleanField(default=False)
    
    # Estadísticas detalladas
    preguntas_correctas = models.PositiveIntegerField(default=0)
    preguntas_incorrectas = models.PositiveIntegerField(default=0)
    preguntas_sin_responder = models.PositiveIntegerField(default=0)
    
    # Metadatos
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Intento de Examen"
        verbose_name_plural = "Intentos de Examen"
        ordering = ['-fecha_inicio']
        unique_together = ['estudiante', 'examen', 'fecha_inicio']
    
    def __str__(self):
        estado = "Completado" if self.completado else "En progreso"
        return f"{self.estudiante.username} - {self.examen.titulo} ({estado})"
    
    def finalizar_intento(self):
        """Finaliza el intento y calcula resultados"""
        if self.completado:
            return
        
        self.fecha_fin = timezone.now()
        self.tiempo_empleado = self.fecha_fin - self.fecha_inicio
        self.completado = True
        
        # Calcular estadísticas
        respuestas = self.respuestas_dadas.all()
        self.preguntas_correctas = respuestas.filter(es_correcta=True).count()
        self.preguntas_incorrectas = respuestas.filter(es_correcta=False, respuesta_seleccionada__isnull=False).count()
        self.preguntas_sin_responder = respuestas.filter(respuesta_seleccionada__isnull=True).count()
        
        # Calcular puntuación
        total_preguntas = respuestas.count()
        if total_preguntas > 0:
            self.porcentaje = (self.preguntas_correctas / total_preguntas) * 100
            self.puntuacion_obtenida = (self.porcentaje * self.examen.puntuacion_maxima) / 100
            self.aprobado = self.puntuacion_obtenida >= (self.examen.nota_minima_aprobado * 10)  # Convertir a escala 100
        
        self.save()
    
    @property
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido"""
        if self.fecha_fin:
            return self.tiempo_empleado
        return timezone.now() - self.fecha_inicio
    
    @property
    def tiempo_restante(self):
        """Calcula el tiempo restante"""
        tiempo_limite = timedelta(minutes=self.examen.tiempo_limite)
        tiempo_usado = self.tiempo_transcurrido
        return max(timedelta(0), tiempo_limite - tiempo_usado)


class PreguntaExamen(models.Model):
    """Preguntas específicas asignadas a un intento de examen"""
    intento = models.ForeignKey(IntentosExamen, on_delete=models.CASCADE, related_name='preguntas_asignadas')
    pregunta = models.ForeignKey(BancoPregunta, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = "Pregunta en Examen"
        verbose_name_plural = "Preguntas en Examen"
        ordering = ['orden']
        unique_together = ['intento', 'orden']
    
    def __str__(self):
        return f"Pregunta {self.orden} - {self.intento}"


class RespuestaEstudiante(models.Model):
    """Respuestas dadas por los estudiantes"""
    intento = models.ForeignKey(IntentosExamen, on_delete=models.CASCADE, related_name='respuestas_dadas')
    pregunta = models.ForeignKey(BancoPregunta, on_delete=models.CASCADE)
    respuesta_seleccionada = models.ForeignKey(RespuestaPregunta, on_delete=models.CASCADE, blank=True, null=True)
    
    # Metadatos
    tiempo_respuesta = models.PositiveIntegerField(help_text="Tiempo en segundos", blank=True, null=True)
    fecha_respuesta = models.DateTimeField(auto_now=True)
    es_correcta = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Respuesta de Estudiante"
        verbose_name_plural = "Respuestas de Estudiantes"
        unique_together = ['intento', 'pregunta']
    
    def save(self, *args, **kwargs):
        """Actualiza estadísticas al guardar"""
        if self.respuesta_seleccionada:
            self.es_correcta = self.respuesta_seleccionada.es_correcta
            
            # Actualizar estadísticas de la pregunta
            if self.pk is None:  # Nueva respuesta
                self.pregunta.veces_preguntada += 1
                if self.es_correcta:
                    self.pregunta.veces_acertada += 1
                self.pregunta.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.intento.estudiante.username} - Pregunta {self.pregunta.id}"


class EstadisticasExamen(models.Model):
    """Estadísticas generales de exámenes"""
    examen = models.OneToOneField(Examen, on_delete=models.CASCADE, related_name='estadisticas')
    
    # Estadísticas generales
    total_intentos = models.PositiveIntegerField(default=0)
    total_aprobados = models.PositiveIntegerField(default=0)
    total_suspensos = models.PositiveIntegerField(default=0)
    
    # Promedios
    puntuacion_promedio = models.FloatField(default=0)
    tiempo_promedio = models.DurationField(default=timedelta(0))
    porcentaje_aprobados = models.FloatField(default=0)
    
    # Extremos
    puntuacion_maxima = models.FloatField(default=0)
    puntuacion_minima = models.FloatField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estadísticas de Examen"
        verbose_name_plural = "Estadísticas de Exámenes"
    
    def actualizar_estadisticas(self):
        """Actualiza todas las estadísticas"""
        intentos = self.examen.intentos.filter(completado=True)
        
        self.total_intentos = intentos.count()
        if self.total_intentos > 0:
            self.total_aprobados = intentos.filter(aprobado=True).count()
            self.total_suspensos = self.total_intentos - self.total_aprobados
            self.porcentaje_aprobados = (self.total_aprobados / self.total_intentos) * 100
            
            puntuaciones = intentos.values_list('puntuacion_obtenida', flat=True)
            self.puntuacion_promedio = sum(puntuaciones) / len(puntuaciones)
            self.puntuacion_maxima = max(puntuaciones)
            self.puntuacion_minima = min(puntuaciones)
            
            tiempos = [i.tiempo_empleado for i in intentos if i.tiempo_empleado]
            if tiempos:
                self.tiempo_promedio = sum(tiempos, timedelta(0)) / len(tiempos)
        
        self.save()