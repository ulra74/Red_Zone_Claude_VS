# core/models.py - ACTUALIZADO con relación Oposicion-Tema

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import os

User = get_user_model()

class Oposicion(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_convocatoria = models.DateField()
    alumnos_con_acceso = models.ManyToManyField(
        User, 
        limit_choices_to={'user_type': 'student'},
        blank=True,
        related_name='oposiciones_acceso'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Oposiciones"
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_temas(self):
        """Cuenta total de temas asociados"""
        return self.temas.count()
    
    @property
    def total_estudiantes(self):
        """Cuenta total de estudiantes con acceso"""
        return self.alumnos_con_acceso.count()


class Tema(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, help_text="Descripción del tema")
    
    # RELACIÓN MANY-TO-MANY CON OPOSICIONES
    oposiciones = models.ManyToManyField(
        Oposicion,
        blank=True,
        related_name='temas',
        help_text="Oposiciones a las que pertenece este tema"
    )
    
    alumnos_con_acceso = models.ManyToManyField(
        User,
        limit_choices_to={'user_type': 'student'},
        blank=True,
        related_name='temas_acceso'
    )
    
    # Campos adicionales para organización
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en la oposición")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_oposiciones(self):
        """Cuenta total de oposiciones asociadas"""
        return self.oposiciones.count()
    
    @property
    def total_estudiantes(self):
        """Cuenta total de estudiantes con acceso"""
        return self.alumnos_con_acceso.count()
    
    def get_oposiciones_list(self):
        """Devuelve lista de nombres de oposiciones"""
        return ", ".join([op.nombre for op in self.oposiciones.all()[:3]]) + \
               (f" (+{self.oposiciones.count() - 3} más)" if self.oposiciones.count() > 3 else "")
    
    @property
    def total_apartados(self):
        """Cuenta total de apartados del tema"""
        return self.apartados.count()


class Apartado(models.Model):
    """Apartados o secciones dentro de un tema"""
    tema = models.ForeignKey(
        Tema, 
        on_delete=models.CASCADE, 
        related_name='apartados',
        help_text="Tema al que pertenece este apartado"
    )
    nombre = models.CharField(max_length=200, help_text="Nombre del apartado")
    descripcion = models.TextField(blank=True, help_text="Descripción del apartado")
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el tema")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden', 'nombre']
        unique_together = ['tema', 'nombre']  # No permitir apartados duplicados en el mismo tema
        verbose_name_plural = "Apartados"
    
    def __str__(self):
        return f"{self.tema.nombre} - {self.nombre}"
    
    @property
    def total_preguntas(self):
        """Cuenta total de preguntas en este apartado"""
        return self.preguntas.count() if hasattr(self, 'preguntas') else 0


class Pregunta(models.Model):
    """Preguntas tipo test para examenes"""
    
    # Tipos de dificultad
    DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('medio', 'Medio'),
        ('dificil', 'Difícil'),
    ]
    
    apartado = models.ForeignKey(
        Apartado,
        on_delete=models.CASCADE,
        related_name='preguntas',
        help_text="Apartado al que pertenece esta pregunta"
    )
    
    enunciado = models.TextField(
        help_text="Texto de la pregunta"
    )
    
    texto_aclaratorio = models.TextField(
        blank=True,
        help_text="Explicación que se mostrará después de responder (opcional)"
    )
    
    # La dificultad se calcula automáticamente basada en el porcentaje de acierto
    # No necesitamos almacenar puntos ya que siempre serán los mismos
    # No necesitamos orden ya que las preguntas se mostrarán aleatoriamente
    
    activa = models.BooleanField(
        default=True,
        help_text="Si la pregunta está activa para usar en exámenes"
    )
    
    # Estadísticas de uso
    veces_preguntada = models.PositiveIntegerField(
        default=0,
        help_text="Número de veces que se ha usado en exámenes"
    )
    
    veces_acertada = models.PositiveIntegerField(
        default=0,
        help_text="Número de veces que se ha respondido correctamente"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']  # Orden por fecha de creación
        verbose_name_plural = "Preguntas"
    
    def __str__(self):
        return f"{self.apartado.tema.nombre} - {self.apartado.nombre} - {self.enunciado[:50]}..."
    
    @property
    def porcentaje_acierto(self):
        """Calcula el porcentaje de acierto de la pregunta"""
        if self.veces_preguntada == 0:
            return 0
        return (self.veces_acertada / self.veces_preguntada) * 100
    
    @property
    def dificultad_automatica(self):
        """Calcula la dificultad automáticamente basada en el porcentaje de acierto"""
        if self.veces_preguntada < 10:  # Mínimo 10 intentos para calcular dificultad
            return 'medio'
        
        porcentaje = self.porcentaje_acierto
        if porcentaje >= 70:
            return 'facil'
        elif porcentaje >= 40:
            return 'medio'
        else:
            return 'dificil'
    
    @property
    def dificultad(self):
        """Propiedad para compatibilidad con templates existentes"""
        return self.dificultad_automatica
    
    def get_dificultad_display(self):
        """Obtiene el display de la dificultad automática"""
        dificultad_choices = {
            'facil': 'Fácil',
            'medio': 'Medio',
            'dificil': 'Difícil'
        }
        return dificultad_choices.get(self.dificultad_automatica, 'Medio')
    
    @property
    def puntos(self):
        """Todos los puntos valen 1 - propiedad para compatibilidad"""
        return 1
    
    @property
    def respuesta_correcta(self):
        """Obtiene la respuesta correcta"""
        return self.respuestas.filter(es_correcta=True).first()
    
    @property
    def respuestas_incorrectas(self):
        """Obtiene las respuestas incorrectas"""
        return self.respuestas.filter(es_correcta=False)
    
    def incrementar_estadisticas(self, acertada=False):
        """Incrementa las estadísticas de uso"""
        self.veces_preguntada += 1
        if acertada:
            self.veces_acertada += 1
        self.save(update_fields=['veces_preguntada', 'veces_acertada'])


class Respuesta(models.Model):
    """Respuestas posibles para una pregunta"""
    
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='respuestas',
        help_text="Pregunta a la que pertenece esta respuesta"
    )
    
    texto = models.TextField(
        help_text="Texto de la respuesta"
    )
    
    es_correcta = models.BooleanField(
        default=False,
        help_text="Marcar si esta es la respuesta correcta"
    )
    
    # Eliminamos el orden fijo - se mostrará aleatoriamente
    
    explicacion = models.TextField(
        blank=True,
        help_text="Explicación adicional para esta respuesta (opcional)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']  # Las respuestas se mostrarán en orden aleatorio
        verbose_name_plural = "Respuestas"
        # Asegurar que solo haya una respuesta correcta por pregunta
        unique_together = []
    
    def __str__(self):
        estado = "✓" if self.es_correcta else "✗"
        return f"{estado} {self.texto[:30]}..."
    
    def save(self, *args, **kwargs):
        """Validar que solo hay una respuesta correcta por pregunta"""
        if self.es_correcta:
            # Si esta respuesta se marca como correcta, desmarcar las otras
            Respuesta.objects.filter(
                pregunta=self.pregunta,
                es_correcta=True
            ).exclude(pk=self.pk).update(es_correcta=False)
        super().save(*args, **kwargs)


# Modelo intermedio opcional para datos adicionales de la relación
class TemaOposicion(models.Model):
    """Modelo intermedio para datos adicionales de la relación Tema-Oposición"""
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    oposicion = models.ForeignKey(Oposicion, on_delete=models.CASCADE)
    
    # Campos específicos de la relación
    orden_en_oposicion = models.PositiveIntegerField(default=0)
    es_obligatorio_en_oposicion = models.BooleanField(default=True)
    peso_en_oposicion = models.PositiveIntegerField(default=1, help_text="Peso específico en esta oposición")
    fecha_inicio_tema = models.DateField(null=True, blank=True, help_text="Cuándo se empieza este tema")
    fecha_fin_tema = models.DateField(null=True, blank=True, help_text="Cuándo se termina este tema")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tema', 'oposicion']
        ordering = ['orden_en_oposicion', 'tema__nombre']
        verbose_name = "Tema en Oposición"
        verbose_name_plural = "Temas en Oposiciones"
    
    def __str__(self):
        return f"{self.tema.nombre} - {self.oposicion.nombre}"


class TipoArchivo(models.TextChoices):
    PDF = 'pdf', 'PDF'
    VIDEO = 'video', 'Video'
    AUDIO = 'audio', 'Audio'
    IMAGEN = 'imagen', 'Imagen'
    DOCUMENTO = 'documento', 'Documento'
    PRESENTACION = 'presentacion', 'Presentación'
    OTRO = 'otro', 'Otro'


def upload_to_oposicion(instance, filename):
    """Función para definir la ruta de subida de archivos de oposiciones"""
    return f'oposiciones/{instance.oposicion.id}/{filename}'


def upload_to_tema(instance, filename):
    """Función para definir la ruta de subida de archivos de temas"""
    return f'temas/{instance.tema.id}/{filename}'


class ArchivoOposicion(models.Model):
    """Archivos asociados a oposiciones"""
    oposicion = models.ForeignKey(
        Oposicion, 
        on_delete=models.CASCADE, 
        related_name='archivos'
    )
    nombre = models.CharField(max_length=200, help_text="Nombre descriptivo del archivo")
    descripcion = models.TextField(blank=True, help_text="Descripción opcional del contenido")
    archivo = models.FileField(
        upload_to=upload_to_oposicion,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 
                                  'mp4', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif']
            )
        ]
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TipoArchivo.choices, 
        default=TipoArchivo.DOCUMENTO
    )
    tamaño = models.PositiveIntegerField(blank=True, null=True, help_text="Tamaño en bytes")
    es_publico = models.BooleanField(
        default=True, 
        help_text="Si está marcado, todos los estudiantes con acceso a la oposición podrán ver este archivo"
    )
    subido_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='archivos_oposicion_subidos'
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descargas = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Archivo de Oposición"
        verbose_name_plural = "Archivos de Oposiciones"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre} - {self.oposicion.nombre}"
    
    def save(self, *args, **kwargs):
        if self.archivo and not self.tamaño:
            self.tamaño = self.archivo.size
        super().save(*args, **kwargs)
    
    @property
    def tamaño_legible(self):
        """Devuelve el tamaño del archivo en formato legible"""
        if not self.tamaño:
            return "Desconocido"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.tamaño < 1024.0:
                return f"{self.tamaño:.1f} {unit}"
            self.tamaño /= 1024.0
        return f"{self.tamaño:.1f} TB"
    
    @property
    def extension(self):
        """Devuelve la extensión del archivo"""
        if self.archivo:
            return os.path.splitext(self.archivo.name)[1].lower()
        return ""


class ArchivoTema(models.Model):
    """Archivos asociados a temas"""
    tema = models.ForeignKey(
        Tema, 
        on_delete=models.CASCADE, 
        related_name='archivos'
    )
    nombre = models.CharField(max_length=200, help_text="Nombre descriptivo del archivo")
    descripcion = models.TextField(blank=True, help_text="Descripción opcional del contenido")
    archivo = models.FileField(
        upload_to=upload_to_tema,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 
                                  'mp4', 'avi', 'mov', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif']
            )
        ]
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TipoArchivo.choices, 
        default=TipoArchivo.DOCUMENTO
    )
    tamaño = models.PositiveIntegerField(blank=True, null=True, help_text="Tamaño en bytes")
    es_publico = models.BooleanField(
        default=True, 
        help_text="Si está marcado, todos los estudiantes con acceso al tema podrán ver este archivo"
    )
    subido_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='archivos_tema_subidos'
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descargas = models.PositiveIntegerField(default=0)
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el tema")
    
    class Meta:
        verbose_name = "Archivo de Tema"
        verbose_name_plural = "Archivos de Temas"
        ordering = ['orden', '-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre} - {self.tema.nombre}"
    
    def save(self, *args, **kwargs):
        if self.archivo and not self.tamaño:
            self.tamaño = self.archivo.size
        super().save(*args, **kwargs)
    
    @property
    def tamaño_legible(self):
        """Devuelve el tamaño del archivo en formato legible"""
        if not self.tamaño:
            return "Desconocido"
        
        bytes_size = self.tamaño
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    @property
    def extension(self):
        """Devuelve la extensión del archivo"""
        if self.archivo:
            return os.path.splitext(self.archivo.name)[1].lower()
        return ""


class DescargaArchivo(models.Model):
    """Registro de descargas de archivos para estadísticas"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo_oposicion = models.ForeignKey(
        ArchivoOposicion, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='registros_descarga'
    )
    archivo_tema = models.ForeignKey(
        ArchivoTema, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='registros_descarga'
    )
    fecha_descarga = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Descarga de Archivo"
        verbose_name_plural = "Descargas de Archivos"
        ordering = ['-fecha_descarga']
    
    def __str__(self):
        archivo = self.archivo_oposicion or self.archivo_tema
        return f"{self.usuario.username} - {archivo.nombre if archivo else 'Archivo eliminado'}"


class ProgresoEstudiante(models.Model):
    """Modelo para trackear el progreso de los estudiantes"""
    estudiante = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'student'},
        related_name='progreso'
    )
    oposicion = models.ForeignKey(
        Oposicion, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='progreso_estudiantes'
    )
    tema = models.ForeignKey(
        Tema, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='progreso_estudiantes'
    )
    porcentaje_completado = models.PositiveIntegerField(default=0)
    tiempo_estudiado = models.PositiveIntegerField(default=0, help_text="Tiempo en minutos")
    ultima_actividad = models.DateTimeField(auto_now=True)
    completado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Progreso de Estudiante"
        verbose_name_plural = "Progreso de Estudiantes"
        unique_together = [['estudiante', 'oposicion'], ['estudiante', 'tema']]
        ordering = ['-ultima_actividad']
    
    def __str__(self):
        contenido = self.oposicion or self.tema
        return f"{self.estudiante.username} - {contenido.nombre if contenido else 'Contenido eliminado'} ({self.porcentaje_completado}%)"


# ============================================================================
# MODELOS DEL SISTEMA DE EXÁMENES
# ============================================================================

class ExamenTest(models.Model):
    """Modelo para configurar y almacenar exámenes tipo test"""
    
    TIPO_CHOICES = [
        ('normal', 'Normal'),
        ('examen', 'Examen'),
    ]
    
    TIPO_ACLARACION_CHOICES = [
        ('inmediata', 'Inmediata (después de cada pregunta)'),
        ('final', 'Al final del examen'),
    ]
    
    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'student'},
        related_name='examenes_test'
    )
    
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del examen"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='normal',
        help_text="Tipo de examen"
    )
    
    # Configuración de temas y apartados
    temas_seleccionados = models.ManyToManyField(
        Tema,
        related_name='examenes_test_tema',
        help_text="Temas seleccionados para el examen"
    )
    
    apartados_seleccionados = models.ManyToManyField(
        Apartado,
        related_name='examenes_test_apartado',
        blank=True,
        help_text="Apartados específicos seleccionados (opcional)"
    )
    
    # Configuración del examen
    numero_preguntas = models.PositiveIntegerField(
        help_text="Número de preguntas del examen (mínimo 10)"
    )
    
    tiempo_por_pregunta = models.PositiveIntegerField(
        help_text="Tiempo máximo por pregunta en segundos (0 = sin límite)"
    )
    
    tipo_aclaracion = models.CharField(
        max_length=20,
        choices=TIPO_ACLARACION_CHOICES,
        default='inmediata',
        help_text="Cuándo mostrar las aclaraciones"
    )
    
    # Fechas
    fecha_inicio = models.DateTimeField(
        help_text="Fecha y hora de inicio del examen"
    )
    
    fecha_fin = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora de finalización del examen"
    )
    
    # Estado
    completado = models.BooleanField(
        default=False,
        help_text="Si el examen ha sido completado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Examen Test"
        verbose_name_plural = "Exámenes Test"
    
    def __str__(self):
        return f"{self.estudiante.username} - {self.nombre}"
    
    @property
    def duracion_total(self):
        """Duración total del examen en minutos"""
        if self.fecha_fin and self.fecha_inicio:
            delta = self.fecha_fin - self.fecha_inicio
            return int(delta.total_seconds() / 60)
        return 0
    
    @property
    def preguntas_respondidas(self):
        """Número de preguntas respondidas"""
        return self.respuestas_examen.count()
    
    @property
    def preguntas_correctas(self):
        """Número de preguntas correctas"""
        return self.respuestas_examen.filter(es_correcta=True).count()
    
    @property
    def porcentaje_acierto(self):
        """Porcentaje de acierto del examen"""
        if self.preguntas_respondidas == 0:
            return 0
        return (self.preguntas_correctas / self.preguntas_respondidas) * 100
    
    def clean(self):
        """Validación del modelo"""
        from django.core.exceptions import ValidationError
        
        if self.numero_preguntas < 10:
            raise ValidationError("El número mínimo de preguntas es 10")
        
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")


class ExamenTestResultado(models.Model):
    """Modelo para almacenar los resultados finales de un examen test"""
    
    examen = models.OneToOneField(
        ExamenTest,
        on_delete=models.SET_NULL,
        related_name='resultado',
        null=True,
        blank=True
    )
    
    # Campos para conservar información del examen eliminado
    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'student'},
        related_name='resultados_examenes'
    )
    nombre_examen = models.CharField(
        max_length=200,
        help_text="Nombre del examen (conservado para el ranking)"
    )
    fecha_completado = models.DateTimeField(
        help_text="Fecha cuando se completó el examen"
    )
    tipo_examen = models.CharField(
        max_length=20,
        choices=[('normal', 'Normal'), ('examen', 'Examen')],
        default='normal'
    )
    
    # Campo para identificar exámenes del mismo tipo (mismos temas/apartados)
    examen_signature = models.CharField(
        max_length=500,
        blank=True,
        help_text="Hash de los temas y apartados seleccionados para identificar exámenes similares"
    )
    
    puntuacion_total = models.PositiveIntegerField(
        help_text="Puntuación total obtenida"
    )
    
    puntuacion_maxima = models.PositiveIntegerField(
        help_text="Puntuación máxima posible"
    )
    
    porcentaje_acierto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Porcentaje de acierto"
    )
    
    tiempo_total_segundos = models.PositiveIntegerField(
        help_text="Tiempo total empleado en segundos"
    )
    
    preguntas_correctas = models.PositiveIntegerField(
        help_text="Número de preguntas correctas"
    )
    
    preguntas_incorrectas = models.PositiveIntegerField(
        help_text="Número de preguntas incorrectas"
    )
    
    preguntas_sin_responder = models.PositiveIntegerField(
        default=0,
        help_text="Número de preguntas sin responder (por timeout)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Resultado de Examen Test"
        verbose_name_plural = "Resultados de Exámenes Test"
    
    def __str__(self):
        return f"{self.estudiante.username} - {self.nombre_examen} - {self.porcentaje_acierto}%"
    
    @property
    def tiempo_total_minutos(self):
        """Tiempo total en minutos"""
        return self.tiempo_total_segundos / 60
    
    @property
    def tiempo_promedio_por_pregunta(self):
        """Tiempo promedio por pregunta en segundos"""
        total_preguntas = self.preguntas_correctas + self.preguntas_incorrectas + self.preguntas_sin_responder
        if total_preguntas == 0:
            return 0
        return self.tiempo_total_segundos / total_preguntas
    
    @property
    def calificacion_texto(self):
        """Calificación en texto"""
        if self.porcentaje_acierto >= 90:
            return "Excelente"
        elif self.porcentaje_acierto >= 80:
            return "Muy Bueno"
        elif self.porcentaje_acierto >= 70:
            return "Bueno"
        elif self.porcentaje_acierto >= 60:
            return "Regular"
        else:
            return "Insuficiente"
    
    def get_tipo_examen_display(self):
        """Obtiene el nombre legible del tipo de examen"""
        tipo_choices = dict(self._meta.get_field('tipo_examen').choices)
        return tipo_choices.get(self.tipo_examen, self.tipo_examen)


class RespuestaExamenTest(models.Model):
    """Modelo para almacenar las respuestas individuales de un examen test"""
    
    examen = models.ForeignKey(
        ExamenTest,
        on_delete=models.CASCADE,
        related_name='respuestas_examen'
    )
    
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='respuestas_en_examenes_test'
    )
    
    respuesta_seleccionada = models.ForeignKey(
        Respuesta,
        on_delete=models.CASCADE,
        related_name='seleccionada_en_examenes_test',
        blank=True,
        null=True,
        help_text="Respuesta seleccionada por el estudiante"
    )
    
    es_correcta = models.BooleanField(
        default=False,
        help_text="Si la respuesta seleccionada es correcta"
    )
    
    tiempo_empleado_segundos = models.PositiveIntegerField(
        help_text="Tiempo empleado en responder esta pregunta en segundos"
    )
    
    orden_pregunta = models.PositiveIntegerField(
        help_text="Orden en que apareció la pregunta en el examen"
    )
    
    timeout = models.BooleanField(
        default=False,
        help_text="Si la pregunta se respondió por timeout"
    )
    
    penalizada_por_pausa = models.BooleanField(
        default=False,
        help_text="Si la pregunta fue marcada como incorrecta por pausar el examen"
    )
    
    respondida_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['orden_pregunta']
        verbose_name = "Respuesta de Examen Test"
        verbose_name_plural = "Respuestas de Exámenes Test"
        unique_together = ['examen', 'pregunta']
    
    def __str__(self):
        estado = "✓" if self.es_correcta else "✗"
        timeout_text = " (TIMEOUT)" if self.timeout else ""
        pausa_text = " (PAUSA)" if self.penalizada_por_pausa else ""
        return f"{estado} {self.pregunta.enunciado[:50]}...{timeout_text}{pausa_text}"
    
    def save(self, *args, **kwargs):
        """Actualizar estadísticas de la pregunta al guardar"""
        if self.pk is None:  # Solo en creación
            # Actualizar estadísticas de la pregunta
            self.pregunta.incrementar_estadisticas(acertada=self.es_correcta)
        super().save(*args, **kwargs)


# ============================================================================
# IMPORTAR TODOS LOS MODELOS DE LOS OTROS ARCHIVOS
# ============================================================================

# Importar modelos de evaluaciones
from .models_evaluaciones import (
    TipoEvaluacion, DificultadPregunta, Categoria, BancoPregunta, 
    RespuestaPregunta, Examen, IntentosExamen, PreguntaExamen, 
    RespuestaEstudiante, EstadisticasExamen
)

# Importar modelos de gamificación
from .models_gamificacion import (
    TipoLogro, Logro, LogroUsuario, DesafioSemanal, 
    ParticipacionDesafio, PuntuacionUsuario
)

# Importar modelos de preparación física
from .models_preparacion_fisica import (
    TipoEjercicio, EjercicioFisico, PlanEntrenamiento, 
    SesionEntrenamiento, EjercicioSesion, RegistroMarcas
)

# Hacer que todos los modelos estén disponibles en este módulo
__all__ = [
    # Modelos base
    'Oposicion', 'Tema', 'TemaOposicion', 'TipoArchivo', 'ArchivoOposicion', 'ArchivoTema', 
    'DescargaArchivo', 'ProgresoEstudiante',
    
    # Modelos de evaluaciones
    'TipoEvaluacion', 'DificultadPregunta', 'Categoria', 'BancoPregunta', 
    'RespuestaPregunta', 'Examen', 'IntentosExamen', 'PreguntaExamen', 
    'RespuestaEstudiante', 'EstadisticasExamen',
    
    # Modelos de gamificación
    'TipoLogro', 'Logro', 'LogroUsuario', 'DesafioSemanal', 
    'ParticipacionDesafio', 'PuntuacionUsuario',
    
    # Modelos de preparación física
    'TipoEjercicio', 'EjercicioFisico', 'PlanEntrenamiento', 
    'SesionEntrenamiento', 'EjercicioSesion', 'RegistroMarcas'
]