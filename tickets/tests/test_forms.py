from django.test import TestCase
from tickets.models import Cinema, CinemaHall, Movie, ShowTime, Seat
from tickets.forms import SeatSelectionForm
from datetime import datetime, timedelta

class SeatSelectionFormTest(TestCase):
    def setUp(self):
        self.cinema = Cinema.objects.create(
            name="Test Cinema",
            address="Test Address",
            latitude=0.0,
            longitude=0.0
        )
        self.hall = CinemaHall.objects.create(cinema=self.cinema, name="Hall 1", rows=5, seats_per_row=5)
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_date=datetime.today().date(),
            duration=120,
            director="Director",
            actors="Actor 1, Actor 2",
        )
        self.showtime = ShowTime.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=2),
            price=500
        )
        self.seat = Seat.objects.create(hall=self.hall, row=1, number=1, is_available=True)

    def test_valid_form(self):
        data = {
            'seats': [self.seat.id],
            'ticket_type': 'adult'
        }
        form = SeatSelectionForm(data=data, showtime=self.showtime)
        self.assertTrue(form.is_valid())
