# Generated manually for removing peso_evaluacion and es_obligatorio fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tema',
            name='es_obligatorio',
        ),
        migrations.RemoveField(
            model_name='tema',
            name='peso_evaluacion',
        ),
    ]