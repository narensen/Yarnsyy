from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import csv
import random
import os

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------------
# CSV-based product loading (No MongoDB)
# -------------------------------------------------------------------

# Maximum number of products to load from CSV
MAX_PRODUCTS = 12

def load_csv_products(filename='new_products.csv', max_products=MAX_PRODUCTS):
    """Load products from CSV file and enrich with additional fields"""
    products = []
    
    with open(filename, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Only load up to max_products
            product_id = int(row['id'])
            if product_id > max_products:
                break
                
            # Extract color from product name
            name = row['name']
            color = extract_color(name)
            
            # Create enriched product
            product = {
                'id': product_id,
                'name': name,
                'price': float(row['price']),
                'image': row['image'],
                'category': row.get('category', 'other').lower(),
                'color': color,
                'description': f"Beautiful handcrafted {name.lower()}. Made with love and premium yarn.",
                'popular': product_id in [1, 2, 5, 8],  # Mark some as popular
                'new': product_id in [10, 11, 12],  # Mark recent ones as new
            }
            products.append(product)
    
    return products

def extract_color(name):
    """Extract color from product name"""
    name_lower = name.lower()
    colors = ['lavender', 'midnight', 'blush', 'pink', 'emerald', 'green', 
              'ocean', 'blue', 'sunset', 'orange', 'cream', 'purple', 
              'rose', 'gold', 'sage', 'buttercream', 'indigo']
    
    for color in colors:
        if color in name_lower:
            return color.capitalize()
    
    return 'Natural'

# Load products from CSV on startup
PRODUCTS = load_csv_products()


# Sample orders data (in production, this would also be in a database)
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

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products or filtered products from in-memory list"""
    
    # Get filter parameters
    category = request.args.get('category')
    color = request.args.get('color')
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'name')  # name, price, newest
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', float('inf')))
    
    # Filter products
    filtered_products = PRODUCTS.copy()
    
    # Apply filters
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    
    if color:
        filtered_products = [p for p in filtered_products if p['color'].lower() == color.lower()]
    
    if search:
        filtered_products = [
            p for p in filtered_products 
            if search in p['name'].lower() 
            or search in p['description'].lower() 
            or search in p['category'].lower()
        ]
    
    # Apply price filter
    filtered_products = [
        p for p in filtered_products 
        if min_price <= p['price'] <= max_price
    ]
    
    # Apply sorting
    if sort_by == 'price':
        filtered_products.sort(key=lambda p: p['price'])
    elif sort_by == 'newest':
        filtered_products.sort(key=lambda p: p['id'], reverse=True)
    else:  # name
        filtered_products.sort(key=lambda p: p['name'])
    
    # Get filter metadata
    all_categories = sorted(list(set(p['category'] for p in PRODUCTS)))
    all_colors = sorted(list(set(p['color'] for p in PRODUCTS if p['color'])))
    
    prices = [p['price'] for p in PRODUCTS]
    price_range = {'min': min(prices) if prices else 0, 'max': max(prices) if prices else 0}
    
    # Build response
    response = {
        'products': filtered_products,
        'total': len(filtered_products),
        'filters': {
            'categories': all_categories,
            'colors': all_colors,
            'price_range': price_range
        }
    }
    
    return jsonify(response)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID from in-memory list"""
    
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/<int:product_id>/details', methods=['GET'])
def get_product_details(product_id):
    """Get detailed product information from in-memory list"""
    
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Find related products (same category, different ID)
    related = [
        p for p in PRODUCTS 
        if p['category'] == product['category'] and p['id'] != product_id
    ][:4]  # Limit to 4 related products
    
    return jsonify({
        'product': product,
        'related': related
    })

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get product recommendations from in-memory list"""
    
    # Get products that are popular or new
    candidates = [p for p in PRODUCTS if p.get('popular') or p.get('new')]
    
    # If we have candidates, pick up to 4 random ones
    if candidates:
        recommendations = random.sample(candidates, min(4, len(candidates)))
    else:
        # Fallback to random products
        recommendations = random.sample(PRODUCTS, min(4, len(PRODUCTS)))
    
    return jsonify(recommendations)

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
def manage_cart():
    """Manage cart operations (cart is managed in localStorage on frontend)"""
    if request.method == 'GET':
        return jsonify({'items': [], 'total': 0})
    
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({'success': True, 'message': 'Item added to cart'})
    
    if request.method == 'DELETE':
        return jsonify({'success': True, 'message': 'Item removed from cart'})

@app.route('/api/connection-status', methods=['GET'])
def connection_status():
    """Return data source connection status (CSV-based)"""
    return jsonify({
        'connected': False,
        'message': 'Using CSV data (No MongoDB)',
        'dataSource': 'CSV'
    })

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
        'message': 'Connected to Yarnsy API (CSV Version - No MongoDB)',
        'dataSource': 'CSV',
        'productCount': len(PRODUCTS),
        'endpoints': [
            '/api/products',
            '/api/products/<id>',
            '/api/products/<id>/details',
            '/api/recommendations',
            '/api/connection-status'
        ]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Yarnsy API server (CSV Version - No MongoDB)")
    print("="*60)
    
    print(f"\n✅ Loaded {len(PRODUCTS)} products from CSV file")
    print(f"   Products: {', '.join([p['name'] for p in PRODUCTS[:3]])}...")
    
    print("\n📡 Available endpoints:")
    print("  - http://localhost:5000/")
    print("  - http://localhost:5000/api/products")
    print("  - http://localhost:5000/api/recommendations")
    print("  - http://localhost:5000/api/connection-status")
    
    print("\n🗄️  Data Source: CSV (new_products.csv)")
    print("💾 Cart Storage: localStorage (frontend)")
    
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Use environment variable to control debug mode (default: True for development)
    # Set FLASK_DEBUG=False in production
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    
    app.run(host='0.0.0.0', debug=debug_mode, port=5000)