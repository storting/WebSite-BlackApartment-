from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import TenantRegistrationForm, LandlordRegistrationForm
from .models import User

def index(request):
    return render(request, 'BlackApp/index.html')

def apartment_list(request):
    return render(request, 'BlackApp/apartments.html')

def apartment_detail(request, id):
    return render(request, 'BlackApp/apartment_detail.html')

def register_tenant(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('index')
        else:
            return render(request, 'BlackApp/register.html', {'form': form, 'form_type': 'tenant'})
    else:
        form = TenantRegistrationForm()
        return render(request, 'BlackApp/register.html', {'form': form, 'form_type': 'tenant'})

def register_landlord(request):
    if request.method == 'POST':
        form = LandlordRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('index')
        else:
            return render(request, 'BlackApp/register.html', {'form': form, 'form_type': 'landlord'})
    else:
        form = LandlordRegistrationForm()
        return render(request, 'BlackApp/register.html', {'form': form, 'form_type': 'landlord'})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'С возвращением, {user.username}!')
            print(f'С возвращением, {user.username}!')
            return redirect('index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
            print(f'Неверное имя пользователя или пароль {username, password}')
    return render(request, 'BlackApp/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('index')

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Пожалуйста, войдите, чтобы увидеть профиль')
        return redirect('login')
    return render(request, 'BlackApp/profile.html', {'user': request.user})