from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from api.models import Category, Product, Order


class EcommerceAPITests(APITestCase):

    def setUp(self):
        # Create normal user
        self.user = User.objects.create_user(username="alice", email="alice@example.com", password="password123")

        # Create admin user
        self.admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass")

        # Generate JWT for normal user
        response = self.client.post(reverse("token_obtain_pair"), {"username": "alice", "password": "password123"})
        self.user_token = response.data["access"]

        # Generate JWT for admin
        response_admin = self.client.post(reverse("token_obtain_pair"), {"username": "admin", "password": "adminpass"})
        self.admin_token = response_admin.data["access"]

        # Setup URLs
        self.category_url = reverse("categories-list")
        self.product_url = reverse("products-list")
        self.order_url = reverse("orders-list")

    def authenticate_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

    def authenticate_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")


    # Authentication Tests
    def test_user_registration(self):
        url = reverse("register")
        data = {"username": "test1", "email": "test1@mail.com", "password": "test1@123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_jwt_token_generation(self):
        response = self.client.post(reverse("token_obtain_pair"), {"username": "test1", "password": "test1@123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


    # Category Tests
    def test_admin_can_create_category(self):
        self.authenticate_admin()
        data = {"name": "Electronics", "description": "Gadgets and devices"}
        response = self.client.post(self.category_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_category(self):
        self.authenticate_user()
        data = {"name": "Home", "description": "Household items"}
        response = self.client.post(self.category_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_categories(self):
        Category.objects.create(name="Books", description="All books")
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    # Product Tests
    def test_admin_can_create_product(self):
        self.authenticate_admin()
        category = Category.objects.create(name="Mobiles", description="Smartphones")
        data = {
            "name": "iPhone 16",
            "description": "Latest iPhone",
            "price": 120000,
            "stock": 5,
            "category_id": category.id,
        }
        response = self.client.post(self.product_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_list_products(self):
        category = Category.objects.create(name="Books", description="All kinds of books")
        Product.objects.create(name="Django Book", description="Learn Django", price=500, stock=10, category=category)
        response = self.client.get(self.product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_filter_products_by_category(self):
        cat1 = Category.objects.create(name="Mobiles", description="Phones")
        cat2 = Category.objects.create(name="Laptops", description="Computers")
        Product.objects.create(name="iPhone", price=1200, stock=10, category=cat1)
        Product.objects.create(name="Dell Laptop", price=800, stock=10, category=cat2)
        response = self.client.get(f"{self.product_url}?category={cat1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p["category"]["id"] == cat1.id for p in response.data["results"]))

    def test_product_pagination(self):
        cat = Category.objects.create(name="Electronics", description="Gadgets")
        for i in range(15):
            Product.objects.create(name=f"Product {i}", description="Test", price=10, stock=5, category=cat)
        response = self.client.get(self.product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)  # Page size = 10


    # Order Tests
    def test_user_can_place_order(self):
        self.authenticate_user()
        cat = Category.objects.create(name="Accessories", description="Wearables")
        product = Product.objects.create(name="Smart Watch", price=200, stock=5, category=cat)
        data = {
            "items": [
                {"product_id": product.id, "quantity": 2}
            ]
        }
        response = self.client.post(self.order_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        product.refresh_from_db()
        self.assertEqual(product.stock, 3)  # Stock reduced

    def test_user_can_view_own_orders(self):
        self.authenticate_user()
        cat = Category.objects.create(name="Books", description="Educational")
        product = Product.objects.create(name="Python 101", price=50, stock=10, category=cat)
        order = Order.objects.create(user=self.user, total_price=100)
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_order_status(self):
        self.authenticate_admin()
        order = Order.objects.create(user=self.user, total_price=100, status="pending")
        url = reverse("orders-detail", args=[order.id])
        response = self.client.patch(url, {"status": "shipped"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "shipped")

    def test_user_cannot_update_order_status(self):
        self.authenticate_user()
        order = Order.objects.create(user=self.user, total_price=100, status="pending")
        url = reverse("orders-detail", args=[order.id])
        response = self.client.patch(url, {"status": "delivered"}, format="json")
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
