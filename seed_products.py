import csv
from database import db

def import_products_from_csv(filename):
    products = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean and typecast fields
            product = {
                "id": int(row["id"]),
                "name": row["name"].strip(),
                "price": float(row["price"]),
                "image": row["image"].strip(),
                "category": row["category"].strip(),
                # Default extra fields
                "description": "",
                "color": "",
                "popular": False,
                "new": False,
                "sale": False,
                "images": [row["image"].strip()],
                "sizes": [],
                "materials": "",
                "care_instructions": "",
                "in_stock": True,
                "stock_quantity": 10,
                "tags": []
            }
            products.append(product)

    # Clear existing and insert new
    print("Clearing existing products...")
    db.products.delete_many({})
    print(f"Inserting {len(products)} products...")
    db.products.insert_many(products)
    print("✅ Import complete!")

if __name__ == "__main__":
    import_products_from_csv("new_products.csv")
