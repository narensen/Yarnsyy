# DEPRECATED: This file is no longer used.
# The application now loads products from CSV (new_products.csv) instead of MongoDB.
# See app.py for the new CSV-based implementation.

# Previous MongoDB implementation (kept for reference)
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client[os.getenv('MONGODB_DB_NAME', 'yarnsy')]
        self.products = self.db.products
        self.orders = self.db.orders

db = Database()
