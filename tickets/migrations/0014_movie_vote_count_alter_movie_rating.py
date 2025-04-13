# Generated by Django 5.1.7 on 2025-04-02 06:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0013_genre_alter_movie_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='vote_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='movie',
            name='rating',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)], verbose_name='Рейтинг фильма'),
        ),
    ]
