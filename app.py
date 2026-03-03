import os
import uuid
from flask import Flask, render_template, redirect, url_for, session, flash, request
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import Config
from models import db, User, Product
from forms import RegisterForm, LoginForm, ProductForm

# -------------------- APP CONFIG --------------------
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config.get("UPLOAD_FOLDER", "static/uploads"), exist_ok=True)

# -------------------- DATABASE INIT --------------------
db.init_app(app)  # Initialize db with the Flask app

# -------------------- LOGIN MANAGER --------------------
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- HELPERS --------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config.get("ALLOWED_EXTENSIONS", {"png","jpg","jpeg","gif"})

def admin_required():
    if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
        flash("Access denied!", "danger")
        return False
    return True

# -------------------- ROUTES --------------------
@app.route("/")
def index():
    featured_products = Product.query.limit(4).all()
    return render_template("index.html", products=featured_products)

# ---------- AUTH ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("products"))
        flash("Invalid username or password!", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

# ---------- PRODUCTS ----------
@app.route("/products")
def products():
    all_products = Product.query.all()
    return render_template("products.html", products=all_products)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

# ---------- CART ----------
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    cart = session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session["cart"] = cart
    session.modified = True
    flash("Product added to cart!", "success")
    return redirect(request.referrer or url_for("products"))

@app.route("/cart")
def cart():
    cart_data = session.get("cart", {})
    cart_items = []
    total = 0
    for pid, qty in cart_data.items():
        product = Product.query.get(int(pid))
        if product:
            item = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": qty,
                "image": product.image or "default.png",
                "subtotal": product.price * qty
            }
            total += item["subtotal"]
            cart_items.append(item)
    return render_template("cart.html", products=cart_items, total=total)

@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    session.modified = True
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart"))

@app.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    if quantity <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = quantity
    session["cart"] = cart
    session.modified = True
    flash("Cart updated.", "success")
    return redirect(url_for("cart"))

@app.route("/checkout")
@login_required
def checkout():
    if not session.get("cart"):
        flash("Cart is empty.", "warning")
        return redirect(url_for("products"))
    session.pop("cart", None)
    flash("Order placed successfully!", "success")
    return redirect(url_for("products"))

# ---------- ADMIN ----------
@app.route("/admin")
@login_required
def admin_dashboard():
    if not admin_required():
        return redirect(url_for("index"))
    all_products = Product.query.all()
    return render_template("admin/dashboard.html", products=all_products)

@app.route("/admin/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if not admin_required():
        return redirect(url_for("index"))
    form = ProductForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            unique_name = str(uuid.uuid4()) + "_" + secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))
            filename = unique_name
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=filename
        )
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/add_product.html", form=form)

# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    # Run locally with Flask’s built-in server on Windows
    with app.app_context():
        db.create_all()  # Create tables if they don’t exist
    app.run(debug=True, host="127.0.0.1", port=5000)