from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize the database
db = SQLAlchemy()


# =====================================================
# USER MODEL
# =====================================================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    cart_items = db.relationship(
        "CartItem", back_populates="user", cascade="all, delete-orphan"
    )
    invoices = db.relationship(
        "Invoice", back_populates="user", cascade="all, delete-orphan"
    )

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


# =====================================================
# CATEGORY MODEL
# =====================================================
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationships
    products = db.relationship("Product", back_populates="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"


# =====================================================
# PRODUCT MODEL
# =====================================================
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=100)
    brand = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(200), default="default.png")
    rating = db.Column(db.Float, default=4.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    category = db.relationship("Category", back_populates="products")
    cart_items = db.relationship(
        "CartItem", back_populates="product", cascade="all, delete-orphan"
    )
    invoice_items = db.relationship(
        "InvoiceItem", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Product {self.name}>"


# =====================================================
# CART ITEM MODEL
# =====================================================
class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="cart_items")
    product = db.relationship("Product", back_populates="cart_items")

    # Subtotal calculation
    def subtotal(self):
        return self.quantity * self.product.price

    def __repr__(self):
        return f"<CartItem {self.product.name} x {self.quantity}>"


# =====================================================
# INVOICE MODEL
# =====================================================
class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="invoices")
    items = db.relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Invoice #{self.id} - User {self.user_id}>"


# =====================================================
# INVOICE ITEM MODEL
# =====================================================
class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    invoice = db.relationship("Invoice", back_populates="items")
    product = db.relationship("Product", back_populates="invoice_items")

    # Subtotal calculation
    def subtotal(self):
        return self.quantity * self.price

    def __repr__(self):
        return f"<InvoiceItem {self.product.name} x {self.quantity}>"