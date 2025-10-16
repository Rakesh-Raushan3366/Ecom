from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from django.db.models import Prefetch
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, RegisterSerializer, UserSerializer
from .filters import ProductFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

CACHE_TIMEOUT = 3600  # 1 hour

# User registration view
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

# JWT token view
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUser,)  # only admin can create/update/delete

    def list(self, request, *args, **kwargs):
        key = "categories_list"
        data = cache.get(key)
        if data is None:
            qs = self.get_queryset()
            data = CategorySerializer(qs, many=True).data
            cache.set(key, data, CACHE_TIMEOUT)
        return Response(data)

# Product viewset with filtering, searching, ordering, and caching
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "stock", "created_at"]

    # Override list to implement caching
    def list(self, request, *args, **kwargs):
        # caching key depends on query params so different filters have different keys
        key = f"products_list:{request.get_full_path()}"
        data = cache.get(key)
        if data is None:
            qs = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = serializer.data
                # stash paginated response as well
                cache.set(key, data, CACHE_TIMEOUT)
                return self.get_paginated_response(data)
            serializer = self.get_serializer(qs, many=True)
            data = serializer.data
            cache.set(key, data, CACHE_TIMEOUT)
        # If cached, still need to return paginated shape when applicable
        # Simpler approach: return full cached array with manual pagination
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(data)

    # Admin-only create/update/destroy should invalidate caches
    def perform_create(self, serializer):
        serializer.save()
        cache.clear()

    def perform_update(self, serializer):
        serializer.save()
        cache.clear()

    def perform_destroy(self, instance):
        instance.delete()
        cache.clear()

# Order viewset with user-specific data and notifications
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    # users see only their orders; admins can see all
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.select_related("user").prefetch_related("items__product")
        return Order.objects.filter(user=user).prefetch_related("items__product")

    # notify user on order creation and status change
    def perform_create(self, serializer):
        order = serializer.save()
        # invalidate product cache because stock changed
        cache.clear()
        # notify user via channels
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        group_name = f"user_{order.user.id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "order.notification",
                "order_id": order.id,
                "status": order.status,
            },
        )

    # notify user on status change
    def perform_update(self, serializer):
        prev_status = self.get_object().status
        order = serializer.save()
        if order.status != prev_status:
            # send notification
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            group_name = f"user_{order.user.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "order.notification",
                    "order_id": order.id,
                    "status": order.status,
                },
            )