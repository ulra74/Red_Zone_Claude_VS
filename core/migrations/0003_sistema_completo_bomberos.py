from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_sistema_evaluaciones'),
    ]

    operations = [
        # Ejercicios Físicos
        migrations.CreateModel(
            name='EjercicioFisico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('categoria', models.CharField(choices=[
                    ('resistencia', 'Resistencia'),
                    ('fuerza', 'Fuerza'),
                    ('velocidad', 'Velocidad'),
                    ('agilidad', 'Agilidad'),
                    ('flexibilidad', 'Flexibilidad'),
                    ('natacion', 'Natación'),
                    ('escalada', 'Escalada')
                ], max_length=20)),
                ('descripcion', models.TextField()),
                ('instrucciones', models.TextField(blank=True)),
                ('video_demostrativo', models.FileField(blank=True, null=True, upload_to='ejercicios/videos/')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='ejercicios/imagenes/')),
                ('tiempo_objetivo_hombre', models.DurationField(blank=True, null=True)),
                ('tiempo_objetivo_mujer', models.DurationField(blank=True, null=True)),
                ('repeticiones_objetivo', models.IntegerField(blank=True, null=True)),
                ('distancia_objetivo', models.FloatField(blank=True, help_text='En metros', null=True)),
                ('peso_objetivo', models.FloatField(blank=True, help_text='En kg', null=True)),
                ('baremo_excelente', models.CharField(blank=True, max_length=100)),
                ('baremo_bueno', models.CharField(blank=True, max_length=100)),
                ('baremo_aceptable', models.CharField(blank=True, max_length=100)),
                ('baremo_insuficiente', models.CharField(blank=True, max_length=100)),
                ('es_obligatorio_bomberos', models.BooleanField(default=False)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Ejercicio Físico',
                'verbose_name_plural': 'Ejercicios Físicos',
                'ordering': ['orden', 'nombre'],
            },
        ),
        
        # Planes de Entrenamiento
        migrations.CreateModel(
            name='PlanEntrenamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('tipo_plan', models.CharField(choices=[
                    ('principiante', 'Principiante'),
                    ('intermedio', 'Intermedio'),
                    ('avanzado', 'Avanzado'),
                    ('precompeticion', 'Pre-competición'),
                    ('mantenimiento', 'Mantenimiento')
                ], default='principiante', max_length=20)),
                ('fase_actual', models.CharField(choices=[
                    ('base', 'Fase Base'),
                    ('desarrollo', 'Fase de Desarrollo'),
                    ('pico', 'Pico de Forma'),
                    ('mantenimiento', 'Mantenimiento'),
                    ('recuperacion', 'Recuperación')
                ], default='base', max_length=20)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('fecha_examen_objetivo', models.DateField(blank=True, null=True)),
                ('dias_entrenamiento_semana', models.IntegerField(default=5)),
                ('duracion_sesion_minutos', models.IntegerField(default=90)),
                ('objetivo_principal', models.TextField()),
                ('objetivos_secundarios', models.TextField(blank=True)),
                ('activo', models.BooleanField(default=True)),
                ('completado', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planes_entrenamiento', to='accounts.customuser')),
            ],
            options={
                'verbose_name': 'Plan de Entrenamiento',
                'verbose_name_plural': 'Planes de Entrenamiento',
                'ordering': ['-created_at'],
            },
        ),
        
        # Sistema de Gamificación
        migrations.CreateModel(
            name='Logro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('icono', models.CharField(help_text='Icono de Bootstrap Icons', max_length=50)),
                ('color', models.CharField(default='#007bff', help_text='Color hexadecimal', max_length=7)),
                ('tipo', models.CharField(choices=[
                    ('estudio', 'Estudio'),
                    ('fisico', 'Físico'),
                    ('examenes', 'Exámenes'),
                    ('constancia', 'Constancia'),
                    ('social', 'Social'),
                    ('especial', 'Especial')
                ], max_length=20)),
                ('criterio_json', models.JSONField(help_text='Criterios en formato JSON')),
                ('puntos', models.IntegerField(default=100)),
                ('es_secreto', models.BooleanField(default=False)),
                ('activo', models.BooleanField(default=True)),
                ('orden', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Logro',
                'verbose_name_plural': 'Logros',
                'ordering': ['orden', 'nombre'],
            },
        ),
        
        migrations.CreateModel(
            name='PuntuacionUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntos_totales', models.IntegerField(default=0)),
                ('puntos_mes_actual', models.IntegerField(default=0)),
                ('puntos_semana_actual', models.IntegerField(default=0)),
                ('puntos_estudio', models.IntegerField(default=0)),
                ('puntos_examenes', models.IntegerField(default=0)),
                ('puntos_fisico', models.IntegerField(default=0)),
                ('puntos_constancia', models.IntegerField(default=0)),
                ('puntos_social', models.IntegerField(default=0)),
                ('racha_dias_consecutivos', models.IntegerField(default=0)),
                ('racha_maxima', models.IntegerField(default=0)),
                ('ultimo_dia_actividad', models.DateField(blank=True, null=True)),
                ('nivel', models.IntegerField(default=1)),
                ('experiencia_actual', models.IntegerField(default=0)),
                ('experiencia_siguiente_nivel', models.IntegerField(default=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='puntuacion', to='accounts.customuser')),
            ],
            options={
                'verbose_name': 'Puntuación de Usuario',
                'verbose_name_plural': 'Puntuaciones de Usuario',
                'ordering': ['-puntos_totales'],
            },
        ),
    ]
