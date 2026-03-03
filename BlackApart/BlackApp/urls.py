from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/tenant/', views.register_tenant, name='register_tenant'),
    path('register/landlord/', views.register_landlord, name='register_landlord'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('apartments/', views.apartment_list, name='apartment_list'), 
    path('apartment/<int:id>/', views.apartment_detail, name='apartment_detail'), 
]