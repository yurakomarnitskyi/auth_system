# Generated by Django 5.0 on 2024-01-02 20:35

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorites_id', models.CharField(max_length=50, unique=True)),
                ('saved_laptops', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10), size=None)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
