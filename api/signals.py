from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Category, Order
from django.core.cache import cache

# Signal handlers to clear cache when models are modified
@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    cache.clear()

# Clear cache when a product is deleted
@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    cache.clear()

# Clear cache when a category is created, updated, or deleted
@receiver(post_save, sender=Category)
def category_saved(sender, instance, **kwargs):
    cache.clear()

# Clear cache when a category is deleted
@receiver(post_delete, sender=Category)
def category_deleted(sender, instance, **kwargs):
    cache.clear()

# Clear cache when an order is deleted
@receiver(post_save, sender=Order)
def order_saved(sender, instance, created, **kwargs):
    # cache cleared during create in view too, but this is a safety net
    cache.clear()
