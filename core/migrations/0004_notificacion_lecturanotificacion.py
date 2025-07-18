# Generated by Django 5.0.14 on 2025-07-18 16:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_examentestresultado_examen_signature'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(help_text='Título de la notificación', max_length=200)),
                ('mensaje', models.TextField(help_text='Contenido del mensaje')),
                ('tipo', models.CharField(choices=[('info', 'Información'), ('important', 'Importante'), ('urgent', 'Urgente'), ('exam', 'Examen'), ('file', 'Nuevo Archivo'), ('general', 'General')], default='info', help_text='Tipo de notificación', max_length=20)),
                ('es_urgente', models.BooleanField(default=False, help_text='Notificación urgente (aparece destacada)')),
                ('requiere_confirmacion', models.BooleanField(default=False, help_text='Requiere que el estudiante confirme haber leído')),
                ('enlace_url', models.URLField(blank=True, help_text='URL opcional para más información')),
                ('enlace_texto', models.CharField(blank=True, help_text='Texto para el enlace', max_length=100)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_expiracion', models.DateTimeField(blank=True, help_text='Fecha después de la cual la notificación no se muestra', null=True)),
                ('activa', models.BooleanField(default=True, help_text='Si la notificación está activa')),
                ('enviado_por', models.ForeignKey(help_text='Administrador que envía la notificación', limit_choices_to={'user_type': 'admin'}, on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones_enviadas', to=settings.AUTH_USER_MODEL)),
                ('oposicion', models.ForeignKey(help_text='Oposición a cuyos estudiantes se envía la notificación', on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to='core.oposicion')),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='LecturaNotificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_lectura', models.DateTimeField(auto_now_add=True)),
                ('confirmada', models.BooleanField(default=False, help_text='Si el usuario confirmó haber leído (para notificaciones importantes)')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones_leidas', to=settings.AUTH_USER_MODEL)),
                ('notificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lecturas', to='core.notificacion')),
            ],
            options={
                'verbose_name': 'Lectura de Notificación',
                'verbose_name_plural': 'Lecturas de Notificaciones',
                'ordering': ['-fecha_lectura'],
                'unique_together': {('notificacion', 'usuario')},
            },
        ),
    ]
