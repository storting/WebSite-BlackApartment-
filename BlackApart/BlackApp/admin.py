from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import User, TenantProfile, LandlordProfile, Property, PropertyImage, Document, Favorite, Booking, Review

# Inline для профилей
class TenantProfileInline(admin.StackedInline):
    model = TenantProfile
    can_delete = False
    fields = ['preferred_property_types', 'max_price', 'min_rooms', 'marital_status', 'has_children', 'employment', 'monthly_income']

class LandlordProfileInline(admin.StackedInline):
    model = LandlordProfile
    can_delete = False
    fields = ['is_verified', 'verified_by', 'verified_at', 'rating', 'reviews_count', 'balance', 'total_properties', 'active_properties']

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'is_blocked')
    list_filter = ('user_type', 'is_blocked', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('user_type', 'phone', 'avatar', 'birth_date', 'email_verified', 'is_blocked', 'block_reason')
        }),
    )
    actions = ['block_users', 'unblock_users', 'verify_users']

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'tenant':
                return [TenantProfileInline]
            elif obj.user_type == 'landlord':
                return [LandlordProfileInline]
        return []

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)
        self.message_user(request, f'{queryset.count()} пользователей заблокировано.')
    block_users.short_description = "Заблокировать выбранных пользователей"

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
        self.message_user(request, f'{queryset.count()} пользователей разблокировано.')
    unblock_users.short_description = "Разблокировать выбранных пользователей"

    def verify_users(self, request, queryset):
        # Для арендодателей ставим is_verified = True в LandlordProfile
        for user in queryset.filter(user_type='landlord'):
            if hasattr(user, 'landlord_profile'):
                user.landlord_profile.is_verified = True
                user.landlord_profile.verified_by = request.user
                user.landlord_profile.verified_at = timezone.now()
                user.landlord_profile.save()
        self.message_user(request, f'{queryset.count()} пользователей верифицировано.')
    verify_users.short_description = "Верифицировать выбранных арендодателей"

admin.site.register(User, CustomUserAdmin)

# Inline для изображений объекта
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'is_main', 'sort_order']

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'address', 'owner', 'price', 'moderation_status', 'created_at', 'views_count')
    list_filter = ('moderation_status', 'property_type', 'rooms', 'created_at')
    search_fields = ('title', 'address', 'description')
    list_editable = ('moderation_status',)
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Основное', {
            'fields': ('owner', 'title', 'description', 'address', 'property_type', 'price')
        }),
        ('Характеристики', {
            'fields': ('rooms', 'area', 'floor', 'floors_total')
        }),
        ('Удобства', {
            'fields': ('has_furniture', 'has_appliances', 'allows_pets', 'allows_children')
        }),
        ('Документы ЕГРН', {
            'fields': ('egrn_number', 'egrn_file', 'egrn_verified')
        }),
        ('Модерация', {
            'fields': ('moderation_status', 'moderator', 'moderation_comment', 'moderated_at')
        }),
        ('Статистика', {
            'fields': ('views_count', 'created_at', 'updated_at', 'published_at')
        }),
    )
    inlines = [PropertyImageInline]
    actions = ['approve_properties', 'reject_properties']

    def approve_properties(self, request, queryset):
        updated = queryset.update(moderation_status='approved', moderated_at=timezone.now(), moderator=request.user)
        self.message_user(request, f'{updated} объектов одобрено.')
    approve_properties.short_description = "Одобрить выбранные объекты"

    def reject_properties(self, request, queryset):
        updated = queryset.update(moderation_status='rejected', moderated_at=timezone.now(), moderator=request.user)
        self.message_user(request, f'{updated} объектов отклонено.')
    reject_properties.short_description = "Отклонить выбранные объекты"

admin.site.register(Property, PropertyAdmin)

# Регистрация остальных моделей (можно упростить)
admin.site.register(TenantProfile)
admin.site.register(LandlordProfile)
admin.site.register(PropertyImage)
admin.site.register(Document)
admin.site.register(Favorite)
admin.site.register(Booking)
admin.site.register(Review)