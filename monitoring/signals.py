# monitoring/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SensorReading

@receiver(post_save, sender=SensorReading)
def sensor_reading_post_save(sender, instance, created, **kwargs):
    """Signal désactivé temporairement - sera implémenté en Week 3"""
    pass