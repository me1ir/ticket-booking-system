from django.test import TestCase
from django.contrib.auth import get_user_model
from tickets.models import Movie, Cinema, CinemaHall, Seat, ShowTime, Booking
from datetime import datetime, date, timedelta

User = get_user_model()

class BookingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.cinema = Cinema.objects.create(name="Cinema1", address="123 Street", latitude=0.0, longitude=0.0)
        self.hall = CinemaHall.objects.create(cinema=self.cinema, name="Hall 1", rows=5, seats_per_row=5)
        self.movie = Movie.objects.create(
            title="Matrix",
            description="Sci-fi action",
            director="Wachowski",
            actors="Keanu Reeves, Laurence Fishburne",
            release_date=date.today(),  # 👈 добавляем обязательную дату!
            duration=120,
            rating=8.7,
            vote_count=100,
            poster=None  # или добавь фиктивный файл, если требуется
        )
        self.showtime = ShowTime.objects.create(
            movie=self.movie,
            hall=self.hall,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=2),
            price=1500
        )
        self.seat = Seat.objects.create(hall=self.hall, row=1, number=1, is_available=True)

    def test_booking_creation(self):
        booking = Booking.objects.create(user=self.user, showtime=self.showtime)
        booking.seats.add(self.seat)
        self.assertEqual(booking.seats.count(), 1)
