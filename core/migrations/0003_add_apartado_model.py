# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_tema_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apartado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre del apartado', max_length=200)),
                ('descripcion', models.TextField(blank=True, help_text='Descripción del apartado')),
                ('orden', models.PositiveIntegerField(default=0, help_text='Orden de aparición en el tema')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tema', models.ForeignKey(help_text='Tema al que pertenece este apartado', on_delete=django.db.models.deletion.CASCADE, related_name='apartados', to='core.tema')),
            ],
            options={
                'verbose_name_plural': 'Apartados',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='apartado',
            unique_together={('tema', 'nombre')},
        ),
    ]