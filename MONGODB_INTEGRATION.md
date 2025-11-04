# MongoDB Integration Guide

## 📋 Overview

This guide outlines how to integrate MongoDB with the Yarnsy e-commerce website. The current implementation uses in-memory data structures, but MongoDB will provide persistent storage for products, orders, users, and more.

---

## 🗄️ Database Structure

### Collections Needed:

1. **users** - User accounts and authentication
2. **products** - Product catalog
3. **orders** - Customer orders
4. **cart** - Shopping carts (optional - can use sessions)

---

## 📦 Installation

### Step 1: Install MongoDB Driver

```bash
pip install pymongo
pip install python-dotenv
```

### Step 2: Update requirements.txt

```txt
Flask==3.0.0
flask-cors==4.0.0
pymongo==4.6.0
python-dotenv==1.0.0
```

---

## 🔧 Configuration

### Step 1: Create `.env` file

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=yarnsy
```

### Step 2: MongoDB Connection Setup

Create `database.py`:

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client[os.getenv('MONGODB_DB_NAME', 'yarnsy')]
        self.users = self.db.users
        self.products = self.db.products
        self.orders = self.db.orders

    def close(self):
        self.client.close()

db = Database()
```

---

## 📝 Schema Definitions

### 1. Users Collection

```python
{
    "_id": ObjectId("..."),
    "email": "user@example.com",
    "name": "John Doe",
    "password": "hashed_password",  # Use bcrypt or similar
    "createdAt": ISODate("2025-01-01T00:00:00Z"),
    "orders": []  # Array of order IDs
}
```

### 2. Products Collection

```python
{
    "_id": ObjectId("..."),
    "id": 1,  # For compatibility
    "name": "Lavender Dream Top",
    "price": 89.99,
    "image": "https://...",
    "category": "tops",
    "description": "Elegant crochet top...",
    "color": "lavender",
    "popular": True,
    "new": False,
    "sale": False,
    "images": [],  # Array of image URLs
    "sizes": [],
    "materials": "",
    "in_stock": True,
    "stock_quantity": 10,
    "tags": []
}
```

### 3. Orders Collection

```python
{
    "_id": ObjectId("..."),
    "orderNumber": "YS123456789",
    "userId": ObjectId("..."),  # Reference to user
    "date": ISODate("2025-01-01T00:00:00Z"),
    "status": "pending",  # pending, shipped, delivered
    "total": 179.98,
    "items": [
        {
            "productId": ObjectId("..."),
            "name": "Lavender Dream Top",
            "quantity": 1,
            "price": 89.99,
            "image": "https://..."
        }
    ],
    "shipping": {
        "name": "John Doe",
        "address": "123 Main St",
        "city": "City",
        "postalCode": "12345",
        "country": "Country"
    },
    "payment": {
        "method": "credit_card",
        "cardLast4": "1234"
    },
    "trackingNumber": "TRACK123456"
}
```

---

## 🔄 Update Backend (app.py)

### Example Implementation:

```python
from database import db
from bson import ObjectId
from datetime import datetime

# Get Products
@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    color = request.args.get('color')
    search = request.args.get('search', '').lower()
    
    query = {}
    if category:
        query['category'] = category
    if color:
        query['color'] = color
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
            {'category': {'$regex': search, '$options': 'i'}}
        ]
    
    products = list(db.products.find(query))
    # Convert ObjectId to string for JSON serialization
    for product in products:
        product['_id'] = str(product['_id'])
    
    return jsonify(products)

# Create Order
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    order = {
        'orderNumber': f"YS{int(datetime.now().timestamp())}",
        'userId': ObjectId(data.get('userId')) if data.get('userId') else None,
        'date': datetime.now(),
        'status': 'pending',
        'total': data.get('total'),
        'items': data.get('items', []),
        'shipping': data.get('shipping', {}),
        'payment': data.get('payment', {}),
        'trackingNumber': None
    }
    
    result = db.orders.insert_one(order)
    order['_id'] = str(result.inserted_id)
    
    return jsonify(order), 201

# Get User Orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    userId = request.args.get('userId')
    query = {}
    if userId:
        query['userId'] = ObjectId(userId)
    
    orders = list(db.orders.find(query).sort('date', -1))
    for order in orders:
        order['_id'] = str(order['_id'])
        if order.get('userId'):
            order['userId'] = str(order['userId'])
        # Convert date to ISO string
        if isinstance(order.get('date'), datetime):
            order['date'] = order['date'].isoformat()
    
    return jsonify(orders)
```

---

## 🚀 Migration Steps

### 1. Seed Initial Products

```python
# seed_products.py
from database import db
from app import PRODUCTS

for product in PRODUCTS:
    db.products.insert_one(product)
```

### 2. Update Authentication

```python
# In AuthContext or backend
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

def signup(name, email, password):
    hashed_password = generate_password_hash(password)
    user = {
        'email': email,
        'name': name,
        'password': hashed_password,
        'createdAt': datetime.now(),
        'orders': []
    }
    result = db.users.insert_one(user)
    user['_id'] = str(result.inserted_id)
    del user['password']
    return user
```

---

## 🔐 Security Considerations

1. **Password Hashing**: Use `werkzeug.security` or `bcrypt`
2. **Input Validation**: Validate all inputs before database operations
3. **Sanitization**: Sanitize search queries to prevent injection
4. **Indexes**: Create indexes on frequently queried fields:
   ```python
   db.products.create_index("category")
   db.products.create_index("name")
   db.orders.create_index("userId")
   db.orders.create_index("orderNumber")
   ```

---

## 📊 Indexes to Create

```python
# In database.py or migration script
db.products.create_index("category")
db.products.create_index("name")
db.products.create_index("color")
db.products.create_index([("name", "text"), ("description", "text")])
db.orders.create_index("userId")
db.orders.create_index("orderNumber")
db.orders.create_index("status")
db.users.create_index("email", unique=True)
```

---

## 🔄 Migration from In-Memory to MongoDB

### Phase 1: Dual Mode
- Keep current in-memory system
- Add MongoDB as secondary storage
- Test thoroughly

### Phase 2: Migration
- Update all endpoints to use MongoDB
- Remove in-memory data structures
- Test all functionality

### Phase 3: Cleanup
- Remove old code
- Optimize queries
- Add indexes

---

## 💡 Tips

1. **Use ObjectId**: MongoDB's ObjectId is recommended for `_id` fields
2. **Keep compatibility**: Maintain `id` field for frontend compatibility
3. **Error Handling**: Always handle database errors gracefully
4. **Connection Pooling**: MongoDB driver handles this automatically
5. **Transactions**: Use transactions for complex operations

---

## 📝 Next Steps

1. Install MongoDB locally or use MongoDB Atlas (cloud)
2. Create `database.py` with connection logic
3. Update `app.py` endpoints to use MongoDB
4. Create migration script to seed initial data
5. Update authentication to use MongoDB
6. Test all endpoints
7. Deploy with MongoDB connection string

---

## 🔗 Resources

- [MongoDB Python Driver Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Free cloud MongoDB
- [Flask MongoDB Tutorial](https://www.mongodb.com/developer/languages/python/python-quickstart-flask/)

---

**Note**: This is a guide structure. Actual implementation will depend on your specific MongoDB setup and requirements.

