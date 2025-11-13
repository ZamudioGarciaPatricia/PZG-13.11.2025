from flask import Flask, render_template, request, redirect, url_for, flash, json
import requests
app = Flask(__name__)

USDA_API_KEY = "2mVbF6kxK7xneQO7arHpkEhocL3fieky45ymC89t" 
USDA_API_BASE_URL = "https://api.nal.usda.gov/fdc/v1/food/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def busca_comida():
    comida_name = request.form.get('comida_name', '')

if __name__ == '__main__':
    app.run(debug=True)