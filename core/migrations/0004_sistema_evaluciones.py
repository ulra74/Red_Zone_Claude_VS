# core/migrations/0004_sistema_evaluaciones.py

from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from datetime import timedelta


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_sistema_completo_bomberos'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Categorías
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('color', models.CharField(default='#007bff', help_text='Color hexadecimal', max_length=7)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('activa', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'ordering': ['orden', 'nombre'],
            },
        ),
        
        # Banco de Preguntas
        migrations.CreateModel(
            name='BancoPregunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enunciado', models.TextField(help_text='Texto de la pregunta')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='preguntas/imagenes/')),
                ('explicacion', models.TextField(blank=True, help_text='Explicación de la respuesta correcta')),
                ('dificultad', models.CharField(choices=[('facil', 'Fácil'), ('medio', 'Medio'), ('dificil', 'Difícil')], default='medio', max_length=10)),
                ('puntos', models.PositiveIntegerField(default=1, help_text='Puntos que vale la pregunta')),
                ('tiempo_estimado', models.PositiveIntegerField(default=60, help_text='Tiempo estimado en segundos')),
                ('activa', models.BooleanField(default=True)),
                ('aprobada', models.BooleanField(default=False, help_text='Pregunta revisada y aprobada')),
                ('veces_preguntada', models.PositiveIntegerField(default=0)),
                ('veces_acertada', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preguntas', to='core.categoria')),
                ('creada_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preguntas_creadas', to=settings.AUTH_USER_MODEL)),
                ('oposicion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.oposicion')),
                ('tema', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.tema')),
            ],
            options={
                'verbose_name': 'Pregunta',
                'verbose_name_plural': 'Banco de Preguntas',
                'ordering': ['-created_at'],
            },
        ),
        
        # Respuestas de Preguntas
        migrations.CreateModel(
            name='RespuestaPregunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('es_correcta', models.BooleanField(default=False)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('explicacion', models.TextField(blank=True, help_text='Explicación de por qué es correcta/incorrecta')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to='core.bancopregunta')),
            ],
            options={
                'verbose_name': 'Respuesta',
                'verbose_name_plural': 'Respuestas',
                'ordering': ['orden'],
            },
        ),
        
        # Exámenes
        migrations.CreateModel(
            name='Examen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('tipo', models.CharField(choices=[('test', 'Test de Opción Múltiple'), ('simulacro', 'Simulacro de Examen'), ('practica', 'Práctica Libre'), ('evaluacion', 'Evaluación Oficial')], default='test', max_length=20)),
                ('numero_preguntas', models.PositiveIntegerField(default=20)),
                ('tiempo_limite', models.PositiveIntegerField(default=30, help_text='Tiempo en minutos')),
                ('puntuacion_maxima', models.PositiveIntegerField(default=100)),
                ('nota_minima_aprobado', models.FloatField(default=5.0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('preguntas_aleatorias', models.BooleanField(default=True)),
                ('respuestas_aleatorias', models.BooleanField(default=True)),
                ('mostrar_resultados_inmediatos', models.BooleanField(default=False)),
                ('permitir_revision', models.BooleanField(default=True)),
                ('intentos_maximos', models.PositiveIntegerField(default=1)),
                ('fecha_inicio', models.DateTimeField(blank=True, null=True)),
                ('fecha_fin', models.DateTimeField(blank=True, null=True)),
                ('activo', models.BooleanField(default=False)),
                ('publicado', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categorias', models.ManyToManyField(blank=True, to='core.categoria')),
                ('creado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examenes_creados', to=settings.AUTH_USER_MODEL)),
                ('oposicion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.oposicion')),
                ('tema', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.tema')),
            ],
            options={
                'verbose_name': 'Examen',
                'verbose_name_plural': 'Exámenes',
                'ordering': ['-created_at'],
            },
        ),
        
        # Intentos de Examen
        migrations.CreateModel(
            name='IntentosExamen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True)),
                ('fecha_fin', models.DateTimeField(blank=True, null=True)),
                ('tiempo_empleado', models.DurationField(blank=True, null=True)),
                ('completado', models.BooleanField(default=False)),
                ('puntuacion_obtenida', models.FloatField(default=0)),
                ('porcentaje', models.FloatField(default=0)),
                ('aprobado', models.BooleanField(default=False)),
                ('preguntas_correctas', models.PositiveIntegerField(default=0)),
                ('preguntas_incorrectas', models.PositiveIntegerField(default=0)),
                ('preguntas_sin_responder', models.PositiveIntegerField(default=0)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='intentos_examenes', to=settings.AUTH_USER_MODEL)),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='intentos', to='core.examen')),
            ],
            options={
                'verbose_name': 'Intento de Examen',
                'verbose_name_plural': 'Intentos de Examen',
                'ordering': ['-fecha_inicio'],
            },
        ),
        
        # Preguntas en Examen
        migrations.CreateModel(
            name='PreguntaExamen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveIntegerField()),
                ('intento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preguntas_asignadas', to='core.intentosexamen')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.bancopregunta')),
            ],
            options={
                'verbose_name': 'Pregunta en Examen',
                'verbose_name_plural': 'Preguntas en Examen',
                'ordering': ['orden'],
            },
        ),
        
        # Respuestas de Estudiantes
        migrations.CreateModel(
            name='RespuestaEstudiante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo_respuesta', models.PositiveIntegerField(blank=True, help_text='Tiempo en segundos', null=True)),
                ('fecha_respuesta', models.DateTimeField(auto_now=True)),
                ('es_correcta', models.BooleanField(default=False)),
                ('intento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respuestas_dadas', to='core.intentosexamen')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.bancopregunta')),
                ('respuesta_seleccionada', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.respuestapregunta')),
            ],
            options={
                'verbose_name': 'Respuesta de Estudiante',
                'verbose_name_plural': 'Respuestas de Estudiantes',
            },
        ),
        
        # Estadísticas de Examen
        migrations.CreateModel(
            name='EstadisticasExamen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_intentos', models.PositiveIntegerField(default=0)),
                ('total_aprobados', models.PositiveIntegerField(default=0)),
                ('total_suspensos', models.PositiveIntegerField(default=0)),
                ('puntuacion_promedio', models.FloatField(default=0)),
                ('tiempo_promedio', models.DurationField(default=timedelta(0))),
                ('porcentaje_aprobados', models.FloatField(default=0)),
                ('puntuacion_maxima', models.FloatField(default=0)),
                ('puntuacion_minima', models.FloatField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('examen', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='estadisticas', to='core.examen')),
            ],
            options={
                'verbose_name': 'Estadísticas de Examen',
                'verbose_name_plural': 'Estadísticas de Exámenes',
            },
        ),
        
        # Constraints únicos
        migrations.AddConstraint(
            model_name='respuestapregunta',
            constraint=models.UniqueConstraint(fields=('pregunta', 'orden'), name='unique_pregunta_orden'),
        ),
        migrations.AddConstraint(
            model_name='preguntaexamen',
            constraint=models.UniqueConstraint(fields=('intento', 'orden'), name='unique_intento_orden'),
        ),
        migrations.AddConstraint(
            model_name='respuestaestudiante',
            constraint=models.UniqueConstraint(fields=('intento', 'pregunta'), name='unique_intento_pregunta'),
        ),
        migrations.AddConstraint(
            model_name='intentosexamen',
            constraint=models.UniqueConstraint(fields=('estudiante', 'examen', 'fecha_inicio'), name='unique_estudiante_examen_fecha'),
        ),
    ]