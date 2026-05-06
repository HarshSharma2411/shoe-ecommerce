from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "store.db")

app = Flask(__name__)
app.secret_key = "fashion-store-secret-key"
app.config["SESSION_COOKIE_NAME"] = "fashion_store_session"

PRODUCTS = [
    {
        "id": 1,
        "name": "Luxe Satin Slip Dress",
        "category": "Clothing",
        "price": 89.00,
        "description": "A sleek satin slip dress with a modern silhouette and adjustable straps.",
        "image_url": "/static/images/product-1.svg",
        "stock": 12,
        "rating": 4.8,
        "tags": "dress, satin, bridal"
    },
    {
        "id": 2,
        "name": "Classic Leather Handbag",
        "category": "Accessories",
        "price": 129.00,
        "description": "Timeless polished leather handbag with gold hardware and a removable shoulder strap.",
        "image_url": "/static/images/product-2.svg",
        "stock": 20,
        "rating": 4.7,
        "tags": "bag, leather, everyday"
    },
    {
        "id": 3,
        "name": "Scented Oud Eau de Parfum",
        "category": "Fragrances",
        "price": 72.00,
        "description": "Warm woody fragrance with notes of oud, amber, and bergamot for all-day elegance.",
        "image_url": "/static/images/product-3.svg",
        "stock": 35,
        "rating": 4.9,
        "tags": "perfume, luxury, unisex"
    },
    {
        "id": 4,
        "name": "Chain-Link Statement Necklace",
        "category": "Accessories",
        "price": 48.00,
        "description": "Bold chain-link necklace that elevates both day and evening looks.",
        "image_url": "/static/images/product-4.svg",
        "stock": 30,
        "rating": 4.6,
        "tags": "jewelry, necklace, statement"
    },
    {
        "id": 5,
        "name": "Signature Tailored Blazer",
        "category": "Clothing",
        "price": 114.00,
        "description": "Structured blazer with a flattering fit and timeless tailoring details.",
        "image_url": "/static/images/product-5.svg",
        "stock": 15,
        "rating": 4.5,
        "tags": "blazer, workwear, tailored"
    },
    {
        "id": 6,
        "name": "Casual Platform Sneakers",
        "category": "Shoes",
        "price": 76.00,
        "description": "Comfortable yet chic platform sneakers for city strolls and weekend styling.",
        "image_url": "/static/images/product-6.svg",
        "stock": 18,
        "rating": 4.4,
        "tags": "sneakers, casual, sporty"
    },
    {
        "id": 7,
        "name": "Silk Scarf Duo Pack",
        "category": "Accessories",
        "price": 34.00,
        "description": "Two luxurious silk scarves in matching prints for styling around the neck, bag, or hair.",
        "image_url": "/static/images/product-7.svg",
        "stock": 40,
        "rating": 4.7,
        "tags": "scarf, silk, gift"
    },
    {
        "id": 8,
        "name": "Modern Wide-Leg Trousers",
        "category": "Clothing",
        "price": 68.00,
        "description": "Effortless wide-leg trousers with a high-rise waist and minimal tailoring.",
        "image_url": "/static/images/product-8.svg",
        "stock": 22,
        "rating": 4.3,
        "tags": "trousers, tailored, workwear"
    },
    {
        "id": 9,
        "name": "Velvet Evening Clutch",
 "category": "Accessories",
        "price": 54.00,
        "description": "Luxurious velvet clutch with a detachable chain and magnetic closure.",
        "image_url": "/static/images/product-9.svg",
        "stock": 25,
        "rating": 4.6,
        "tags": "clutch, evening, velvet"
    },
    {
        "id": 10,
        "name": "Fresh Citrus Body Mist",
        "category": "Fragrances",
        "price": 28.00,
        "description": "Light citrus body mist with energizing notes of orange blossom and mint.",
        "image_url": "/static/images/product-10.svg",
        "stock": 50,
        "rating": 4.2,
        "tags": "body mist, fresh, daytime"
    },
    {
        "id": 11,
        "name": "Elegant Silk Blouse",
        "category": "Clothing",
        "price": 52.00,
        "description": "Sophisticated silk blouse with a delicate floral print and a flattering fit.",
        "image_url": "/static/images/product-11.svg",
        "stock": 28,
        "rating": 4.5,
        "tags": "blouse, silk, elegant"
    },
    {
        "id": 12,
        "name": "Premium Leather Loafers",
        "category": "Shoes",
        "price": 95.00,
        "description": "Timeless leather loafers with a comfortable fit and sophisticated appeal, perfect for both casual and professional settings.",
        "image_url": "/static/images/product-12.svg",
        "stock": 16,
        "rating": 4.7,
        "tags": "loafers, leather, professional"
    }
]

CATEGORIES = sorted({product["category"] for product in PRODUCTS})


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, description TEXT, image_url TEXT, stock INTEGER, rating REAL, tags TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, email TEXT, address TEXT, city TEXT, postal_code TEXT, country TEXT, total REAL, items TEXT)"
    )
    # Add flash sale columns to products if they don't exist yet
    for col_def in [
        "ALTER TABLE products ADD COLUMN flash_sale INTEGER DEFAULT 0",
        "ALTER TABLE products ADD COLUMN flash_sale_price REAL",
    ]:
        try:
            conn.execute(col_def)
        except sqlite3.OperationalError:
            pass  # Column already exists
    # Create flash_sales table
    conn.execute(
        "CREATE TABLE IF NOT EXISTS flash_sales (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT NOT NULL, end_time TEXT NOT NULL, is_active INTEGER DEFAULT 1)"
    )
    # Seed products if table is empty
    if not conn.execute("SELECT 1 FROM products LIMIT 1").fetchone():
        for product in PRODUCTS:
            conn.execute(
                "INSERT INTO products (id, name, category, price, description, image_url, stock, rating, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    product["id"],
                    product["name"],
                    product["category"],
                    product["price"],
                    product["description"],
                    product["image_url"],
                    product["stock"],
                    product["rating"],
                    product["tags"],
                ),
            )
    conn.commit()
    conn.close()


def query_products(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return rows[0] if one and rows else rows


def get_active_flash_sale():
    """Return the currently active flash sale row, or None if no sale is running."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cur = conn.execute(
        "SELECT * FROM flash_sales WHERE is_active = 1 AND start_time <= ? AND end_time >= ? LIMIT 1",
        (now, now),
    )
    row = cur.fetchone()
    conn.close()
    return row


@app.context_processor
def inject_flash_sale():
    """Make active_sale available in every template."""
    return dict(active_sale=get_active_flash_sale())


def get_cart_items():
    cart = session.get("cart", {})
    if not cart:
        return []
    placeholder = []
    ids = tuple(cart.keys())
    products = query_products(f"SELECT * FROM products WHERE id IN ({','.join('?' for _ in ids)})", ids)
    active_sale = get_active_flash_sale()
    for product in products:
        quantity = cart[str(product["id"])] if str(product["id"]) in cart else cart.get(product["id"], 0)
        on_flash_sale = bool(active_sale and product["flash_sale"] and product["flash_sale_price"])
        price = product["flash_sale_price"] if on_flash_sale else product["price"]
        placeholder.append({
            "id": product["id"],
            "name": product["name"],
            "price": price,
            "original_price": product["price"],
            "on_flash_sale": on_flash_sale,
            "quantity": quantity,
            "subtotal": price * quantity,
            "image_url": product["image_url"],
        })
    return placeholder


@app.route("/")
def index():
    featured = query_products("SELECT * FROM products ORDER BY rating DESC LIMIT 6")
    new_arrivals = query_products("SELECT * FROM products ORDER BY id DESC LIMIT 4")
    categories = CATEGORIES
    active_sale = get_active_flash_sale()
    flash_sale_products = []
    if active_sale:
        flash_sale_products = query_products(
            "SELECT * FROM products WHERE flash_sale = 1 ORDER BY rating DESC LIMIT 4"
        )
    return render_template(
        "index.html",
        featured=featured,
        new_arrivals=new_arrivals,
        categories=categories,
        active_sale=active_sale,
        flash_sale_products=flash_sale_products,
    )


@app.route("/category/<category_name>")
def category(category_name):
    products = query_products("SELECT * FROM products WHERE category = ? ORDER BY rating DESC", (category_name,))
    categories = CATEGORIES
    active_sale = get_active_flash_sale()
    return render_template("category.html", products=products, category_name=category_name, categories=categories, active_sale=active_sale)


@app.route("/product/<int:product_id>")
def product(product_id):
    product = query_products("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if not product:
        return render_template("404.html"), 404
    categories = CATEGORIES
    active_sale = get_active_flash_sale()
    return render_template("product.html", product=product, categories=categories, active_sale=active_sale)


@app.route("/search")
def search():
    query_text = request.args.get("q", "").strip()
    categories = CATEGORIES
    products = []
    if query_text:
        wildcard = f"%{query_text}%"
        products = query_products(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ? OR tags LIKE ? ORDER BY rating DESC",
            (wildcard, wildcard, wildcard),
        )
    return render_template("category.html", products=products, category_name=f"Search results for '{query_text}'", categories=categories)


@app.route("/flash-sale")
def flash_sale():
    active_sale = get_active_flash_sale()
    categories = CATEGORIES
    products = []
    sale_end_time = None
    if active_sale:
        products = query_products(
            "SELECT * FROM products WHERE flash_sale = 1 ORDER BY rating DESC"
        )
        sale_end_time = active_sale["end_time"]
    return render_template(
        "flash_sale.html",
        products=products,
        active_sale=active_sale,
        sale_end_time=sale_end_time,
        categories=categories,
    )


@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id")
    qty = int(request.form.get("quantity", 1))
    if not product_id:
        return redirect(url_for("index"))
    cart = session.setdefault("cart", {})
    cart[product_id] = cart.get(product_id, 0) + qty
    session["cart"] = cart
    flash("Item added to your bag.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart")
def cart():
    items = get_cart_items()
    total = sum(item["subtotal"] for item in items)
    categories = CATEGORIES
    return render_template("cart.html", items=items, total=total, categories=categories)


@app.route("/update-cart", methods=["POST"])
def update_cart():
    cart = session.get("cart", {})
    for product_id, quantity in request.form.items():
        if product_id.startswith("qty_"):
            pid = product_id.replace("qty_", "")
            try:
                qty = max(0, int(quantity))
            except ValueError:
                qty = 0
            if qty > 0:
                cart[pid] = qty
            elif pid in cart:
                del cart[pid]
    session["cart"] = cart
    flash("Your cart has been updated.", "info")
    return redirect(url_for("cart"))


@app.route("/clear-cart")
def clear_cart():
    session.pop("cart", None)
    flash("Your bag is now empty.", "info")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = get_cart_items()
    if not items:
        flash("Your bag is empty. Add an item before checking out.", "warning")
        return redirect(url_for("cart"))
    total = sum(item["subtotal"] for item in items)
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        postal_code = request.form.get("postal_code", "").strip()
        country = request.form.get("country", "").strip()

        if not all([full_name, email, address, city, postal_code, country]):
            flash("Please fill in all required fields.", "danger")
            return render_template("checkout.html", items=items, total=total, categories=CATEGORIES)

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO orders (full_name, email, address, city, postal_code, country, total, items) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                full_name,
                email,
                address,
                city,
                postal_code,
                country,
                total,
                "; ".join([f"{item['name']} x{item['quantity']}" for item in items]),
            ),
        )
        conn.commit()
        conn.close()
        session.pop("cart", None)
        flash("Thank you for your order! Your purchase has been processed.", "success")
        return redirect(url_for("index"))

    return render_template("checkout.html", items=items, total=total, categories=CATEGORIES)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not all([name, email, message]):
            flash("Please complete the contact form.", "danger")
        else:
            flash("Thanks for reaching out! We will reply soon.", "success")
            return redirect(url_for("contact"))
    categories = CATEGORIES
    return render_template("contact.html", categories=categories)


@app.route("/sitemap")
def sitemap():
    categories = CATEGORIES
    products = query_products("SELECT * FROM products ORDER BY category, name")
    pages = [
        {"name": "Home", "url": url_for("index")},
        {"name": "Bag", "url": url_for("cart")},
        {"name": "Checkout", "url": url_for("checkout")},
        {"name": "Contact", "url": url_for("contact")},
    ]
    return render_template("sitemap.html", categories=categories, products=products, pages=pages)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", categories=CATEGORIES), 404


initialize_database()

if __name__ == "__main__":
    app.run(debug=True)
