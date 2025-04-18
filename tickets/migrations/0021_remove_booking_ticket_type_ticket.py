# Generated by Django 5.1.7 on 2025-04-13 10:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0020_booking_ticket_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='ticket_type',
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_type', models.CharField(choices=[('adult', 'Взрослый'), ('student', 'Студенческий'), ('child', 'Детский')], max_length=10)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='tickets.booking')),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.seat')),
            ],
        ),
    ]
