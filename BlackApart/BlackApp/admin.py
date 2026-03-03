from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TenantProfile, LandlordProfile, Property, PropertyImage, Document, Favorite, ViewingRequest, Review

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'is_blocked')
    list_filter = ('user_type', 'is_blocked', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('user_type', 'phone', 'avatar', 'birth_date', 'email_verified', 'is_blocked', 'block_reason')
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(TenantProfile)
admin.site.register(LandlordProfile)
admin.site.register(Property)
admin.site.register(PropertyImage)
admin.site.register(Document)
admin.site.register(Favorite)
admin.site.register(ViewingRequest)
admin.site.register(Review)