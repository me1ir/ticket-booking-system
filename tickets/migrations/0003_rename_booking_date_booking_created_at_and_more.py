# Generated by Django 5.1.7 on 2025-03-30 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_movie_slug_alter_movie_duration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='booking_date',
            new_name='created_at',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='qr_code',
        ),
        migrations.AddField(
            model_name='booking',
            name='ticket_code',
            field=models.CharField(default='TEMP-CODE', max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name='showtime',
            name='available_seats',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='booking',
            name='seats',
            field=models.PositiveIntegerField(),
        ),
    ]
