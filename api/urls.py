from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, OrderViewSet, RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")   # Registering the CategoryViewSet with the router
router.register("products", ProductViewSet, basename="products")   # Registering the ProductViewSet with the router
router.register("orders", OrderViewSet, basename="orders")   # Registering the OrderViewSet with the router

urlpatterns = [
    path("", include(router.urls)), # Including the router URLs
    path("auth/register/", RegisterView.as_view(), name="register"), # User registration endpoint
]
