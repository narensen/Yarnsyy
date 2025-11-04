from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client[os.getenv('MONGODB_DB_NAME', 'yarnsy')]
        self.products = self.db.products
        self.orders = self.db.orders
        self.users = self.db.users
        self.cart = self.db.cart
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance optimization"""
        try:
            # Products indexes
            self.products.create_index([('id', ASCENDING)], unique=True)
            self.products.create_index([('category', ASCENDING)])
            
            # Orders indexes
            self.orders.create_index([('userId', ASCENDING)])
            self.orders.create_index([('orderNumber', ASCENDING)], unique=True)
            
            # Users indexes
            self.users.create_index([('email', ASCENDING)], unique=True)
            
            # Cart indexes
            self.cart.create_index([('userId', ASCENDING)], unique=True)
            
            print("✅ Database indexes created successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")

db = Database()