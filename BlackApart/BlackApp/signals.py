# BlackApp/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from geopy.geocoders import Yandex
from django.conf import settings
from .models import Property

@receiver(pre_save, sender=Property)
def geocode_property(sender, instance, **kwargs):
    
    if instance.address and (instance.latitude is None or instance.longitude is None):
        try:
            api_key = settings.YANDEX_API_KEY
            geolocator = Yandex(api_key='18d8b773-5924-4a29-8afc-8918512836c9')
            location = geolocator.geocode(instance.address)
            if location:
                instance.latitude = location.latitude
                instance.longitude = location.longitude
            else:
                return
        except Exception as e:
            return 
    else:
        return