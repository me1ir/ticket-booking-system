from .models import CustomUser, Movie, CinemaHall, ShowTime, Booking, Seat, Genre
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.urls import path  # Добавьте этот импорт
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from .models import CinemaHall, Seat
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.html import format_html
from .models import CinemaHall, Seat
from django.contrib import admin
from .models import Cinema  # Убедись, что импорт есть выше

@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')
    search_fields = ('name', 'address')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CinemaHall)
class CinemaHallAdmin(admin.ModelAdmin):
    list_display = ('name', 'rows', 'seats_per_row', 'seats_count', 'create_seats_link')
    actions = ['create_seats_action']

    def seats_count(self, obj):
        return obj.seat_set.count()

    seats_count.short_description = 'Кол-во мест'

    def create_seats_link(self, obj):
        url = reverse('admin:create_seats_for_hall', args=[obj.pk])
        return format_html('<a class="button" href="{}">Создать места</a>', url)

    create_seats_link.short_description = 'Действия'
    create_seats_link.allow_tags = True

    @admin.action(description='Создать места для выбранных залов')
    def create_seats_action(self, request, queryset):
        for hall in queryset:
            self._create_seats_for_hall(hall)
        self.message_user(request, f"Созданы места для {queryset.count()} залов")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/create_seats/',
                 self.admin_site.admin_view(self.create_seats_view),
                 name='create_seats_for_hall'),
        ]
        return custom_urls + urls

    def create_seats_view(self, request, object_id):
        hall = self.get_object(request, object_id)
        self._create_seats_for_hall(hall)
        self.message_user(request, f"Места созданы для зала {hall.name}")
        return redirect('..')

    def _create_seats_for_hall(self, hall):
        # Удаляем существующие места
        hall.seat_set.all().delete()

        # Создаем новые места
        for row in range(1, hall.rows + 1):
            for seat_num in range(1, hall.seats_per_row + 1):
                Seat.objects.create(
                    hall=hall,
                    row=row,
                    number=seat_num,
                    price=500.00,
                    is_available=True
                )


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


class MovieAdmin(admin.ModelAdmin):
    list_filter = ('genres', 'release_date')
    filter_horizontal = ('genres',)
    list_display = ('title', 'director', 'rating', 'release_date', 'poster_path')
    search_fields = ('title', 'director', 'actors')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('genres')


admin.site.register(Movie, MovieAdmin)


@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'formatted_start_time', 'formatted_end_time', 'formatted_price')
    list_filter = ('hall', 'movie')

    def formatted_start_time(self, obj):
        return obj.start_time.strftime('%d.%m.%Y %H:%M')

    formatted_start_time.short_description = 'Начало'

    def formatted_end_time(self, obj):
        return obj.end_time.strftime('%d.%m.%Y %H:%M')

    formatted_end_time.short_description = 'Окончание'

    def formatted_price(self, obj):
        return f"{obj.price} ₸"  # Форматирование цены с валютой

    formatted_price.short_description = 'Цена'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'showtime_info', 'seats_count', 'formatted_total_price')
    list_filter = ('booking_time',)
    search_fields = ('user__username', 'id')

    def showtime_info(self, obj):
        return f"{obj.showtime.movie.title} ({obj.showtime.start_time.strftime('%d.%m.%Y')})"

    showtime_info.short_description = 'Сеанс'

    def seats_count(self, obj):
        return obj.seats.count()

    seats_count.short_description = 'Кол-во мест'

    def formatted_total_price(self, obj):
        return f"{obj.total_price} ₸"

    formatted_total_price.short_description = 'Стоимость'


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('hall', 'row', 'number', 'is_available')
    list_filter = ('hall', 'is_available')
    search_fields = ('hall__name',)
