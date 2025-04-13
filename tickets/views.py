from .forms import RegisterForm, BookingForm
import random
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Movie, ShowTime, Booking, Genre
from .forms import BookingForm
from django.shortcuts import render, get_object_or_404
from .models import ShowTime, Seat
from .forms import SeatSelectionForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import ShowTime, Seat, Booking
from django.db import transaction
from .forms import SeatSelectionForm
from django.db.models import Count
from django.shortcuts import redirect
from django.contrib.auth import logout
from .forms import RegisterForm  # Вместо CustomUserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Movie
from .forms import MovieRatingForm
from django.shortcuts import render
from .models import Movie  # Убедись, что импортировал модель Movie
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Booking
# views.py
import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Booking
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # ✅ Проверка на пустую сумму
    if booking.total_price == 0:
        messages.error(request, "Сумма брони равна 0 — нельзя оплатить.")
        return redirect('home')

    # 🔒 Создание Stripe-сессии
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Билет на {booking.showtime.movie.title}',
                },
                'unit_amount': int(booking.total_price * 100),  # в центах!
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
    )

    print("Redirecting to Stripe session:", session.url)  # для отладки

    return redirect(session.url, code=303)


def payment_success(request):
    return render(request, 'tickets/success.html')

def payment_cancel(request):
    return render(request, 'tickets/cancel.html')


def checkout_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'tickets/checkout.html', {'booking': booking})


@login_required
def refund_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.is_refunded:
        messages.error(request, "Этот билет уже был возвращен.")
    else:
        # Логика возврата, например, отмена платежа через API (например, Stripe)
        # Здесь можно вставить код для обработки возврата через платежную систему

        # Обновляем статус брони
        booking.is_refunded = True
        booking.save()

        messages.success(request, "Ваш билет успешно возвращен.")

    return redirect('profile')  # Перенаправление на страницу профиля или на страницу с деталями брони


def logout_view(request):
    """Функция выхода пользователя"""
    logout(request)
    return redirect('home')  # Перенаправляем на главную


def home(request):
    movies = Movie.objects.all()[:4]  # Выводим 4 фильма на главную
    return render(request, 'tickets/home.html', {'movies': movies})


@login_required
def rate_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        form = MovieRatingForm(request.POST)
        if form.is_valid():
            new_rating = int(form.cleaned_data['rating'])  # Преобразуем в int
            movie.update_rating(new_rating)  # Обновляем рейтинг
            messages.success(request, 'Спасибо за вашу оценку!')
            return redirect('movie_detail', movie_id=movie.id)  # Перенаправляем обратно на фильм
    else:
        form = MovieRatingForm()

    return render(request, 'tickets/rate_movie.html', {'form': form, 'movie': movie})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Booking


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    return render(request, 'tickets/booking_confirmation.html', {
        'booking': booking,
        'qr_code_url': booking.qr_code.url if booking.qr_code else None
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)  # Используем RegisterForm
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход
            return redirect('home')  # Перенаправление на главную
    else:
        form = RegisterForm()

    return render(request, 'tickets/register.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Movie, ShowTime



from .models import Movie, Genre, Cinema
from django.db.models import Count

def movie_list(request):
    movies = Movie.objects.prefetch_related('genres').all()
    query = request.GET.get('q')
    genre_id = request.GET.get('genre')
    cinema_id = request.GET.get('cinema')
    sort_by = request.GET.get('sort_by', '-release_date')

    # Фильтрация по поиску
    if query:
        movies = movies.filter(title__icontains=query)

    # Фильтрация по жанру
    if genre_id:
        movies = movies.filter(genres__id=genre_id).distinct()

    # 🔥 Фильтрация по кинотеатру (по связанной модели через ShowTime → Hall → Cinema)
    if cinema_id:
        movies = movies.filter(showtime__hall__cinema_id=cinema_id).distinct()

    # Сортировка
    SORT_OPTIONS = {
        'title': 'title',
        '-title': '-title',
        'rating': 'rating',
        '-rating': '-rating',
        'release_date': 'release_date',
        '-release_date': '-release_date',
    }
    movies = movies.order_by(SORT_OPTIONS.get(sort_by, '-release_date'))

    # Получаем жанры и кинотеатры
    genres = Genre.objects.annotate(movie_count=Count('movie')).filter(movie_count__gt=0).order_by('-movie_count', 'name')
    all_cinemas = Cinema.objects.all()

    context = {
        'movies': movies,
        'query': query,
        'selected_genre': genre_id,
        'selected_sort': sort_by,
        'genres': genres,
        'all_cinemas': all_cinemas,
    }
    view = request.GET.get('view', 'grid')  # по умолчанию плитка
    context['view'] = view

    return render(request, 'tickets/movie_list.html', context)


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie.objects.prefetch_related('genres'), id=movie_id)
    showtimes = ShowTime.objects.filter(movie=movie).select_related('hall').order_by('start_time')

    # Форматируем список актеров
    movie.actors = movie.actors.replace(',', ', ')

    return render(request, 'tickets/movie_detail.html', {
        'movie': movie,
        'showtimes': showtimes
    })

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'tickets/profile.html', {'bookings': bookings})


# Добавляем недостающее представление
@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'tickets/user_bookings.html', {'bookings': bookings})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'tickets/booking_detail.html', {'booking': booking})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from .models import Movie, ShowTime, Booking, Seat, Genre, Ticket
from .forms import SeatSelectionForm, MovieRatingForm, RegisterForm

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import ShowTime, Seat, Booking, Ticket
from .forms import SeatSelectionForm

@login_required
@transaction.atomic
def seat_selection(request, showtime_id):
    showtime = get_object_or_404(ShowTime, id=showtime_id)

    if request.method == 'POST':
        print("📨 Получен POST-запрос на бронирование")
        print("POST данные:", request.POST)

        form = SeatSelectionForm(request.POST, showtime=showtime)

        if form.is_valid():
            print("✅ Форма валидна")
            selected_seats = form.cleaned_data['seats']

            # Проверка доступности
            unavailable_seats = selected_seats.filter(is_available=False)
            if unavailable_seats.exists():
                messages.error(request, f"Некоторые места уже заняты: {', '.join(str(s) for s in unavailable_seats)}")
                return redirect('seat_selection', showtime_id=showtime_id)

            booking = Booking.objects.create(
                user=request.user,
                showtime=showtime,
                total_price=0
            )

            total_price = Decimal('0.0')

            for seat in selected_seats:
                ticket_type = request.POST.get(f'seat_type_{seat.id}', 'adult')
                print(f"🎟 Место {seat.id} — тип: {ticket_type}")

                Ticket.objects.create(
                    booking=booking,
                    seat=seat,
                    ticket_type=ticket_type
                )

                discount = {
                    'adult': Decimal('1.0'),
                    'student': Decimal('0.7'),
                    'child': Decimal('0.5')
                }
                multiplier = discount.get(ticket_type, Decimal('1.0'))
                total_price += seat.price * multiplier

                seat.is_available = False
                seat.save()

            booking.total_price = total_price

            # Генерация QR-кода с полной информацией
            booking.generate_qr_code()

            booking.save()

            print("✅ Бронирование сохранено. Переход к оплате.")
            return redirect('checkout', booking_id=booking.id)

        else:
            print("❌ Форма НЕвалидна:")
            print(form.errors)

    else:
        form = SeatSelectionForm(showtime=showtime)

    seats = Seat.objects.filter(hall=showtime.hall).order_by('row', 'number')
    rows = {}
    for seat in seats:
        rows.setdefault(seat.row, []).append(seat)

    return render(request, 'tickets/seat_selection.html', {
        'showtime': showtime,
        'form': form,
        'rows': rows
    })
