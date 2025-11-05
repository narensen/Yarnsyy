# Yarnsy - Handcrafted Crochet Boutique E-commerce

A fully responsive, modern e-commerce website for a boutique store specializing in handcrafted crochet tops and accessories. Built with React, Tailwind CSS, Framer Motion, and Flask backend.

## 🌸 Features

- **Responsive Design**: Mobile-first approach with beautiful breakpoints
- **Modern UI/UX**: Soft pastel boutique aesthetic with smooth animations
- **Product Browsing**: Dynamic product grid with filtering and search
- **Shopping Cart**: Persistent cart with localStorage (no backend required)
- **Checkout Flow**: Complete checkout process with order confirmation
- **Order Tracking**: View past orders with status tracking
- **AI Assistant**: "Meow" chat assistant for shopping help
- **Backend API**: Flask REST API for products, orders, and recommendations
- **CSV-Based Products**: Products loaded from CSV file (no database required)

## 🗄️ Data Storage

- **Products**: Loaded from `new_products.csv` (12 handcrafted items)
- **Cart**: Managed in browser localStorage (frontend)
- **No MongoDB Required**: Simple CSV-based product storage

## 🎨 Design Theme

- **Colors**: Cream (#FFF9F8), Lavender (#C9B6E4), Pink Blush (#EAD8EB), Charcoal (#333333)
- **Typography**: Playfair Display (headings) + Poppins (body)
- **Style**: Minimal, elegant, cozy with soft shadows and rounded edges

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- npm or yarn
- **No MongoDB required!**

### Installation

1. **Clone the repository**
   ```bash
   cd Yarnsy
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask backend** (in one terminal)
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

2. **Start the React development server** (in another terminal)
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

3. **Open your browser**
   Navigate to `http://localhost:3000` to see the application

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## 📁 Project Structure

```
Yarnsy/
├── src/
│   ├── components/      # Reusable React components
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   ├── ProductCard.jsx
│   │   ├── ProductGrid.jsx
│   │   ├── CategoryCard.jsx
│   │   ├── FilterSidebar.jsx
│   │   ├── Newsletter.jsx
│   │   └── MeowAssistant.jsx
│   ├── pages/           # Page components
│   │   ├── Home.jsx
│   │   ├── About.jsx
│   │   ├── Shop.jsx
│   │   ├── Cart.jsx
│   │   ├── Checkout.jsx
│   │   ├── MyOrders.jsx
│   │   └── OrderConfirmation.jsx
│   ├── context/         # React Context providers
│   │   └── CartContext.jsx
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles with Tailwind
├── app.py               # Flask backend API
├── requirements.txt     # Python dependencies
├── package.json         # Node dependencies
├── tailwind.config.js   # Tailwind CSS configuration
├── vite.config.js      # Vite configuration
└── README.md
```

## 🛍️ Pages

- **Home**: Hero section, category highlights, featured products, newsletter
- **About**: Brand philosophy, story, stats, founder's note
- **Shop**: Product grid with filtering (category, color, price, popularity)
- **Cart**: Shopping cart with quantity management
- **Checkout**: Shipping and payment forms
- **Order Confirmation**: Success page with order details
- **My Orders**: Order history with tracking status

## 🤖 AI Assistant - Meow 🐾

Floating chat assistant that helps with:
- Product recommendations
- Order tracking
- Crochet care instructions
- Gift ideas

## 🔌 API Endpoints

- `GET /` - API health check and info
- `GET /api/products` - Get all products (with optional filtering)
- `GET /api/products/:id` - Get specific product
- `GET /api/products/:id/details` - Get product with related items
- `GET /api/recommendations` - Get personalized product recommendations
- `GET /api/connection-status` - Get data source status (CSV-based)
- `GET /api/cart` - Get cart (managed in localStorage)
- `POST /api/cart` - Add to cart (returns success)
- `DELETE /api/cart` - Remove from cart (returns success)
- `GET /api/orders` - Get user's orders
- `GET /api/orders/:id` - Get specific order
- `GET /api/shipping` - Get shipping/tracking info
- `GET /api/health` - Health check

## 🎯 Key Technologies

- **React 18**: Modern React with hooks and context
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Vite**: Fast build tool and dev server
- **Flask**: Python backend API
- **Axios**: HTTP client for API calls
- **Lucide React**: Icon library

## 📱 Mobile Responsive

The website is fully responsive with breakpoints:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## 🎨 Customization

### Colors
Edit `tailwind.config.js` to customize the color palette:
```js
colors: {
  'cream': '#FFF9F8',
  'lavender': '#C9B6E4',
  'pink-blush': '#EAD8EB',
  'charcoal': '#333333',
}
```

### Products
Add or modify products in `new_products.csv`. The first 12 products are loaded automatically.
CSV format: `id,name,price,image,category`

## 📝 License

This project is built as a portfolio/demo project.

## 🙏 Acknowledgments

- Design inspired by boutique e-commerce stores
- Images from Unsplash
- Icons from Lucide React

---

**Crafted with ❤️ and yarn.**

