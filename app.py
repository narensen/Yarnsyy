from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
# Import the database connection
from database import db
# Import this to handle MongoDB's _id
from bson.json_util import dumps
import json

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------------
# WE NO LONGER NEED THIS:
# - load_csv_products (function)
# - INITIAL_PRODUCTS (list)
# - initialize_products (function)
# - PRODUCTS = initialize_products() (global variable)
# Your database is now the single source of truth.
# -------------------------------------------------------------------


# Sample orders data (in production, this would also be in a database)
# I've updated the image URLs to be hardcoded since the 'PRODUCTS' list is gone.
ORDERS = [
    {
        'id': 1,
        'orderNumber': 'YS123456789',
        'date': (datetime.now() - timedelta(days=10)).isoformat(),
        'status': 'delivered',
        'total': 179.98,
        'items': [
            {'id': 1, 'name': 'Lavender Dream Top', 'quantity': 1, 'price': 89.99, 'image': 'https://images.unsplash.com/photo-1590736969955-71cc94901144?q=80&w=2070'},
            {'id': 2, 'name': 'Sunset Blush Bag', 'quantity': 1, 'price': 64.99, 'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=2127'},
        ],
        'trackingNumber': 'TRACK123456',
    },
    {
        'id': 2,
        'orderNumber': 'YS987654321',
        'date': (datetime.now() - timedelta(days=5)).isoformat(),
        'status': 'shipped',
        'total': 89.99,
        'items': [
            {'id': 4, 'name': 'Mint Fresh Top', 'quantity': 1, 'price': 89.99, 'image': 'https://images.unsplash.com/photo-1590736969955-71cc94901144?q=80&w=2070'},
        ],
        'trackingNumber': 'TRACK789012',
    },
    {
        'id': 3,
        'orderNumber': 'YS111222333',
        'date': (datetime.now() - timedelta(days=2)).isoformat(),
        'status': 'pending',
        'total': 45.99,
        'items': [
            {'id': 3, 'name': 'Rose Garden Scarf', 'quantity': 1, 'price': 45.99, 'image': 'https://images.unsplash.com/photo-1590736969955-71cc94901144?q=80&w=2070'},
        ],
        'trackingNumber': None,
    },
]

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

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
def manage_cart():
    """Manage cart operations"""
    if request.method == 'GET':
        return jsonify({'items': [], 'total': 0})
    
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({'success': True, 'message': 'Item added to cart'})
    
    if request.method == 'DELETE':
        return jsonify({'success': True, 'message': 'Item removed from cart'})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get user's orders"""
    return jsonify(ORDERS)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    order = next((o for o in ORDERS if o['id'] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/shipping', methods=['GET'])
def get_shipping():
    """Get shipping and tracking information"""
    order_id = request.args.get('order_id')
    
    if order_id:
        order = next((o for o in ORDERS if o['id'] == int(order_id)), None)
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
        'message': 'Connected to Yarnsy API (MongoDB Version)',
        'endpoints': [
            '/api/products',
            '/api/products/<id>',
            '/api/products/<id>/details',
            '/api/recommendations'
        ]
    })

if __name__ == '__main__':
    print("\nStarting Yarnsy API server (MongoDB)...")
    
    # --- CHANGED: Check MongoDB connection on startup ---
    try:
        # Use the more robust client-level admin command for ping
        db.client.admin.command('ping')
        
        print("✅ MongoDB connection successful.")
        product_count = db.products.count_documents({})
        print(f"Loaded {product_count} products from database.")
        
        print("\nAvailable endpoints:")
        print("  - http://localhost:5000/")
        print("  - http://localhost:5000/api/products")
        print("  - http://localhost:5000/api/recommendations")
        print("\nPress Ctrl+C to stop the server")
        
        # Run the app *only* if the connection is successful
        app.run(host='0.0.0.0', debug=True, port=5000)
        
    except Exception as e:
        # THIS IS THE NEW, BETTER ERROR MESSAGE
        print(f"❌ ERROR: Could not connect to MongoDB.")
        print("\n==================== ERROR DETAILS ====================")
        print(f"Details: {e}")
        print("=======================================================")
        print("\nPlease check the following:")
        print("  1. Is your MongoDB server running?")
        print("  2. Is your .env file correct? (MONGODB_URI=\"mongodb://127.0.0.1:27017/yarnsydb\")")
        print("  3. Are there any firewall rules blocking the connection?")
        exit(1) # Exit the script