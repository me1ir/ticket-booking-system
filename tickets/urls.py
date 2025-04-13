from django.urls import path
from . import views

# app_name = 'tickets'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('movies/', views.movie_list, name='movie_list'),
    path('book/<int:showtime_id>/', views.seat_selection, name='seat_selection'),
    path('booking/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('rate_movie/<int:movie_id>/', views.rate_movie, name='rate_movie'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('booking/refund/<int:booking_id>/', views.refund_booking, name='refund_booking'),
    path('bookings/', views.user_bookings, name='user-bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('checkout/<int:booking_id>/', views.create_checkout_session, name='checkout'),

    path('success/', views.payment_success, name='payment-success'),
    path('cancel/', views.payment_cancel, name='payment-cancel'),
]
