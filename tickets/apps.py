import os
from django.apps import AppConfig
from django.core.management import call_command

class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        if os.environ.get("RENDER"):
            try:
                call_command("loaddata", "movies.json")
                print("✅ Fixtures loaded on Render.")
            except Exception as e:
                print(f"❌ Error loading fixtures: {e}")
