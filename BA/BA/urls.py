from django.contrib import admin
from django.urls import path
from WebSite import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.mainPage, name='home'),
    path('login', views.AuthorizationPage),
    path('reg', views.RegistrationPage),

]
