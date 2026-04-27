from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import TenantRegistrationForm, LandlordRegistrationForm, PropertyForm, DocumentForm 
from .models import User, Property, PropertyImage, Favorite, Document, Review, Booking
from django.db.models import Q
from django.db import models
from datetime import date, timedelta
import re

def index(request):
    latest_properties = Property.objects.filter(moderation_status='approved').order_by('-published_at')[:6]
    return render(request, 'BlackApp/index.html', {'latest_properties': latest_properties})

## Профили и тп

def register_tenant(request):
    if request.method == 'POST':
        tenant_form = TenantRegistrationForm(request.POST)
        if tenant_form.is_valid():
            user = tenant_form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('index')
        else:
            # При ошибках заполнения возвращаем форму арендатора + пустую форму арендодателя
            landlord_form = LandlordRegistrationForm()
            return render(request, 'BlackApp/register.html', {
                'tenant_form': tenant_form,
                'landlord_form': landlord_form,
                'form_type': 'tenant'
            })
    else:
        tenant_form = TenantRegistrationForm()
        landlord_form = LandlordRegistrationForm()
        return render(request, 'BlackApp/register.html', {
            'tenant_form': tenant_form,
            'landlord_form': landlord_form,
            'form_type': 'tenant'
        })


def register_landlord(request):
    if request.method == 'POST':
        landlord_form = LandlordRegistrationForm(request.POST)
        if landlord_form.is_valid():
            user = landlord_form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('index')
        else:
            tenant_form = TenantRegistrationForm()
            return render(request, 'BlackApp/register.html', {
                'tenant_form': tenant_form,
                'landlord_form': landlord_form,
                'form_type': 'landlord'
            })
    else:
        tenant_form = TenantRegistrationForm()
        landlord_form = LandlordRegistrationForm()
        return render(request, 'BlackApp/register.html', {
            'tenant_form': tenant_form,
            'landlord_form': landlord_form,
            'form_type': 'landlord'
        })
    
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

@login_required
def profile(request):
    user = request.user
    context = {'user': user}

    if user.user_type == 'tenant':
        # Добавляем избранное
        favorites = Favorite.objects.filter(user=user).select_related('property')
        bookings = Booking.objects.filter(tenant=user).select_related('property')
        context.update({
            'favorites': favorites,
            'bookings': bookings,
        })
    elif user.user_type == 'landlord':
        properties = Property.objects.filter(owner=user)  
        incoming_bookings = Booking.objects.filter(property__owner=user).select_related('tenant', 'property')
        reviews = Review.objects.filter(landlord=user).select_related('author', 'property')
        documents = Document.objects.filter(user=user)
        context.update({
            'properties': properties, 
            'incoming_bookings': incoming_bookings,
            'reviews': reviews,
            'documents': documents,
        })

    return render(request, 'BlackApp/profile.html', context)

@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        request.user.avatar = request.FILES['avatar']
        request.user.save()
        messages.success(request, 'Аватар обновлён')
    return redirect('profile')

@login_required
def add_to_favorites(request, property_id):
    if request.user.user_type != 'tenant':
        messages.error(request, 'Только арендаторы могут добавлять в избранное')
        return redirect(request.META.get('HTTP_REFERER', 'profile'))
    
    property_obj = get_object_or_404(Property, id=property_id)
    Favorite.objects.get_or_create(user=request.user, property=property_obj)
    messages.success(request, 'Объект добавлен в избранное')
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def remove_from_favorites(request, property_id):
    favorite = get_object_or_404(Favorite, user=request.user, property_id=property_id)
    favorite.delete()
    messages.success(request, 'Объект удалён из избранного')
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        if user.user_type == 'landlord':
            user.birth_date = request.POST.get('birth_date') or None
        user.save()
        messages.success(request, 'Профиль обновлён')
        return redirect('profile')
    return redirect('profile')

# Документы и их свойства

@login_required
def upload_document(request):
    if request.user.user_type != 'landlord':
        messages.error(request, 'Только арендодатели могут загружать документы')
        return redirect('profile')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            messages.success(request, 'Документ загружен')
            return redirect('profile')
    else:
        form = DocumentForm()
    return render(request, 'BlackApp/upload_document.html', {'form': form})

@login_required
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, user=request.user)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Документ удалён')
    return redirect('profile')

# Объекты и их свойства

def apartment_list(request):
    properties = Property.objects.filter(moderation_status='approved').order_by('-published_at')

    address_query = request.GET.get('address', '').strip()
    if address_query:
        # 1. Убираем "г", "г.", "город" в начале
        normalized = re.sub(r'^(г|город)\.?\s*', '', address_query, flags=re.IGNORECASE)
        
        # 2. Словарь замен сокращений
        replacements = {
            'пр-кт': 'проспект',
            'пр-т': 'проспект',
            'просп': 'проспект',
            'ул': 'улица',
            'пер': 'переулок',
            'пл': 'площадь',
            'б-р': 'бульвар',
            'наб': 'набережная',
            'ш': 'шоссе',
        }
        for short, full in replacements.items():
            normalized = re.sub(r'\b' + re.escape(short) + r'\b', full, normalized, flags=re.IGNORECASE)
        
        # 3. Убираем лишние пробелы
        normalized = ' '.join(normalized.split())
        
        # 4. Ищем
        properties = properties.filter(
            Q(address__icontains=normalized) | Q(title__icontains=normalized)
        )
    property_type = request.GET.get('type')

    if property_type:
        properties = properties.filter(property_type=property_type)
    
    min_price = request.GET.get('min_price')
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    rooms = request.GET.get('rooms')
    if rooms:
        properties = properties.filter(rooms=rooms)
    
    context = {
        'properties': properties,
        'property_types': Property.PROPERTY_TYPES, 
    }
    return render(request, 'BlackApp/apartments.html', context)

def apartment_detail(request, id):
    property = get_object_or_404(Property, id=id, moderation_status='approved')
    property.views_count += 1
    property.save(update_fields=['views_count'])

    is_favorite = False
    if request.user.is_authenticated and request.user.user_type == 'tenant':
        is_favorite = Favorite.objects.filter(user=request.user, property=property).exists()

    confirmed_bookings = Booking.objects.filter(property=property, status='confirmed')
    booked_dates = set()
    for booking in confirmed_bookings:
        delta = booking.end_date - booking.start_date
        for i in range(delta.days + 1):
            day = booking.start_date + timedelta(days=i)
            booked_dates.add(day)

    booked_dates_str = [d.strftime('%Y-%m-%d') for d in booked_dates]

    context = {
        'property': property,
        'is_favorite': is_favorite,
        'booked_dates': booked_dates_str,
    }
    return render(request, 'BlackApp/apartment_detail.html', context)

@login_required
def add_property(request):
    if request.user.user_type != 'landlord':
        messages.error(request, 'Только арендодатели могут добавлять объекты')
        return redirect('index')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.moderation_status = 'pending' 
            property_obj.save()
            
            images = request.FILES.getlist('images')
            for i, img in enumerate(images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=img,
                    is_main=(i == 0)
                )
            
            property_obj.move_files_to_property_folder()
            return redirect('profile')
        else:
            messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = PropertyForm()
    
    return render(request, 'BlackApp/add_property.html', {'form': form})

@login_required
def edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            images = request.FILES.getlist('images')
            if images:
                for i, img in enumerate(images):
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=img,
                        is_main=(not property_obj.images.exists() and i == 0)
                    )
            property_obj.move_files_to_property_folder()
            return redirect('profile')
    else:
        form = PropertyForm(instance=property_obj)
    
    return render(request, 'BlackApp/edit_property.html', {'form': form, 'property': property_obj})

@login_required
def delete_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, 'Объект удалён')
    return redirect('profile')

@login_required
def edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.save() 
            delete_images = request.POST.getlist('delete_images')
            if delete_images:
                PropertyImage.objects.filter(id__in=delete_images, property=property_obj).delete()

            new_images = request.FILES.getlist('new_images')
            for i, img in enumerate(new_images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=img,
                    is_main=(not property_obj.images.exists() and i == 0) 
                )

            main_image_id = request.POST.get('main_image')
            if main_image_id:
                property_obj.images.update(is_main=False)
                PropertyImage.objects.filter(id=main_image_id, property=property_obj).update(is_main=True)

            messages.success(request, 'Объект успешно обновлён')
            return redirect('profile')
        else:
            messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'BlackApp/add_property.html', {
        'form': form,
        'property': property_obj
    })

# Бронирование и её свойства

@login_required
def create_booking(request, property_id):
    if request.user.user_type != 'tenant':
        messages.error(request, 'Только арендаторы могут бронировать')
        return redirect('apartment_detail', id=property_id)

    property_obj = get_object_or_404(Property, id=property_id, moderation_status='approved')

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        message = request.POST.get('message', '')

        if start_date >= end_date:
            messages.error(request, 'Дата выезда должна быть позже даты заезда')
            return render(request, 'BlackApp/create_booking.html', {'property': property_obj, 'today': date.today()})

        if start_date < str(date.today()):
            messages.error(request, 'Дата заезда не может быть в прошлом')
            return render(request, 'BlackApp/create_booking.html', {'property': property_obj, 'today': date.today()})

        # Проверка пересечений
        existing = Booking.objects.filter(
            property=property_obj,
            status='confirmed',
            start_date__lt=end_date,
            end_date__gt=start_date
        )
        if existing.exists():
            messages.error(request, 'Выбранные даты уже заняты')
            return render(request, 'BlackApp/create_booking.html', {'property': property_obj, 'today': date.today()})

        Booking.objects.create(
            tenant=request.user,
            property=property_obj,
            start_date=start_date,
            end_date=end_date,
            message=message,
            status='pending'
        )
        messages.success(request, 'Запрос на бронирование отправлен')
        return redirect('apartment_detail', id=property_id)

    return render(request, 'BlackApp/create_booking.html', {'property': property_obj, 'today': date.today()})

@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, property__owner=request.user)
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, 'Бронирование подтверждено')
    return redirect('profile')

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, property__owner=request.user)
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Бронирование отклонено')
    return redirect('profile')

@login_required
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, property__owner=request.user)
    if booking.status == 'confirmed':
        booking.status = 'completed'
        booking.save()
        messages.success(request, 'Бронирование завершено')
    return redirect('profile')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    if booking.status == 'pending' or booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Бронирование отменено')
    return redirect('profile')

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.tenant != request.user and booking.property.owner != request.user:
        messages.error(request, 'Нет прав на удаление')
        return redirect('profile')
    if booking.status not in ['cancelled', 'completed']:
        messages.error(request, 'Можно удалять только отменённые или завершённые брони')
        return redirect('profile')
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Бронирование удалено')
    return redirect('profile')

