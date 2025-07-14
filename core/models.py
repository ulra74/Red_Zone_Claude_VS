# core/models.py - ARCHIVO CORREGIDO

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

class Tema(models.Model):
    nombre = models.CharField(max_length=200)
    alumnos_con_acceso = models.ManyToManyField(
        User,
        limit_choices_to={'user_type': 'student'},
        blank=True,
        related_name='temas_acceso'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre


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
    'Oposicion', 'Tema', 'TipoArchivo', 'ArchivoOposicion', 'ArchivoTema', 
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