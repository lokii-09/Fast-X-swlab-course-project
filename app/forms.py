from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange

# Login form definition
class LoginForm(FlaskForm):
    phone = StringField('Phone Number', validators=[
        DataRequired(), Length(min=10, max=10, message="Phone number must be 10 digits.")
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Customer', 'Customer'),
        ('Delivery Agent', 'Delivery Agent')
    ], validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddItemForm(FlaskForm):
    item_name = StringField('Item Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message="Item name must be between 2 and 50 characters.")
    ])
    item_type = SelectField('Item Type', choices=[
        ('Fruits', 'Fruits'),
        ('Vegetables', 'Vegetables'),
        ('Dairy', 'Dairy'),
        ('Bakery', 'Bakery'),
        ('Meat', 'Meat'),
        ('Seafood', 'Seafood'),
        ('Grains', 'Grains'),
        ('Snacks', 'Snacks'),
        ('Beverages', 'Beverages'),
        ('Breakfast', 'Breakfast'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    price = FloatField('Price', validators=[
        DataRequired(),
        NumberRange(min=0.01, max=1000, message="Price must be between 0.01 and 1000.")
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000, message="Stock must be between 1 and 1000.")
    ])
    discount = IntegerField('Discount (%)', validators=[
        NumberRange(min=0, max=100, message="Discount must be between 0 and 100.")
    ], default=0)
    submit = SubmitField('Add Item')

class UpdateItemForm(FlaskForm):
    price = FloatField('Price', validators=[
        DataRequired(),
        NumberRange(min=0.01, max=1000, message="Price must be between 0.01 and 1000.")
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000, message="Stock must be between 0 and 1000.")
    ])
    discount = IntegerField('Discount (%)', validators=[
        NumberRange(min=0, max=100, message="Discount must be between 0 and 100.")
    ])
    submit = SubmitField('Update Item')
