from django.urls import path
from . import views

urlpatterns = [
    # Главная
    path('', views.index, name='index'),

    # Регистрация и аутентификация
    path('register/tenant/', views.register_tenant, name='register_tenant'),
    path('register/landlord/', views.register_landlord, name='register_landlord'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профиль и связанные действия
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/upload-avatar/', views.upload_avatar, name='upload_avatar'),

    # Объекты недвижимости (для арендодателя)
    path('add-property/', views.add_property, name='add_property'),
    path('property/edit/<int:property_id>/', views.edit_property, name='edit_property'),
    path('property/delete/<int:property_id>/', views.delete_property, name='delete_property'),

    # Избранное (для арендатора)
    path('favorites/add/<int:property_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:property_id>/', views.remove_from_favorites, name='remove_from_favorites'),

    # Бронирование
    path('booking/create/<int:property_id>/', views.create_booking, name='create_booking'),
    path('booking/confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('booking/reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('booking/complete/<int:booking_id>/', views.complete_booking, name='complete_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),

    # Документы (для арендодателя)
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/delete/<int:doc_id>/', views.delete_document, name='delete_document'),

    # Список квартир и детальная страница (публичные)
    path('apartments/', views.apartment_list, name='apartment_list'),
    path('apartment/<int:id>/', views.apartment_detail, name='apartment_detail'),
]