# Generated by Django 3.0.3 on 2020-03-04 04:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuenta', '0003_auto_20200304_0130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='EmpRubro1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='EmpRubro1', to='cuenta.rubro'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='EmpRubro2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='EmpRubro2', to='cuenta.rubro'),
        ),
    ]
