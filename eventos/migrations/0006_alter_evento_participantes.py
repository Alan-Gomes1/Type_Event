# Generated by Django 4.2.1 on 2023-05-30 19:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eventos', '0005_evento_participantes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='participantes',
            field=models.ManyToManyField(blank=True, related_name='participantes', to=settings.AUTH_USER_MODEL),
        ),
    ]
