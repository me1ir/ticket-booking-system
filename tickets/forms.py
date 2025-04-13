from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Booking, Seat, Movie


class MovieRatingForm(forms.Form):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]  # Только целые числа от 1 до 10

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label="Оцените фильм"
    )


class SeatSelectionForm(forms.Form):
    seats = forms.ModelMultipleChoiceField(
        queryset=Seat.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Выберите места"
    )

    def __init__(self, *args, **kwargs):
        showtime = kwargs.pop('showtime', None)
        available_seats = kwargs.pop('available_seats', None)
        super().__init__(*args, **kwargs)

        if showtime:
            self.fields['seats'].queryset = Seat.objects.filter(
                hall=showtime.hall,
                is_available=True
            )
        elif available_seats:
            self.fields['seats'].queryset = available_seats


class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'phone']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seats']
        widgets = {
            'seats': forms.NumberInput(attrs={'min': 1, 'max': 10})
        }
