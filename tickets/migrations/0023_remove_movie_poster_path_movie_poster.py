# Generated by Django 5.1.7 on 2025-04-15 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0022_remove_movie_poster_movie_poster_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='poster_path',
        ),
        migrations.AddField(
            model_name='movie',
            name='poster',
            field=models.ImageField(default='posters/default.jpg', upload_to='posters/'),
        ),
    ]
