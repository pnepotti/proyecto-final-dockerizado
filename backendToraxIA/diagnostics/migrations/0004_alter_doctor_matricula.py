# Generated by Django 5.1.1 on 2024-10-12 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnostics', '0003_doctor_matricula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='matricula',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
