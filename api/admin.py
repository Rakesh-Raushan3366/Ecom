from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# Register your models here.

# Register Category configurations
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")

# Register Product configurations
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "category", "updated_at")

# Inline for OrderItem to be used in OrderAdmin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product", "quantity", "price_at_purchase")
    can_delete = False
    extra = 0

# Register Order configurations
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    inlines = [OrderItemInline]