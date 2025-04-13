from django.test import TestCase
from tickets.models import Movie, Seat, CinemaHall, Cinema
from datetime import date

class MovieModelTest(TestCase):
    def test_str_representation(self):
        movie = Movie.objects.create(
            title="Inception",
            duration=148,
            release_date=date(2010, 7, 16)  # <-- добавили обязательное поле
        )
        self.assertEqual(str(movie), "Inception")
