# 📦 Product Dataset Guide

## Where to Place Your Dataset

You can provide your product dataset in one of these formats:

### **Option 1: Python Dictionary (Recommended)**
Place your data in `app.py` in the `PRODUCTS` array. This is the easiest and works immediately.

### **Option 2: JSON File**
Create a `products.json` file in the root directory, and I'll help integrate it.

### **Option 3: CSV File**
Create a `products.csv` file, and I'll create a loader to convert it.

---

## 📋 Product Data Structure

Here's the structure I expect for each product:

```python
{
    'id': 1,                          # Unique number (required)
    'name': 'Product Name',           # Product title (required)
    'price': 89.99,                   # Price in dollars (required)
    'image': 'https://...',            # Main image URL (required)
    'category': 'tops',               # Category: 'tops', 'bags', 'accessories' (required)
    'description': 'Full description', # Detailed product description (optional but recommended)
    'color': 'lavender',              # Color name (optional)
    'popular': True,                  # Is it popular? (optional, boolean)
    'new': False,                     # Is it new? (optional, boolean)
    'sale': False,                    # Is it on sale? (optional, boolean)
    
    # Additional fields for product detail page (when you create it):
    'images': [                       # Multiple images (optional)
        'https://...',
        'https://...',
    ],
    'sizes': ['S', 'M', 'L'],         # Available sizes (optional)
    'materials': '100% Cotton',       # Materials info (optional)
    'care_instructions': 'Hand wash', # Care instructions (optional)
    'in_stock': True,                 # Stock status (optional)
    'stock_quantity': 10,             # Stock count (optional)
    'tags': ['summer', 'casual'],     # Tags for search (optional)
}
```

---

## 📝 Example Product Entry

```python
{
    'id': 7,
    'name': 'Ocean Breeze Crochet Top',
    'price': 79.99,
    'image': 'https://images.unsplash.com/photo-1590736969955-71cc94901144?q=80&w=2070',
    'category': 'tops',
    'description': 'A beautiful crochet top featuring soft ocean-inspired colors. Handcrafted with premium yarn, this piece is perfect for summer days and beach outings.',
    'color': 'mint',
    'popular': True,
    'new': True,
    'sale': False,
    'images': [
        'https://images.unsplash.com/photo-1590736969955-71cc94901144?q=80&w=2070',
        'https://images.unsplash.com/photo-1590736969955-71cc94901144?q=80&w=2070',
    ],
    'sizes': ['S', 'M', 'L'],
    'materials': '100% Premium Cotton Yarn',
    'care_instructions': 'Hand wash cold, lay flat to dry',
    'in_stock': True,
    'stock_quantity': 15,
    'tags': ['summer', 'beach', 'casual', 'crochet'],
}
```

---

## 🔍 What Will Be Used

### **For Product Listings (Shop Page):**
- `id`, `name`, `price`, `image`, `category`, `description` (preview)
- `popular`, `new`, `sale` (for filtering)
- `color` (for color filtering)

### **For Product Detail Page (Coming Soon):**
- All fields will be used
- `images` array for image gallery
- `sizes` for size selection
- `materials` and `care_instructions` for product info
- `in_stock` and `stock_quantity` for inventory

### **For Search:**
- Searches through: `name`, `description`, `category`, `tags`

---

## 📍 Current Location

Right now, products are defined in:
- **File:** `app.py`
- **Variable:** `PRODUCTS` (starting around line 10)

You can either:
1. Replace the existing `PRODUCTS` array with your data
2. Append to it
3. Share your dataset and I'll integrate it

---

## 💡 Tips

1. **Images**: Use URLs to hosted images (Unsplash, your own hosting, etc.)
2. **IDs**: Make sure each product has a unique ID
3. **Categories**: Stick to: 'tops', 'bags', 'accessories' (or add more if needed)
4. **Descriptions**: The longer and more detailed, the better for SEO and user experience
5. **Tags**: Helpful for search functionality

---

## 📤 How to Share Your Dataset

When you're ready, you can:
1. **Share the data directly** - Paste it here and I'll integrate it
2. **Create a file** - Make `products.json` or `products.csv` and share it
3. **Update app.py directly** - Replace the PRODUCTS array yourself

Let me know when you have your dataset ready! 🎉

