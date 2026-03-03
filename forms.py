# forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

# -------------------- REGISTER FORM --------------------
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

# -------------------- LOGIN FORM --------------------
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# -------------------- PRODUCT FORM --------------------
class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    price = FloatField("Price", validators=[DataRequired()])
    image = FileField(
        "Product Image",
        validators=[FileAllowed(["jpg", "png", "jpeg", "gif"], "Images only!")]
    )
    submit = SubmitField("Add Product")