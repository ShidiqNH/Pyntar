import os
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'test-index'


@app.route('/')
def landing_page():
    return render_template('pages/index.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('pages/dashboard.html', modules=MODULES)

@app.route('/progress')
def progress_page():
    return render_template('pages/progress.html', modules=MODULES)

@app.route('/login')
def login_page():
    return render_template('pages/login.html')

@app.route('/register')
def register_page():
    return render_template('pages/register.html')


MODULES = [
    {"id": 0, "title": "Introduction to Python", "desc": "Introduction to syntax and printing."},
    {"id": 1, "title": "Variables & Data Types", "desc": "Storing data and basic operations."},
    {"id": 2, "title": "Conditionals (If-Else)", "desc": "If statements and decision making."},
    {"id": 3, "title": "Lists & Arrays", "desc": "Working with ordered lists and arrays."},
    {"id": 4, "title": "Loops (For/While)", "desc": "For loops, while loops, and iterators."},
    {"id": 5, "title": "Functions & Modular Code", "desc": "Creating reusable functions and code modules."},
    {"id": 6, "title": "String Manipulation", "desc": "Slicing, formatting, and processing text strings."},
    {"id": 7, "title": "Dictionaries & Sets", "desc": "Storing data in key-value pairs and unique sets."},
    {"id": 8, "title": "Exception Handling", "desc": "Catching errors and writing safe, robust scripts."},
    {"id": 9, "title": "File Handling (Tambahan)", "desc": "Reading, writing, and managing external text files."},
    {"id": 10, "title": "Built-in Libraries (Tambahan)", "desc": "Importing math, random, and other standard libraries."},
    {"id": 11, "title": "Final Project", "desc": "Combine everything you learned into a complete project."}
]

@app.route('/course/module/<int:module_id>')
def module_page(module_id):
    if 0 <= module_id < len(MODULES):
        module = MODULES[module_id]
        return render_template('pages/module.html', active_module=module_id, module=module)
    return redirect(url_for('dashboard_page'))




if __name__ == '__main__':
    # debug=True biar kalau kamu edit HTML, browser otomatis mendeteksi perubahan
    app.run(host='0.0.0.0', port=5000, debug=True)