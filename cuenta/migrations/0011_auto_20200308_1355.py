# Generated by Django 3.0.3 on 2020-03-08 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cuenta', '0010_empresa_emptelefono'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='solicitud',
            unique_together=set(),
        ),
    ]
