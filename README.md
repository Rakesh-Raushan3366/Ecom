# 🛒 Advanced E-Commerce API  
### Built with Django REST Framework, Redis, and Django Channels  

---

## 🎯 **Overview**
This is a fully functional **E-commerce REST API** that supports:  
- 🧍 User registration, login, and profile management (JWT Auth)  
- 🛍️ Product & Category management (with filtering, pagination, and caching via Redis)  
- 🧾 Order placement, tracking, and real-time notifications (via Django Channels)  
- ⚡ Optimized performance with query caching, prefetching, and pagination  

---

## 🧰 **Tech Stack**
| Layer | Technology |
|--------|-------------|
| **Backend Framework** | Django 4.2 + Django REST Framework |
| **Authentication** | JWT (SimpleJWT) |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **Real-time Updates** | Django Channels + Channels Redis |
| **Testing** | Django Test Framework (APITestCase) |

---

## ⚙️ **Features**
### 👤 User & Auth
- Register new users using email & password.  
- Obtain JWT access and refresh tokens.  
- Manage personal profile (name, phone, address, etc.).  

### 🛍️ Product Management
- Category CRUD (Admin only).  
- Product CRUD (Admin only).  
- Product listing with:  
  - Pagination (10 per page)  
  - Filtering by category, price range, and stock  
  - Caching using Redis  

### 🧾 Order System
- Add products to cart and place an order.  
- Automatic stock reduction after order.  
- Track order status (`pending → shipped → delivered`).  
- Admin can update order status.  

### 🔔 Real-Time Notifications
- Users get notified instantly when their order status changes (WebSocket).  

---

## 🚀 **Project Setup**

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Rakesh-Raushan3366/Ecom.git
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate      # (Windows)
# or
source venv/bin/activate   # (Linux/Mac)
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables
Create a `.env` file in the root:
```
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=ecom_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/1
```

### 5️⃣ Start PostgreSQL & Redis
You can run them via Docker Compose:
```bash
docker-compose up -d
```

### 6️⃣ Apply Migrations
```bash
python manage.py migrate
```

### 7️⃣ Create Superuser
```bash
python manage.py createsuperuser
```

### 8️⃣ Run Server (with Channels ASGI)
```bash
uvicorn ecom.asgi:application --host 0.0.0.0 --port 8000
```

Visit: http://127.0.0.1:8000/

---

## 🔑 **Authentication (JWT)**
| Action | Endpoint | Method |
|---------|-----------|--------|
| Register | `/api/auth/register/` | POST |
| Obtain Token | `/api/auth/token/` | POST |
| Refresh Token | `/api/auth/token/refresh/` | POST |

Header Example:
```
Authorization: Bearer <access_token>
```

---

## 🧭 **API Endpoints**

### 👤 Users
| Function | Method | Endpoint |
|-----------|---------|-----------|
| Register user | POST | `/api/auth/register/` |
| Get JWT tokens | POST | `/api/auth/token/` |

### 🏷️ Categories
| Function | Method | Endpoint | Auth |
|-----------|---------|-----------|-------|
| List categories | GET | `/api/categories/` | Public |
| Create category | POST | `/api/categories/` | Admin |

### 🛍️ Products
| Function | Method | Endpoint | Auth |
|-----------|---------|-----------|-------|
| List products | GET | `/api/products/` | Public |
| Filter products | GET | `/api/products/?category=1&min_price=100&max_price=500` | Public |
| Add product | POST | `/api/products/` | Admin |
| Update product | PATCH | `/api/products/{id}/` | Admin |
| Delete product | DELETE | `/api/products/{id}/` | Admin |

### 🧾 Orders
| Function | Method | Endpoint | Auth |
|-----------|---------|-----------|-------|
| Place order | POST | `/api/orders/` | Authenticated |
| View orders | GET | `/api/orders/` | Authenticated |
| Update order status | PATCH | `/api/orders/{id}/` | Admin |

---

## 💾 **Caching with Redis**
- Product and Category list endpoints are cached for 1 hour.  
- Cache automatically invalidates when product or category changes.  
- Manual clear:
```python
from django.core.cache import cache
cache.clear()
```

---

## 🔔 **Real-Time Order Updates**
WebSocket Endpoint:
```
ws://127.0.0.1:8000/ws/orders/
```
When an order status changes, users receive:
```json
{
  "type": "order_update",
  "order_id": 1,
  "status": "shipped"
}
```

---

## 🧪 **Running Tests**
```bash
python manage.py test
```

Expected output:
```
Ran 14 tests in 6.123s
OK
```

---

## 🧾 **Author**
**Rakesh Raushan**  
🎓 Assignment: *Advanced E-commerce API with Caching and Notifications*  
📅 October 2025  
🚀 Built with ❤️ using Django REST Framework  
