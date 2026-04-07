import os, re, shutil
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.core.files import File
from io import BytesIO
from django.utils import timezone
from PIL import Image as PilImage
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings

class User(AbstractUser):
    USER_TYPES = (
        ('tenant', 'Арендатор'),          # Ищет жилье
        ('landlord', 'Арендодатель'),      # Сдает жилье
        ('moderator', 'Модератор'),        # Проверяет объявления и документы
        ('admin', 'Администратор'),        # Управляет системой
    )
    
    # Основные поля (для всех ролей)
    user_type = models.CharField(
        'Тип пользователя', 
        max_length=20, 
        choices=USER_TYPES, 
        default='tenant',
        db_index=True  # Индекс для быстрого поиска (SYS-NFR-01)
    )
    
    # Валидация телефона (SYS-NFR-06)
    phone_regex = RegexValidator(
        regex=r'^\+?7?\d{10,15}$',
        message="Телефон должен быть в формате: '+79991234567' или '89991234567'"
    )
    phone = models.CharField(
        'Телефон', 
        max_length=16, 
        validators=[phone_regex],
        unique=True,  # Телефон должен быть уникальным
        db_index=True,
        blank=True, 
        null=True
    )
    
    # Email уже есть в AbstractUser, добавим индекс для быстрого поиска
    email = models.EmailField('Email', db_index=True, unique=True)
    
    # Аватар
    avatar = models.ImageField('Аватар', upload_to='avatars/', null=True, blank=True)
    
    # Дата регистрации (для аналитики)
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)
    
    # Последняя активность (для мониторинга)
    last_activity = models.DateTimeField('Последняя активность', auto_now=True)
    
    # Блокировка пользователя (безопасность - SYS-NFR-03)
    is_blocked = models.BooleanField('Заблокирован', default=False)
    block_reason = models.TextField('Причина блокировки', blank=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['user_type', 'is_active']),
            models.Index(fields=['date_joined']),
        ]
        
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"
    
    def clean(self):
        """Дополнительная валидация (SYS-NFR-06)"""
        if self.user_type == 'landlord' and not self.phone:
            raise ValidationError('Арендодатель должен указать телефон')
    
    def get_full_name(self):
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        return self.username


class TenantProfile(models.Model):
    """
    Профиль арендатора (дополнительные поля для TAL)
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='tenant_profile',
        limit_choices_to={'user_type': 'tenant'}
    )
    
    # Предпочтения по жилью (для быстрого подбора)
    preferred_property_types = models.TextField(
        'Предпочитаемые типы жилья',
        default="[]",
        help_text='Например: ["apartment", "house"]'
    )
    max_price = models.DecimalField(
        'Максимальная цена', 
        max_digits=12, 
        decimal_places=2,
        null=True, 
        blank=True
    )
    min_rooms = models.PositiveSmallIntegerField('Минимум комнат', null=True, blank=True)
    
    # Семейное положение (для статистики)
    marital_status = models.CharField(
        'Семейное положение',
        max_length=20,
        choices=(
            ('single', 'Холост/Не замужем'),
            ('married', 'Женат/Замужем'),
            ('divorced', 'Разведен'),
        ),
        blank=True
    )
    
    # Есть ли дети
    has_children = models.BooleanField('Есть дети', default=False)
    
    # Работа (для проверки платежеспособности - LAN-NFR-03)
    employment = models.CharField('Место работы', max_length=200, blank=True)
    monthly_income = models.DecimalField(
        'Ежемесячный доход', 
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name = 'Профиль арендатора'
        verbose_name_plural = 'Профили арендаторов'
    
    def __str__(self):
        return f"Профиль арендатора: {self.user.username}"


class LandlordProfile(models.Model):
    """
    Профиль арендодателя (дополнительные поля для LAN)
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='landlord_profile',
        limit_choices_to={'user_type': 'landlord'}
    )
    
    # Верификация (LAN-NFR-03, MOD-NFR-01)
    is_verified = models.BooleanField('Верифицирован', default=False)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_landlords',
        limit_choices_to={'user_type__in': ['moderator', 'admin']}
    )
    verified_at = models.DateTimeField('Дата верификации', null=True, blank=True)
    
    # Рейтинг (на основе отзывов)
    rating = models.FloatField('Рейтинг', default=0.0)
    reviews_count = models.PositiveIntegerField('Количество отзывов', default=0)
    
    # Баланс (для платных услуг)
    balance = models.DecimalField('Баланс', max_digits=10, decimal_places=2, default=0)
    
    # Статистика
    total_properties = models.PositiveIntegerField('Всего объектов', default=0)
    active_properties = models.PositiveIntegerField('Активных объектов', default=0)
    total_bookings = models.PositiveIntegerField('Всего бронирований', default=0)
    
    class Meta:
        verbose_name = 'Профиль арендодателя'
        verbose_name_plural = 'Профили арендодателей'
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"Профиль арендодателя: {self.user.username}"


class Property(models.Model):
    """
    Объект недвижимости (с учетом модерации - MOD-NFR-01)
    """
    PROPERTY_TYPES = (
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('commercial', 'Коммерческая'),
        ('land', 'Участок'),
    )
    
    # Статусы модерации (MOD-NFR-01)
    MODERATION_STATUSES = (
        ('draft', 'Черновик'),
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('archived', 'В архиве'),
    )
    
    # Владелец (арендодатель)
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='properties',
        limit_choices_to={'user_type': 'landlord'},
        verbose_name='Владелец'
    )
    
    # Основная информация
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание')
    
    # Адрес (для быстрого поиска - MOD-NFR-02)
    address = models.CharField('Адрес', max_length=255, db_index=True)
    latitude = models.FloatField('Широта', null=True, blank=True)
    longitude = models.FloatField('Долгота', null=True, blank=True)
    
    # Характеристики
    property_type = models.CharField('Тип', max_length=20, choices=PROPERTY_TYPES, db_index=True)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2, db_index=True)
    rooms = models.PositiveSmallIntegerField('Комнат', null=True, blank=True, db_index=True)
    area = models.FloatField('Площадь (м²)')
    floor = models.PositiveSmallIntegerField('Этаж', null=True, blank=True)
    floors_total = models.PositiveSmallIntegerField('Этажей в доме', null=True, blank=True)
    has_furniture = models.BooleanField('С мебелью', default=False)
    has_appliances = models.BooleanField('С техникой', default=False)
    separate_bathroom = models.BooleanField('Раздельный санулзел', default=False)
    allows_pets = models.BooleanField('Можно с животными', default=False)
    allows_children = models.BooleanField('Можно с детьми', default=False)
    
    # Данные ЕГРН (SYS-NFR-06)
    egrn_number = models.CharField(
        'Номер ЕГРН', 
        max_length=50, 
        unique=True,
        help_text='Выписка из Единого государственного реестра недвижимости'
    )
    egrn_file = models.FileField(
        'Файл ЕГРН',
        upload_to='temp/egrn/%Y/%m/',
        help_text='Загрузите выписку из ЕГРН'
    )
    egrn_verified = models.BooleanField('ЕГРН проверен', default=False)
    
    # Модерация (MOD-NFR-01)
    moderation_status = models.CharField(
        'Статус модерации', 
        max_length=20, 
        choices=MODERATION_STATUSES, 
        default='pending',
        db_index=True
    )
    moderator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='moderated_properties',
        limit_choices_to={'user_type__in': ['moderator', 'admin']}
    )
    moderation_comment = models.TextField('Комментарий модератора', blank=True)
    moderated_at = models.DateTimeField('Дата модерации', null=True, blank=True)
    
    # Даты
    created_at = models.DateTimeField('Создано', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    published_at = models.DateTimeField('Опубликовано', null=True, blank=True, db_index=True)
    
    # Статистика просмотров
    views_count = models.PositiveIntegerField('Просмотры', default=0)
    
    class Meta:
        verbose_name = 'Объект недвижимости'
        verbose_name_plural = 'Объекты недвижимости'
        ordering = ['-published_at']
        indexes = [
            # Составные индексы для частых фильтров (MOD-NFR-02)
            models.Index(fields=['moderation_status', 'published_at']),
            models.Index(fields=['property_type', 'price']),
            models.Index(fields=['rooms', 'area']),
        ]
    
    def __str__(self):
        return f"{self.address} - {self.price} ₽"
    
    def save(self, *args, **kwargs):
        """Автоматически обновляем published_at при публикации"""
        if self.moderation_status == 'approved' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def move_files_to_property_folder(self):
        """Перемещает все файлы объекта в папку properties/<id>/"""
        target_dir = os.path.join(settings.MEDIA_ROOT, 'properties', str(self.id))
        os.makedirs(target_dir, exist_ok=True)

        for img in self.images.all():
            # оригинал
            old_path = img.image.path
            if os.path.dirname(old_path) != target_dir:
                new_name = os.path.basename(old_path)
                new_path = os.path.join(target_dir, new_name)
                shutil.move(old_path, new_path)
                img.image.name = os.path.join('properties', str(self.id), new_name)

            # миниатюра
            if img.thumbnail and img.thumbnail.name:
                old_thumb_path = img.thumbnail.path
                if os.path.dirname(old_thumb_path) != target_dir:
                    new_thumb_name = os.path.basename(old_thumb_path)
                    new_thumb_path = os.path.join(target_dir, new_thumb_name)
                    shutil.move(old_thumb_path, new_thumb_path)
                    img.thumbnail.name = os.path.join('properties', str(self.id), new_thumb_name)

            img.save()

        if self.egrn_file and self.egrn_file.name:
            old_path = self.egrn_file.path
            if os.path.dirname(old_path) != target_dir:
                new_name = os.path.basename(old_path)
                new_path = os.path.join(target_dir, new_name)
                shutil.move(old_path, new_path)
                self.egrn_file.name = os.path.join('properties', str(self.id), new_name)
                self.save(update_fields=['egrn_file'])

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Фото', upload_to='temp/%Y/%m/%d/')
    thumbnail = models.ImageField('Миниатюра', upload_to='temp/thumbnails/%Y/%m/%d/', null=True, blank=True)
    is_main = models.BooleanField('Главное фото', default=False)
    sort_order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'Фото'
        ordering = ['-is_main', 'sort_order']
        indexes = [
            models.Index(fields=['property', 'is_main']),
        ]

    def __str__(self):
        return f"Фото {self.sort_order} для {self.property.address}"

    def save(self, *args, **kwargs):
        # Сначала сохраняем, чтобы получить ID (нужен для пути)
        super().save(*args, **kwargs)

        # Если есть изображение и нет миниатюры – создаём
        if self.image and not self.thumbnail:
            self.create_thumbnail()
            # Сохраняем снова, чтобы записать thumbnail
            super().save(update_fields=['thumbnail'])

    def create_thumbnail(self):
        try:
            # Открываем оригинал
            img = PilImage.open(self.image.path)
            # Определяем размер миниатюры (например, 300x300)
            img.thumbnail((300, 300), PilImage.Resampling.LANCZOS)

            # Сохраняем в BytesIO
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            
            # Генерируем имя файла для миниатюры
            filename = os.path.basename(self.image.name)
            name, ext = os.path.splitext(filename)
            thumb_filename = f"{name}_thumb.jpg"
            
            # Сохраняем в поле thumbnail
            self.thumbnail.save(thumb_filename, File(thumb_io), save=False)
        except Exception as e:
            print(f"Ошибка создания миниатюры: {e}")


class Document(models.Model):
    """
    Документы пользователей (для верификации - LAN-NFR-03)
    """
    DOCUMENT_TYPES = (
        ('passport', 'Паспорт'),
        ('egrn', 'Выписка ЕГРН'),
        ('ownership', 'Свидетельство о собственности'),
        ('contract', 'Договор аренды'),
        ('other', 'Другое'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField('Тип документа', max_length=20, choices=DOCUMENT_TYPES, db_index=True)
    title = models.CharField('Название', max_length=100)
    file = models.FileField('Файл', upload_to='documents/%Y/%m/')
    uploaded_at = models.DateTimeField('Загружено', auto_now_add=True)
    
    # Модерация документа
    is_verified = models.BooleanField('Проверен', default=False, db_index=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_documents',
        limit_choices_to={'user_type__in': ['moderator', 'admin']}
    )
    verified_at = models.DateTimeField('Проверен', null=True, blank=True)
    rejection_reason = models.TextField('Причина отказа', blank=True)
    
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        indexes = [
            models.Index(fields=['user', 'doc_type']),
            models.Index(fields=['is_verified', 'uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.user.username}"


class Favorite(models.Model):
    """
    Избранное (для арендаторов - TAL-NFR-01)
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites',
        limit_choices_to={'user_type': 'tenant'}
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'property']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.property.address}"

class Booking(models.Model):
    STATUSES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    )

    tenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        limit_choices_to={'user_type': 'tenant'}
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField('Дата заезда')
    end_date = models.DateField('Дата выезда')
    message = models.TextField('Сообщение', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUSES, default='pending', db_index=True)
    response_message = models.TextField('Ответ', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tenant.username} - {self.property.address} ({self.start_date} - {self.end_date})"

class Review(models.Model):
    """
    Отзывы (для рейтинга арендодателей)
    """
    # Кто оставляет отзыв (арендатор)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_given',
        limit_choices_to={'user_type': 'tenant'}
    )
    
    # Кому оставляют отзыв (арендодатель)
    landlord = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_received',
        limit_choices_to={'user_type': 'landlord'}
    )
    
    # По какому объекту
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    
    # Отзыв
    rating = models.PositiveSmallIntegerField('Оценка', choices=[(i, i) for i in range(1, 6)])
    text = models.TextField('Текст отзыва')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    # Модерация отзыва
    is_moderated = models.BooleanField('Промодерирован', default=False)
    moderated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='moderated_reviews'
    )
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ['author', 'property']  # Один отзыв на объект
        indexes = [
            models.Index(fields=['landlord', 'rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.username} -> {self.landlord.username}: {self.rating}★"

@receiver(post_delete, sender=Property)
def delete_property_folder(sender, instance, **kwargs):
    """Удаляет папку с файлами объекта при удалении объекта"""
    folder_path = os.path.join(settings.MEDIA_ROOT, 'properties', str(instance.id))
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)