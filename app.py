from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
from wtforms import FileField, SelectField
from datetime import datetime
import os
import random

app = Flask(__name__)

# Set a secret key for session management
app.config['SECRET_KEY'] = os.urandom(24)

# Setup the database URI (SQLite for local development)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup the folder for image uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize the database
db = SQLAlchemy(app)

# Define the Recipe model
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_name = db.Column(db.String(100), nullable=False)
    image_reference = db.Column(db.String(200), nullable=False)  # New field for image reference
    food_type = db.Column(db.String(50), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically add date and time

# Create the database tables (if they don't exist)
with app.app_context():
    db.create_all()

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Custom admin view to handle image upload and dropdown for food type
class RecipeView(ModelView):
    # Columns to display in the list view
    column_list = ('id', 'name', 'food_type', 'date_added')

    # Format the 'date_added' column to show only the date (no time)
    column_formatters = {
        'date_added': lambda v, c, m, p: m.date_added.strftime('%Y-%m-%d') if m.date_added else ''
    }

    # Exclude 'date_added' from the form to prevent the date picker from showing up
    form_excluded_columns = ['date_added']

    # Make food_type a dropdown in the form and image_name a file field
    form_overrides = {
        'food_type': SelectField,
        'image_name': FileField
    }

    # Predefine choices for the dropdown
    form_args = {
        'food_type': {
            'choices': [
                ('Appetizer/Snacks', 'Appetizer/Snacks'),
                ('Breakfast', 'Breakfast'),
                ('Dinner', 'Dinner'),
                ('Lunch', 'Lunch'),
                ('Soup', 'Soup')
            ]
        }
    }

    def on_model_change(self, form, model, is_created):
        # Automatically set the 'date_added' to the current date (without time) when adding a new recipe
        if is_created:
            model.date_added = datetime.utcnow().date()  # Only store the date, no time

        # Check if an image is uploaded
        if form.image_name.data:
            image = form.image_name.data
            if allowed_file(image.filename):
                # Secure the filename and save it
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                model.image_name = filename  # Save the filename to the database

# Setup Flask-Admin
admin = Admin(app, name='Recipe Admin', template_mode='bootstrap3')

# Add Recipe model to Flask-Admin
admin.add_view(RecipeView(Recipe, db.session))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        food_type = request.form.get('food_type')
        recipes = Recipe.query.filter_by(food_type=food_type).all()
        if recipes:
            recipe = random.choice(recipes)
            return render_template('home.html', recipe=recipe)
    else:
        recipes = Recipe.query.all()  # Display all recipes on the home page by default
    return render_template('home.html', recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
