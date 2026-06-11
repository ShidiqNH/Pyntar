import os, json
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'test-index'

# Load modules content data
json_path = os.path.join(os.path.dirname(__file__), 'modules_content.json')
with open(json_path, 'r', encoding='utf-8') as f:
    MODULES_CONTENT = json.load(f)



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
    {
        "id": 0,
        "title": "Introduction to Python",
        "desc": "Langkah awal memahami sintaksis Python. Berkenalan dengan lingkungan ekosistem koding tanpa setup yang rumit."
    },
    {
        "id": 1,
        "title": "Variables & Data Types",
        "desc": "Fondasi dasar penyimpanan data di memori serta manipulasi nilai objek pertama kamu."
    },
    {
        "id": 2,
        "title": "Conditionals (If-Else)",
        "desc": "Mengatur alur pengambilan keputusan program berdasarkan logika dan kondisi tertentu."
    },
    {
        "id": 3,
        "title": "Lists & Arrays",
        "desc": "Manajemen kumpulan data linear secara terstruktur untuk persiapan pengolahan data massal."
    },
    {
        "id": 4,
        "title": "Loops (For/While)",
        "desc": "Otomatisasi tugas berulang dan pemrosesan baris data secara cepat dan efisien."
    },
    {
        "id": 5,
        "title": "Functions & Modular Code",
        "desc": "Menerapkan modularitas dan efisiensi penulisan kode agar bisa digunakan kembali (reusable code)."
    },
    {
        "id": 6,
        "title": "String Manipulation",
        "desc": "Teknik pembersihan dan pengolahan data teks dasar sebelum dianalisis oleh sistem."
    },
    {
        "id": 7,
        "title": "Dictionaries & Sets",
        "desc": "Penyimpanan struktur data kompleks yang efisien untuk pemodelan data objek modern."
    },
    {
        "id": 8,
        "title": "Exception Handling",
        "desc": "Membangun aplikasi yang tangguh (robust) terhadap kesalahan input dan gangguan sistem."
    },
    {
        "id": 9,
        "title": "File Handling (Tambahan)",
        "desc": "Kemampuan interaksi program secara langsung dengan media penyimpanan file lokal."
    },
    {
        "id": 10,
        "title": "Built-in Libraries (Tambahan)",
        "desc": "Mempercepat pengembangan program dengan memanfaatkan modul siap pakai yang efisien."
    },
    {
        "id": 11,
        "title": "Final Project",
        "desc": "Uji kompetensi akhir koding kamu dengan membangun sistem mini-analisis data interaktif."
    }
]

@app.route('/course/module/<int:module_id>')
def module_page(module_id):
    if 0 <= module_id < len(MODULES):
        module = MODULES[module_id]
        # Read JSON file dynamically on each request to support hot reloading of content
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
        except Exception:
            content_data = {}
        content = content_data.get(str(module_id), {})
        return render_template('pages/module.html', active_module=module_id, module=module, content=content)
    return redirect(url_for('dashboard_page'))


@app.route('/course/module/<int:module_id>/quiz')
def quiz_page(module_id):
    if 0 <= module_id < len(MODULES):
        module = MODULES[module_id]
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
        except Exception:
            content_data = {}
        content = content_data.get(str(module_id), {})
        quiz = content.get('quiz', {})
        return render_template('pages/quiz.html', active_module=module_id, module=module, content=content, quiz=quiz, is_quiz=True)
    return redirect(url_for('dashboard_page'))




if __name__ == '__main__':
    # debug=True biar kalau kamu edit HTML, browser otomatis mendeteksi perubahan
    app.run(host='0.0.0.0', port=5000, debug=True)