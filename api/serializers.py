from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, OrderItem
from django.db import transaction

User = get_user_model()

# User Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

# Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]

    # Create user with hashed password
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user

# Product and Category Serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

# Nested serializers for Product and Order
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "category", "category_id", "created_at", "updated_at"]

# Order and OrderItem Serializers
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product", write_only=True)
    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "quantity", "price_at_purchase"]

# Order Serializer with nested items
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "created_at", "updated_at", "items"]
        read_only_fields = ["user", "total_price", "created_at", "updated_at"]

    # Create order with items and handle stock reduction
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user
        with transaction.atomic():
            order = Order.objects.create(user=user, status="pending", total_price=0)
            total = 0
            for item in items_data:
                product = item["product"]
                qty = item["quantity"]
                if product.stock < qty:
                    raise serializers.ValidationError(f"Not enough stock for {product.name}")
                # reduce stock
                product.stock -= qty
                product.save()
                price = product.price
                OrderItem.objects.create(order=order, product=product, quantity=qty, price_at_purchase=price)
                total += price * qty
            order.total_price = total
            order.save()
        return order

    # Update order status only
    def update(self, instance, validated_data):
        status = validated_data.get("status")
        if status:
            instance.status = status
            instance.save()
        return instance
