from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

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