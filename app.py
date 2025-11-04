from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import time
# Import the database connection
from database import db
# Import this to handle MongoDB's _id
from bson.json_util import dumps
import json

app = Flask(__name__)
CORS(app)

# Helper function to convert MongoDB docs to JSON
# This removes the non-serializable '_id' field
def mongo_to_json(data):
    # Use bson.json_util.dumps to handle MongoDB types like ObjectId
    # Then reload it as a standard Python dict/list
    return json.loads(dumps(data))

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products or filtered products from MongoDB"""
    
    # Get filter parameters
    category = request.args.get('category')
    color = request.args.get('color')
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'name')  # name, price, newest
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', float('inf')))
    
    # --- CHANGED: Start building a MongoDB query filter ---
    query_filter = {
        'price': {'$gte': min_price, '$lte': max_price}
    }
    
    if category:
        query_filter['category'] = category
    if color:
        query_filter['color'] = color
    if search:
        query_filter['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
            {'category': {'$regex': search, '$options': 'i'}},
        ]
    
    # --- CHANGED: Set sorting direction ---
    sort_field = 'name'
    sort_order = 1  # 1 for ascending, -1 for descending
    
    if sort_by == 'price':
        sort_field = 'price'
    elif sort_by == 'newest':
        sort_field = 'id' # Assuming higher IDs are newer
        sort_order = -1
    
    # --- CHANGED: Fetch from MongoDB ---
    # .find() returns a 'cursor' (an iterable)
    # We pass the filter and sort parameters
    products_cursor = db.products.find(query_filter).sort(sort_field, sort_order)
    
    # Convert the cursor to a list
    products = list(products_cursor)
    
    # --- CHANGED: Get filters metadata from the database ---
    # This is more efficient than iterating in Python
    all_categories = db.products.distinct('category')
    all_colors = db.products.distinct('color')
    # Remove empty strings if they exist
    all_colors = [c for c in all_colors if c] 
    
    # Get min/max price from all products, not just filtered ones
    price_agg = list(db.products.aggregate([
        {'$group': {'_id': None, 'min': {'$min': '$price'}, 'max': {'$max': '$price'}}}
    ]))
    
    price_range = {'min': 0, 'max': 0}
    if price_agg:
        price_range = {'min': price_agg[0]['min'], 'max': price_agg[0]['max']}

    # Add metadata
    response = {
        'products': mongo_to_json(products), # Convert Mongo data to JSON
        'total': len(products),
        'filters': {
            'categories': sorted(all_categories),
            'colors': sorted(all_colors),
            'price_range': price_range
        }
    }
    
    return jsonify(response)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID from MongoDB"""
    
    # --- CHANGED: Fetch one product from MongoDB ---
    # We use 'id' (our numeric ID) not '_id' (MongoDB's ObjectId)
    product = db.products.find_one({'id': product_id})
    
    if product:
        return jsonify(mongo_to_json(product))
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/<int:product_id>/details', methods=['GET'])
def get_product_details(product_id):
    """Get detailed product information from MongoDB"""
    
    # --- CHANGED: Fetch main product from MongoDB ---
    product = db.products.find_one({'id': product_id})
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # --- CHANGED: Find related products from MongoDB ---
    related_cursor = db.products.find({
        'category': product['category'], 
        'id': {'$ne': product_id} # $ne means 'not equal'
    }).limit(4)
    
    related = list(related_cursor)
    
    return jsonify({
        'product': mongo_to_json(product),
        'related': mongo_to_json(related)
    })

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get product recommendations from MongoDB"""
    
    # --- CHANGED: Fetch recommendations from MongoDB ---
    # Find products that are popular OR new
    # Use $sample to efficiently get random documents
    pipeline = [
        {'$match': {'$or': [{'popular': True}, {'new': True}]}},
        {'$sample': {'size': 4}}
    ]
    recommendations = list(db.products.aggregate(pipeline))
    
    return jsonify(mongo_to_json(recommendations))

# ============================================================================
# CART API - FULLY INTEGRATED WITH MONGODB
# ============================================================================

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get user's cart from MongoDB"""
    user_id = request.args.get('userId')
    
    if not user_id:
        return jsonify({'error': 'userId is required'}), 400
    
    # Fetch cart from MongoDB
    cart = db.cart.find_one({'userId': user_id})
    
    if not cart:
        return jsonify({'items': [], 'total': 0})
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart.get('items', []))
    
    return jsonify({
        'items': cart.get('items', []),
        'total': round(total, 2)
    })

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add product to cart in MongoDB"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('userId'):
        return jsonify({'error': 'userId is required'}), 400
    if not data.get('productId'):
        return jsonify({'error': 'productId is required'}), 400
    
    user_id = data['userId']
    product_id = data['productId']
    quantity = data.get('quantity', 1)
    
    # Check if product exists
    product = db.products.find_one({'id': product_id})
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get or create cart
    cart = db.cart.find_one({'userId': user_id})
    
    if not cart:
        # Create new cart
        cart = {
            'userId': user_id,
            'items': [],
            'updatedAt': datetime.utcnow()
        }
    
    # Check if item already in cart
    item_exists = False
    for item in cart['items']:
        if item['id'] == product_id:
            item['quantity'] += quantity
            item_exists = True
            break
    
    # If item doesn't exist, add it
    if not item_exists:
        cart['items'].append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'image': product['image'],
            'quantity': quantity
        })
    
    cart['updatedAt'] = datetime.utcnow()
    
    # Update cart in MongoDB
    db.cart.update_one(
        {'userId': user_id},
        {'$set': cart},
        upsert=True
    )
    
    return jsonify({'success': True, 'message': 'Item added to cart'})

@app.route('/api/cart', methods=['DELETE'])
def remove_from_cart():
    """Remove item from cart or clear entire cart"""
    user_id = request.args.get('userId')
    product_id = request.args.get('productId')
    
    if not user_id:
        return jsonify({'error': 'userId is required'}), 400
    
    # If no productId, clear entire cart
    if not product_id:
        db.cart.delete_one({'userId': user_id})
        return jsonify({'success': True, 'message': 'Cart cleared'})
    
    # Remove specific item
    cart = db.cart.find_one({'userId': user_id})
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    # Filter out the item to remove
    cart['items'] = [item for item in cart['items'] if item['id'] != int(product_id)]
    cart['updatedAt'] = datetime.utcnow()
    
    db.cart.update_one(
        {'userId': user_id},
        {'$set': cart}
    )
    
    return jsonify({'success': True, 'message': 'Item removed from cart'})

# ============================================================================
# ORDERS API - FULLY INTEGRATED WITH MONGODB
# ============================================================================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get user's orders from MongoDB"""
    user_id = request.args.get('userId')
    
    if not user_id:
        return jsonify({'error': 'userId is required'}), 400
    
    # Fetch orders from MongoDB, sorted by date (newest first)
    orders_cursor = db.orders.find({'userId': user_id}).sort('date', -1)
    orders = list(orders_cursor)
    
    return jsonify(mongo_to_json(orders))

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create new order in MongoDB"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('userId'):
        return jsonify({'error': 'userId is required'}), 400
    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'Order must contain items'}), 400
    
    user_id = data['userId']
    
    # Generate unique order number (YS + timestamp)
    order_number = f"YS{int(time.time())}"
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in data['items'])
    
    # Create order document
    order = {
        'orderNumber': order_number,
        'userId': user_id,
        'items': data['items'],
        'total': round(total, 2),
        'status': 'pending',
        'date': datetime.utcnow().isoformat(),
        'shippingAddress': data.get('shippingAddress', {}),
        'paymentMethod': data.get('paymentMethod', ''),
        'trackingNumber': None
    }
    
    # Insert order into MongoDB
    db.orders.insert_one(order)
    
    # Clear user's cart after successful order
    db.cart.delete_one({'userId': user_id})
    
    return jsonify({
        'success': True,
        'message': 'Order placed successfully',
        'orderNumber': order_number,
        'order': mongo_to_json(order)
    }), 201

@app.route('/api/orders/<order_number>', methods=['GET'])
def get_order_by_number(order_number):
    """Get a specific order by order number from MongoDB"""
    order = db.orders.find_one({'orderNumber': order_number})
    
    if order:
        return jsonify(mongo_to_json(order))
    return jsonify({'error': 'Order not found'}), 404

# ============================================================================
# USER MANAGEMENT API - NEW ENDPOINTS
# ============================================================================

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user in MongoDB"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email'):
        return jsonify({'error': 'email is required'}), 400
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    
    # Check if user with this email already exists
    existing_user = db.users.find_one({'email': data['email']})
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Create user document
    user = {
        'email': data['email'],
        'name': data['name'],
        'createdAt': datetime.utcnow().isoformat(),
        'orders': []
    }
    
    # Insert user into MongoDB
    result = db.users.insert_one(user)
    user['userId'] = str(result.inserted_id)
    
    return jsonify({
        'success': True,
        'message': 'User created successfully',
        'user': mongo_to_json(user)
    }), 201

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information from MongoDB"""
    from bson import ObjectId
    
    try:
        # Try to find by ObjectId first
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            # Try to find by email as fallback
            user = db.users.find_one({'email': user_id})
    except:
        # If ObjectId conversion fails, try email
        user = db.users.find_one({'email': user_id})
    
    if user:
        return jsonify(mongo_to_json(user))
    return jsonify({'error': 'User not found'}), 404

# ============================================================================
# SHIPPING & OTHER ENDPOINTS
# ============================================================================

@app.route('/api/shipping', methods=['GET'])
def get_shipping():
    """Get shipping and tracking information"""
    order_number = request.args.get('orderNumber')
    
    if not order_number:
        return jsonify({'error': 'orderNumber is required'}), 400
    
    order = db.orders.find_one({'orderNumber': order_number})
    if order:
        return jsonify({
            'trackingNumber': order.get('trackingNumber'),
            'status': order['status'],
            'estimatedDelivery': (datetime.now() + timedelta(days=7)).isoformat(),
        })
    
    return jsonify({'error': 'Shipping info not found'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Yarnsy API'})

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/', methods=['GET'])
def index():
    """Root endpoint for API health check"""
    return jsonify({
        'status': 'online',
        'message': 'Connected to Yarnsy API (MongoDB Version - Fully Integrated)',
        'endpoints': [
            'GET  /api/products',
            'GET  /api/products/<id>',
            'GET  /api/products/<id>/details',
            'GET  /api/recommendations',
            'GET  /api/cart?userId=<id>',
            'POST /api/cart',
            'DEL  /api/cart?userId=<id>&productId=<id>',
            'GET  /api/orders?userId=<id>',
            'POST /api/orders',
            'GET  /api/orders/<orderNumber>',
            'POST /api/users',
            'GET  /api/users/<userId>',
            'GET  /api/shipping?orderNumber=<number>'
        ]
    })

if __name__ == '__main__':
    print("\nStarting Yarnsy API server (MongoDB - Fully Integrated)...")
    
    # --- CHANGED: Check MongoDB connection on startup ---
    try:
        # Use the more robust client-level admin command for ping
        db.client.admin.command('ping')
        
        print("✅ MongoDB connection successful.")
        
        # Show counts for all collections
        product_count = db.products.count_documents({})
        order_count = db.orders.count_documents({})
        user_count = db.users.count_documents({})
        cart_count = db.cart.count_documents({})
        
        print(f"📦 Loaded {product_count} products from database.")
        print(f"📋 {order_count} orders in database.")
        print(f"👥 {user_count} users in database.")
        print(f"🛒 {cart_count} active carts in database.")
        
        print("\nAvailable endpoints:")
        print("  - http://localhost:5000/")
        print("  - http://localhost:5000/api/products")
        print("  - http://localhost:5000/api/cart?userId=<id>")
        print("  - http://localhost:5000/api/orders?userId=<id>")
        print("  - http://localhost:5000/api/users")
        print("\nPress Ctrl+C to stop the server")
        
        # Run the app *only* if the connection is successful
        app.run(host='0.0.0.0', debug=True, port=5000)
        
    except Exception as e:
        print(f"❌ ERROR: Could not connect to MongoDB.")
        print("\n==================== ERROR DETAILS ====================")
        print(f"Details: {e}")
        print("=======================================================")
        print("\nPlease check the following:")
        print("  1. Is your MongoDB server running?")
        print("  2. Is your .env file correct? (MONGODB_URI=\"mongodb://127.0.0.1:27017/yarnsydb\")")
        print("  3. Are there any firewall rules blocking the connection?")
        exit(1) # Exit the script
