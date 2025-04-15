# dump_movies.py
import os
import django
import json
from django.core.serializers import serialize

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_booking_system.settings')
django.setup()

from tickets.models import Movie

data = serialize('json', Movie.objects.all(), indent=2)

with open('tickets/fixtures/movies.json', 'w', encoding='utf-8') as f:
    f.write(data)
