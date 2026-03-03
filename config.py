import os

class Config:
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_default_secret_key")

    # Database configuration
    # Use environment variable if available (for production), else fallback to local MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:RAMJEEV07@localhost/olivemart"
    )

    # Disable tracking modifications to save overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload configuration
    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}