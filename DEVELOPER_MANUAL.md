# Developer Manual - Fashion Store

This manual provides comprehensive documentation for developers who need to understand, maintain, and extend the Fashion Store Flask application.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technical Stack](#technical-stack)
3. [Project Structure](#project-structure)
4. [Setup & Installation](#setup--installation)
5. [Application Architecture](#application-architecture)
6. [Database Schema](#database-schema)
7. [Routes & Endpoints](#routes--endpoints)
8. [Key Functions](#key-functions)
9. [Template System](#template-system)
10. [Extending the Application](#extending-the-application)
11. [Testing & Debugging](#testing--debugging)
12. [Deployment](#deployment)

---

## Project Overview

The Fashion Store is a web-based e-commerce application built with Flask, a lightweight Python web framework. It provides functionality for:

- **Product Catalog**: Browse products by category
- **Product Search**: Find items using keyword search
- **Shopping Cart**: Add/remove items and manage quantities
- **Checkout System**: Process customer orders with shipping details
- **Contact Management**: Allow customers to reach out
- **Admin Database**: Store products and orders in SQLite

### Key Features

- Product rating system
- Category-based browsing
- Full-text search across product names, descriptions, and tags
- Session-based shopping cart (persists during user session)
- Order history and storage
- Responsive web interface
- Contact form for customer inquiries

---

## Technical Stack

### Backend
- **Framework**: Flask 2.3.3
- **Language**: Python 3.x
- **Database**: SQLite3
- **Session Management**: Flask sessions (server-side via cookies)

### Frontend
- **Templating**: Jinja2 (built-in with Flask)
- **Styling**: Custom CSS
- **Structure**: HTML5
- **Images**: SVG format for product images

### Dependencies

```
Flask==2.3.3
```

**Note**: The minimal dependencies make this application lightweight and easy to deploy.

---

## Project Structure

```
InClassDemo-GHC (30thApril)/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── store.db                        # SQLite database (auto-created)
├── DEMO/                           # Demo files directory
├── static/                         # Static assets
│   ├── css/
│   │   └── styles.css             # Global styles
│   └── images/                    # Product images
│       ├── product-1.svg through product-11.svg
│       └── [other assets]
└── templates/                     # HTML templates
    ├── base.html                  # Base template (extends all pages)
    ├── index.html                 # Home page
    ├── category.html              # Category & search results
    ├── product.html               # Product detail page
    ├── cart.html                  # Shopping cart
    ├── checkout.html              # Checkout form
    ├── contact.html               # Contact form
    ├── sitemap.html               # Site navigation map
    └── 404.html                   # Error page
```

---

## Setup & Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Download the Project

```bash
cd path/to/project
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venvs
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 6: Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

**Note**: The database (`store.db`) will be automatically created on first run with sample product data.

---

## Application Architecture

### Flask Application Structure

#### Initialization
```python
app = Flask(__name__)
app.secret_key = "fashion-store-secret-key"
```

- **Flask Instance**: Main application object
- **Secret Key**: Used for session encryption and security

#### Database Connection
The app uses SQLite3 for data persistence with two main tables:
- `products`: Static product information
- `orders`: Customer order records

#### Session Management
- Sessions store cart data in a dictionary format: `{product_id: quantity}`
- Sessions persist for the user's browser session
- Using `session.setdefault()` and `session["cart"]` for cart management

### Request/Response Flow

1. **User Request** → Flask Routes
2. **Route Handler** → Database Query (if needed)
3. **Data Processing** → Render Template
4. **Template Rendering** → HTML Response
5. **Browser Display** → User sees webpage

---

## Database Schema

### Products Table

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    description TEXT,
    image_url TEXT,
    stock INTEGER,
    rating REAL,
    tags TEXT
)
```

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER | Unique product identifier |
| `name` | TEXT | Product display name |
| `category` | TEXT | Product category (Clothing, Accessories, Fragrances, Shoes) |
| `price` | REAL | Product price in dollars |
| `description` | TEXT | Detailed product description |
| `image_url` | TEXT | Path to product image (SVG) |
| `stock` | INTEGER | Available quantity |
| `rating` | REAL | Customer rating (0-5 stars) |
| `tags` | TEXT | Comma-separated keywords for search |

### Orders Table

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    country TEXT,
    total REAL,
    items TEXT
)
```

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER | Auto-incrementing order identifier |
| `full_name` | TEXT | Customer's full name |
| `email` | TEXT | Customer's email address |
| `address` | TEXT | Street delivery address |
| `city` | TEXT | City for delivery |
| `postal_code` | TEXT | Postal/ZIP code |
| `country` | TEXT | Country for delivery |
| `total` | REAL | Order total in dollars |
| `items` | TEXT | Semicolon-separated list of items (e.g., "Product x3; Product x2") |

### Data Initialization

Sample products are defined in the `PRODUCTS` list in `app.py` and automatically inserted into the database on first run.

---

## Routes & Endpoints

### Public Routes

#### GET `/`
**Home Page**
- Displays 6 featured products (sorted by highest rating)
- Displays 4 new arrivals (sorted by newest ID)
- Lists all product categories
- **Template**: `index.html`

#### GET `/category/<category_name>`
**Category Page**
- Displays all products in a specific category
- Products sorted by rating (highest first)
- **Parameters**: `category_name` (string)
- **Template**: `category.html`
- **Example**: `/category/Accessories`

#### GET `/product/<product_id>`
**Product Detail Page**
- Displays detailed information about a single product
- Shows image, price, rating, description, tags
- Includes quantity selector and "Add to Cart" button
- Returns 404 if product doesn't exist
- **Parameters**: `product_id` (integer)
- **Template**: `product.html` or `404.html`

#### GET `/search`
**Search Results**
- Full-text search across product name, description, and tags
- Case-insensitive search using SQL LIKE operator
- Results sorted by rating
- **Query Parameters**: `q` (search query string)
- **Template**: `category.html` (reused with search results)
- **Example**: `/search?q=silk`

#### POST `/add-to-cart`
**Add Item to Cart**
- Adds product to user's shopping cart
- Increments quantity if product already in cart
- Stores cart in Flask session
- **Form Parameters**:
  - `product_id` (required)
  - `quantity` (optional, defaults to 1)
- **Response**: Redirects to referring page or home
- **Flash Message**: "Item added to your bag."

#### GET `/cart`
**View Shopping Cart**
- Displays all items in user's cart
- Shows quantity, unit price, and subtotal for each item
- Calculates and displays cart total
- Provides links to update or clear cart
- **Template**: `cart.html`

#### POST `/update-cart`
**Update Cart Quantities**
- Updates quantities for items in cart
- Removes items with quantity 0
- Accepts form data with keys like `qty_<product_id>`
- **Response**: Redirects to cart page
- **Flash Message**: "Your cart has been updated."

#### GET `/clear-cart`
**Clear Shopping Cart**
- Removes all items from cart
- Clears the session cart data
- **Response**: Redirects to cart page
- **Flash Message**: "Your bag is now empty."

#### GET/POST `/checkout`
**Checkout Page & Order Processing**

**GET `/checkout`**:
- Displays checkout form and order summary
- Shows all cart items and total
- Redirects to cart if cart is empty
- **Template**: `checkout.html`

**POST `/checkout`**:
- Processes customer order
- Validates all required fields
- Inserts order into database
- Clears cart on successful order
- **Form Parameters**:
  - `full_name` (required)
  - `email` (required)
  - `address` (required)
  - `city` (required)
  - `postal_code` (required)
  - `country` (required)
- **Response**: Redirects to home on success, returns form on validation failure
- **Flash Message**: "Thank you for your order! Your purchase has been processed."

#### GET/POST `/contact`
**Contact Form**

**GET `/contact`**:
- Displays contact form
- **Template**: `contact.html`

**POST `/contact`**:
- Validates contact form submission
- Displays success message (current implementation doesn't store messages)
- **Form Parameters**:
  - `name` (required)
  - `email` (required)
  - `message` (required)
- **Response**: Redirects to contact page
- **Flash Message**: "Thanks for reaching out! We will reply soon." or validation error

#### GET `/sitemap`
**Sitemap/Navigation**
- Displays all categories, products, and important pages
- Products organized by category
- Useful for site navigation and SEO
- **Template**: `sitemap.html`

#### GET `/non-existent-page` (any undefined route)
**404 Error Handler**
- Returns 404 error page for undefined routes
- Shows available categories
- **Template**: `404.html`

---

## Key Functions

### Database Functions

#### `get_db_connection()`
```python
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
```
- Establishes connection to SQLite database
- `row_factory = sqlite3.Row` allows accessing columns by name
- **Returns**: Connection object

#### `initialize_database()`
```python
def initialize_database():
    if not os.path.exists(DATABASE):
        # Creates tables and inserts sample products
```
- Creates database tables on first application run
- Inserts sample product data from `PRODUCTS` list
- Only runs if `store.db` doesn't exist
- Called in `if __name__ == "__main__"` block

#### `query_products(query, args=(), one=False)`
```python
def query_products(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return rows[0] if one and rows else rows
```
- Generic database query function
- **Parameters**:
  - `query`: SQL query string with `?` placeholders
  - `args`: Tuple of values for query parameters
  - `one`: Boolean to return single row vs. list
- **Returns**: Single row dict or list of row dicts

### Cart Functions

#### `get_cart_items()`
```python
def get_cart_items():
    cart = session.get("cart", {})
    if not cart:
        return []
    # Fetch product details from database for cart items
```
- Retrieves current shopping cart from session
- Fetches product details for each cart item from database
- Calculates subtotal for each item (price × quantity)
- **Returns**: List of cart item dictionaries with:
  - `id`: Product ID
  - `name`: Product name
  - `price`: Unit price
  - `quantity`: Quantity in cart
  - `subtotal`: Price × Quantity
  - `image_url`: Product image

### Data Structure: PRODUCTS List

```python
PRODUCTS = [
    {
        "id": 1,
        "name": "Luxe Satin Slip Dress",
        "category": "Clothing",
        "price": 89.00,
        "description": "...",
        "image_url": "/static/images/product-1.svg",
        "stock": 12,
        "rating": 4.8,
        "tags": "dress, satin, bridal"
    },
    # ... more products
]
```
- Defines sample product data
- Automatically inserted into database on first run
- 12 products across 4 categories
- Ratings range from 4.2 to 4.9 stars

### Data Structure: CATEGORIES

```python
CATEGORIES = sorted({product["category"] for product in PRODUCTS})
```
- Automatically extracted from products
- Sorted alphabetically: Accessories, Clothing, Fragrances, Shoes
- Passed to every template for navigation

#### Latest Product Added

**Product 12 - Premium Leather Loafers**
- **Category**: Shoes
- **Price**: $95.00
- **Stock**: 16 units
- **Rating**: 4.7 stars
- **Description**: Timeless leather loafers with a comfortable fit and sophisticated appeal, perfect for both casual and professional settings.
- **Tags**: loafers, leather, professional
- **Image**: `/static/images/product-12.svg`

---

## Template System

All templates extend from `base.html` which provides:
- Navigation bar with category links
- Search bar
- Flash message display area
- Footer with links to sitemap and contact

### Base Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <!-- CSS files -->
    {% block head %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <!-- Flash messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <!-- Display message -->
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    {% block content %}{% endblock %}
    
    <!-- Footer -->
</body>
</html>
```

### Template Variables Passed from Routes

**Common Variables** (passed to most templates):
- `categories`: List of all product categories

**Home Page** (`index.html`):
- `featured`: Top 6 products by rating
- `new_arrivals`: 4 newest products

**Category Page** (`category.html`):
- `products`: Products in category or search results
- `category_name`: Display name for the page

**Product Page** (`product.html`):
- `product`: Single product object

**Cart Page** (`cart.html`):
- `items`: List of cart items
- `total`: Cart total

**Checkout Page** (`checkout.html`):
- `items`: Cart items for order summary
- `total`: Order total

### Template Filters & Functions

**Jinja2 Built-ins Used**:
- `{{ variable }}`: Output variable
- `{% if condition %}`: Conditional rendering
- `{% for item in list %}`: Loop iteration
- `{{ variable | filter }}`: Apply filters
- `url_for('route_name')`: Generate URLs
- `get_flashed_messages()`: Retrieve flash messages

---

## Extending the Application

### Adding a New Product Category

1. **Update PRODUCTS list** in `app.py`:
```python
PRODUCTS.append({
    "id": 13,
    "name": "New Product",
    "category": "New Category",  # Will auto-appear in CATEGORIES
    "price": 99.00,
    "description": "...",
    "image_url": "/static/images/product-13.svg",
    "stock": 10,
    "rating": 4.5,
    "tags": "tag1, tag2, tag3"
})
```

2. **Delete store.db** (optional, to reinitialize database)

3. **Restart the application**

### Adding a New Product

**Method 1: Update PRODUCTS list (before first run)**:
- Add new dictionary to `PRODUCTS` list
- Set unique `id`
- Include all required fields
- Add SVG image to `/static/images/`

**Method 2: Insert directly into database (after initialization)**:
```python
conn = get_db_connection()
conn.execute(
    "INSERT INTO products (id, name, category, price, description, image_url, stock, rating, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (13, "Product Name", "Category", 99.00, "Description", "/static/images/product-13.svg", 10, 4.5, "tag1, tag2")
)
conn.commit()
conn.close()
```

### Adding a New Route

Example: Add a "Best Sellers" page:

```python
@app.route("/best-sellers")
def best_sellers():
    products = query_products("SELECT * FROM products WHERE rating >= 4.7 ORDER BY rating DESC")
    return render_template("category.html", products=products, category_name="Best Sellers", categories=CATEGORIES)
```

Then add navigation link in `base.html`:
```html
<a href="{{ url_for('best_sellers') }}">Best Sellers</a>
```

### Adding a New Template

1. **Create new file** in `templates/` directory (e.g., `reviews.html`)

2. **Extend base template**:
```html
{% extends "base.html" %}

{% block content %}
    <!-- Your content -->
{% endblock %}
```

3. **Add route** to render the template:
```python
@app.route("/reviews")
def reviews():
    return render_template("reviews.html", categories=CATEGORIES)
```

### Storing Contact Messages

Currently, contact form submissions are not stored. To add persistence:

```python
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        
        if not all([name, email, message]):
            flash("Please complete the contact form.", "danger")
        else:
            # Add this section to store messages
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO contact_messages (name, email, message, created_at) VALUES (?, ?, ?, datetime('now'))",
                (name, email, message)
            )
            conn.commit()
            conn.close()
            
            flash("Thanks for reaching out! We will reply soon.", "success")
            return redirect(url_for("contact"))
    
    categories = CATEGORIES
    return render_template("contact.html", categories=categories)
```

### Implementing User Authentication

To add user login functionality:

1. **Create users table**:
```python
conn.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
```

2. **Use Flask-Login extension** (install via pip):
```bash
pip install Flask-Login
```

3. **Implement login/register routes** following Flask-Login documentation

### Adding Product Reviews

1. **Create reviews table**:
```python
conn.execute("""
    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        user_name TEXT,
        rating INTEGER,
        review_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
""")
```

2. **Add review submission route**:
```python
@app.route("/add-review/<int:product_id>", methods=["POST"])
def add_review(product_id):
    user_name = request.form.get("user_name", "").strip()
    rating = int(request.form.get("rating", 5))
    review_text = request.form.get("review_text", "").strip()
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO reviews (product_id, user_name, rating, review_text) VALUES (?, ?, ?, ?)",
        (product_id, user_name, rating, review_text)
    )
    conn.commit()
    conn.close()
    
    flash("Thank you for your review!", "success")
    return redirect(url_for("product", product_id=product_id))
```

3. **Display reviews on product page** in `product.html`

### Using Pagination for Products

To limit products displayed per page:

```python
@app.route("/category/<category_name>")
def category(category_name):
    page = request.args.get("page", 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page
    
    products = query_products(
        "SELECT * FROM products WHERE category = ? ORDER BY rating DESC LIMIT ? OFFSET ?",
        (category_name, per_page, offset)
    )
    
    total_count = query_products(
        "SELECT COUNT(*) as count FROM products WHERE category = ?",
        (category_name,),
        one=True
    )
    
    total_pages = (total_count['count'] + per_page - 1) // per_page
    
    categories = CATEGORIES
    return render_template(
        "category.html",
        products=products,
        category_name=category_name,
        categories=categories,
        current_page=page,
        total_pages=total_pages
    )
```

---

## Testing & Debugging

### Debug Mode

Flask runs in debug mode by default (see `app.run(debug=True)`):
- **Auto-reloads** when code changes
- **Interactive debugger** on errors
- **Stack trace** in browser

### Accessing Debug Information

1. **Check console output** when running `python app.py`
2. **View error pages** in browser (when debug=True)
3. **Use Python print statements** (output to console)

### Testing Routes Manually

Use your browser or curl:

```bash
# Browse to home
curl http://localhost:5000/

# Search
curl "http://localhost:5000/search?q=silk"

# Product details
curl http://localhost:5000/product/1

# Category
curl http://localhost:5000/category/Accessories
```

### Testing Checkout Flow

1. Navigate to home page
2. Add item to cart
3. Go to cart
4. Click checkout
5. Fill form with test data
6. Submit order
7. Check console for order insertion

### Database Inspection

```python
# In Python shell or test script
from app import query_products

# View all products
products = query_products("SELECT * FROM products")
for p in products:
    print(f"{p['id']}: {p['name']} - ${p['price']}")

# View all orders
orders = query_products("SELECT * FROM orders")
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "ModuleNotFoundError: No module named 'flask'" | Flask not installed | Run `pip install -r requirements.txt` |
| Database errors | First run issue | Delete `store.db` and restart |
| 404 on images | Wrong image path | Verify images exist in `/static/images/` |
| Cart not persisting | Cookies disabled | Enable cookies in browser |
| Session lost | Secret key changed | Restart browser after code changes |

---

## Deployment

### Production Configuration

Before deploying, change these settings in `app.py`:

```python
# Change this
app.run(debug=True)

# To this
app.run(debug=False)

# And change the secret key to something secure
app.secret_key = "generate-secure-random-key-here"
```

### Generating Secure Secret Key

```python
import secrets
secure_key = secrets.token_hex(32)
print(secure_key)
```

### Deployment Options

#### Option 1: Using Gunicorn (Recommended for Production)

1. **Install Gunicorn**:
```bash
pip install gunicorn
```

2. **Create `wsgi.py`**:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

3. **Run with Gunicorn**:
```bash
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
```

#### Option 2: Heroku Deployment

1. **Create `Procfile`**:
```
web: gunicorn app:app
```

2. **Deploy**:
```bash
git init
git add .
git commit -m "Initial commit"
heroku login
heroku create your-app-name
git push heroku main
```

#### Option 3: PythonAnywhere

1. Upload files to PythonAnywhere
2. Configure web app pointing to `app.py`
3. Set environment variables for production

### Environment Variables

For production, use environment variables for sensitive data:

```python
import os

app.secret_key = os.environ.get("SECRET_KEY", "dev-key")
DATABASE = os.environ.get("DATABASE", "store.db")
DEBUG = os.environ.get("DEBUG", "False") == "True"
```

### Database Backup

Regularly backup `store.db`:

```bash
# Windows
copy store.db store.db.backup

# Linux/Mac
cp store.db store.db.backup
```

### Performance Optimization

1. **Use caching** for frequently accessed products:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_categories():
    return CATEGORIES
```

2. **Add database indexing**:
```python
conn.execute("CREATE INDEX idx_category ON products(category)")
```

3. **Compress static files** (CSS, images)

4. **Use CDN** for static assets in production

---

## Contributing Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and single-purpose

### Testing Changes

1. Test locally before committing
2. Verify all routes work
3. Check database queries
4. Test edge cases (empty cart, invalid product ID, etc.)

### Committing Code

```bash
git add .
git commit -m "Descriptive message about changes"
git push origin branch-name
```

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Jinja2 Template Engine](https://jinja.palletsprojects.com/)
- [HTML/CSS Reference](https://developer.mozilla.org/en-US/)

---

## Support & Questions

For issues or questions about the codebase:
1. Check this documentation first
2. Review the inline code comments
3. Check Flask documentation for framework-specific questions
4. Review git history for recent changes

---

**Last Updated**: April 30, 2026
**Framework Version**: Flask 2.3.3
**Python Version**: 3.7+

