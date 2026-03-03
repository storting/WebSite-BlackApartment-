from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, TenantProfile, LandlordProfile
import json

class TenantRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=16, required=True, label='Телефон')
    first_name = forms.CharField(max_length=150, required=True, label='Имя')
    last_name = forms.CharField(max_length=150, required=True, label='Фамилия')

    preferred_property_types = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '["apartment", "house"]'}),
        required=False,
        label='Предпочитаемые типы жилья (JSON-список)',
        help_text='Введите JSON-список, например: ["apartment", "house"]'
    )
    max_price = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label='Максимальная цена')
    min_rooms = forms.IntegerField(required=False, label='Минимум комнат')
    marital_status = forms.ChoiceField(
        choices=TenantProfile._meta.get_field('marital_status').choices,
        required=False,
        label='Семейное положение'
    )
    has_children = forms.BooleanField(required=False, label='Есть дети')
    employment = forms.CharField(max_length=200, required=False, label='Место работы')
    monthly_income = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Ежемесячный доход')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'tenant'
        user.phone = self.cleaned_data['phone']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            tenant_profile, created = TenantProfile.objects.get_or_create(user=user)
            # Сохраняем JSON-строку
            preferred = self.cleaned_data.get('preferred_property_types')
            if preferred:
                try:
                    # Проверяем, что это валидный JSON
                    json.loads(preferred)
                    tenant_profile.preferred_property_types = preferred
                except json.JSONDecodeError:
                    tenant_profile.preferred_property_types = '[]'
            else:
                tenant_profile.preferred_property_types = '[]'
            tenant_profile.max_price = self.cleaned_data.get('max_price')
            tenant_profile.min_rooms = self.cleaned_data.get('min_rooms')
            tenant_profile.marital_status = self.cleaned_data.get('marital_status')
            tenant_profile.has_children = self.cleaned_data.get('has_children')
            tenant_profile.employment = self.cleaned_data.get('employment')
            tenant_profile.monthly_income = self.cleaned_data.get('monthly_income')
            tenant_profile.save()
        return user


class LandlordRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=16, required=True, label='Телефон')
    first_name = forms.CharField(max_length=150, required=True, label='Имя')
    last_name = forms.CharField(max_length=150, required=True, label='Фамилия')
    birth_date = forms.DateField(
        required=True,
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2', 'birth_date')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'landlord'
        user.phone = self.cleaned_data['phone']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.birth_date = self.cleaned_data['birth_date']
        if commit:
            user.save()
            LandlordProfile.objects.get_or_create(user=user)
        return user