# Generated manually for Pregunta and Respuesta models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_apartado_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enunciado', models.TextField(help_text='Texto de la pregunta')),
                ('texto_aclaratorio', models.TextField(blank=True, help_text='Explicación que se mostrará después de responder (opcional)')),
                ('dificultad', models.CharField(choices=[('facil', 'Fácil'), ('medio', 'Medio'), ('dificil', 'Difícil')], default='medio', help_text='Nivel de dificultad de la pregunta', max_length=10)),
                ('puntos', models.PositiveIntegerField(default=1, help_text='Puntos que vale la pregunta')),
                ('orden', models.PositiveIntegerField(default=0, help_text='Orden de aparición en el apartado')),
                ('activa', models.BooleanField(default=True, help_text='Si la pregunta está activa para usar en exámenes')),
                ('veces_preguntada', models.PositiveIntegerField(default=0, help_text='Número de veces que se ha usado en exámenes')),
                ('veces_acertada', models.PositiveIntegerField(default=0, help_text='Número de veces que se ha respondido correctamente')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('apartado', models.ForeignKey(help_text='Apartado al que pertenece esta pregunta', on_delete=django.db.models.deletion.CASCADE, related_name='preguntas', to='core.apartado')),
            ],
            options={
                'verbose_name_plural': 'Preguntas',
                'ordering': ['orden', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField(help_text='Texto de la respuesta')),
                ('es_correcta', models.BooleanField(default=False, help_text='Marcar si esta es la respuesta correcta')),
                ('orden', models.PositiveIntegerField(default=0, help_text='Orden de aparición en la pregunta')),
                ('explicacion', models.TextField(blank=True, help_text='Explicación adicional para esta respuesta (opcional)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pregunta', models.ForeignKey(help_text='Pregunta a la que pertenece esta respuesta', on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to='core.pregunta')),
            ],
            options={
                'verbose_name_plural': 'Respuestas',
                'ordering': ['orden', 'created_at'],
            },
        ),
    ]