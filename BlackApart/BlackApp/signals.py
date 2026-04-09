# BlackApp/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from geopy.geocoders import Yandex
from django.conf import settings
from .models import Property

@receiver(pre_save, sender=Property)
def geocode_property(sender, instance, **kwargs):
    print("\n" + "="*50)
    print(f"🟢 СИГНАЛ pre_save для объекта id={instance.id}, адрес='{instance.address}'")
    print(f"Текущие координаты: lat={instance.latitude}, lon={instance.longitude}")
    
    if instance.address and (instance.latitude is None or instance.longitude is None):
        print("🔄 Запускаем геокодирование...")
        try:
            api_key = settings.YANDEX_API_KEY
            geolocator = Yandex(api_key='18d8b773-5924-4a29-8afc-8918512836c9')
            location = geolocator.geocode(instance.address)
            if location:
                instance.latitude = location.latitude
                instance.longitude = location.longitude
                print(f"✅ Координаты обновлены: {instance.latitude}, {instance.longitude}")
            else:
                print("❌ Геокодер вернул None — адрес не найден.")
        except Exception as e:
            print(f"🔥 Ошибка геокодера: {e}")
    else:
        print("⏭️ Пропускаем геокодирование (нет адреса или координаты уже заданы).")
    print("="*50 + "\n")