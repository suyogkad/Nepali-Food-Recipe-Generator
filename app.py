from flask import Flask, render_template, request
import pandas as pd
import random

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('nepalifoods.csv')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        food_type = request.form.get('food_type')
        recipes = df[df['Type'] == food_type].to_dict(orient='records')
        if recipes:
            recipe = random.choice(recipes)
            return render_template('home.html', recipe=recipe)
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)