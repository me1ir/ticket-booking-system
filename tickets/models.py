from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from io import BytesIO
import qrcode
from django.core.files.base import ContentFile


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)


class Cinema(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class CinemaHall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='halls')
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField(default=10)
    seats_per_row = models.PositiveIntegerField(default=15)

    def __str__(self):
        return f"{self.cinema.name} - {self.name}"


class Seat(models.Model):
    hall = models.ForeignKey('CinemaHall', on_delete=models.CASCADE)
    row = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    seat_type = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('vip', 'VIP')],
        default='standard'
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=500.00,
        verbose_name="Цена места (₸)"
    )

    class Meta:
        unique_together = ('hall', 'row', 'number')

    def __str__(self):
        return f"Ряд {self.row}, Место {self.number} ({self.seat_type})"


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']

    def get_movies_count(self):
        return self.movie_set.count()


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    genres = models.ManyToManyField('Genre')
    director = models.CharField(max_length=100)
    actors = models.TextField(help_text="Перечисление через запятую")

    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        verbose_name="Рейтинг фильма"
    )
    vote_count = models.PositiveIntegerField(default=0)
    release_date = models.DateField()
    duration = models.PositiveIntegerField(help_text="Длительность в минутах")
    poster_path = models.CharField(max_length=200, help_text="Path to static image like 'tickets/posters/matrix.jpg'")
    slug = models.SlugField(blank=True, unique=True)
    trailer_url = models.URLField(blank=True, null=True, help_text="Ссылка на трейлер YouTube")

    def update_rating(self, new_rating):
        self.vote_count += 1
        total_rating = (self.rating * (self.vote_count - 1)) + new_rating
        self.rating = round(total_rating / self.vote_count, 1)
        self.save(update_fields=['rating', 'vote_count'])

    def get_trailer_embed_url(self):
        if self.trailer_url and "watch?v=" in self.trailer_url:
            return self.trailer_url.replace("watch?v=", "embed/").split("&")[0]
        return self.trailer_url

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ShowTime(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    hall = models.ForeignKey('CinemaHall', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=500.00,
        verbose_name="Цена билета (₸)"
    )

    def __str__(self):
        return f"{self.movie.title} в {self.start_time.strftime('%d.%m.%Y %H:%M')}"


class Booking(models.Model):
    showtime = models.ForeignKey('ShowTime', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seats = models.ManyToManyField('Seat')
    booking_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Общая стоимость"
    )
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_refunded = models.BooleanField(default=False, verbose_name="Возвращен?")

    def __str__(self):
        return f"Бронь #{self.id}" if self.id else "Новая бронь"

    def generate_qr_code(self):
        qr_data = f"Фильм: {self.showtime.movie.title}\n"
        qr_data += f"Дата: {self.showtime.start_time.strftime('%d.%m.%Y %H:%M')}\n"
        qr_data += f"Кинотеатр: {self.showtime.hall.cinema.name}, Зал: {self.showtime.hall.name}\n"
        qr_data += "Места:\n"

        for ticket in self.tickets.all():
            qr_data += f" - Ряд {ticket.seat.row} Место {ticket.seat.number} ({ticket.get_ticket_type_display()})\n"

        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        file_name = f'qr_{self.id}.png'
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)


class Ticket(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='tickets')
    seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
    ticket_type = models.CharField(max_length=10, choices=[
        ('adult', 'Взрослый'),
        ('student', 'Студенческий'),
        ('child', 'Детский'),
    ])

    def __str__(self):
        return f"{self.seat} — {self.get_ticket_type_display()}"
