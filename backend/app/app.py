import os
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'test-index'


@app.route('/')
def landing_page():
    return render_template('pages/index.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('pages/dashboard.html')

@app.route('/progress')
def progress_page():
    return render_template('pages/progress.html')

@app.route('/login')
def login_page():
    return render_template('pages/login.html')

@app.route('/register')
def register_page():
    return render_template('pages/register.html')




if __name__ == '__main__':
    # debug=True biar kalau kamu edit HTML, browser otomatis mendeteksi perubahan
    app.run(host='0.0.0.0', port=5000, debug=True)