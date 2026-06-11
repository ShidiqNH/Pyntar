import os
import json
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# 1. Memuat File .env (Pastikan dipanggil paling atas)
from dotenv import load_dotenv
load_dotenv()

# Import fungsi ask_ai dan verify_code dari modul ai_engine yang sudah diperbarui
from ai_engine import ask_ai, verify_code

app = Flask(__name__)
CORS(app)

# Ambil SECRET_KEY dari .env, berikan fallback jika tidak ditemukan
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'test-index-secret-key-12345')

# Path data JSON
json_path = os.path.join(os.path.dirname(__file__), 'modules_content.json')
users_json_path = os.path.join(os.path.dirname(__file__), 'users.json')

# Load data materi modul static
with open(json_path, 'r', encoding='utf-8') as f:
    MODULES_CONTENT = json.load(f)

def load_users():
    if os.path.exists(users_json_path):
        try:
            with open(users_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users):
    with open(users_json_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

def get_user_completed_modules():
    if 'username' not in session:
        return []
    users = load_users()
    user = users.get(session['username'], {})
    raw = user.get('completed_modules', [])
    return [int(m) for m in raw]

# Definisi Daftar Modul Utama
MODULES = [
    {"id": 0,  "title": "Introduction to Python",     "desc": "Langkah awal memahami sintaksis Python. Berkenalan dengan lingkungan ekosistem koding tanpa setup yang rumit."},
    {"id": 1,  "title": "Variables & Data Types",      "desc": "Fondasi dasar penyimpanan data di memori serta manipulasi nilai objek pertama kamu."},
    {"id": 2,  "title": "Conditionals (If-Else)",      "desc": "Mengatur alur pengambilan keputusan program berdasarkan logika dan kondisi tertentu."},
    {"id": 3,  "title": "Lists & Arrays",              "desc": "Manajemen kumpulan data linear secara terstruktur untuk persiapan pengolahan data massal."},
    {"id": 4,  "title": "Loops (For/While)",           "desc": "Otomatisasi tugas berulang dan pemrosesan baris data secara cepat dan efisien."},
    {"id": 5,  "title": "Functions & Modular Code",    "desc": "Menerapkan modularitas dan efisiensi penulisan kode agar bisa digunakan kembali (reusable code)."},
    {"id": 6,  "title": "String Manipulation",         "desc": "Teknik pembersihan dan pengolahan data teks dasar sebelum dianalisis oleh sistem."},
    {"id": 7,  "title": "Dictionaries & Sets",         "desc": "Penyimpanan struktur data kompleks yang efisien untuk pemodelan data objek modern."},
    {"id": 8,  "title": "Exception Handling",          "desc": "Membangun aplikasi yang tangguh (robust) terhadap kesalahan input dan gangguan sistem."},
    {"id": 9,  "title": "File Handling (Tambahan)",    "desc": "Kemampuan interaksi program secara langsung dengan media penyimpanan file lokal."},
    {"id": 10, "title": "Built-in Libraries (Tambahan)", "desc": "Mempercepat pengembangan program dengan memanfaatkan modul siap pakai yang efisien."},
    {"id": 11, "title": "Final Project",               "desc": "Uji kompetensi akhir koding kamu dengan membangun sistem mini-analisis data interaktif."},
]

@app.context_processor
def inject_user_progress():
    completed = get_user_completed_modules()
    total_modules = len(MODULES)
    completed_count = len(completed)
    progress_percent = round((completed_count / total_modules) * 100) if total_modules > 0 else 0
    xp = completed_count * 100
    return dict(
        modules=MODULES,
        completed_modules=completed,
        completed_count=completed_count,
        progress_percent=progress_percent,
        xp=xp,
    )

# ---------------------------------------------------------------------------
# Public & Authentication Routes
# ---------------------------------------------------------------------------
@app.route('/')
def landing_page(): 
    return render_template('pages/index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        users = load_users()
        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard_page'))
        return render_template('pages/login.html', error='Username atau password salah!')
    if 'username' in session: 
        return redirect(url_for('dashboard_page'))
    return render_template('pages/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip()
        password = request.form.get('password', '').strip()
        if not username or not email or not password:
            return render_template('pages/register.html', error='Semua kolom input wajib diisi!')
        users = load_users()
        if username in users: 
            return render_template('pages/register.html', error='Username sudah terdaftar!')
        for existing_user in users.values():
            if existing_user.get('email') == email: 
                return render_template('pages/register.html', error='Alamat email sudah digunakan!')
        
        users[username] = {
            'email': email,
            'password': generate_password_hash(password),
            'completed_modules': [],
            'generated_quizzes': {}  # Penampung kuis berbasis user
        }
        save_users(users)
        return render_template('pages/login.html', success='Registrasi berhasil! Silakan masuk.')
    if 'username' in session: 
        return redirect(url_for('dashboard_page'))
    return render_template('pages/register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

# ---------------------------------------------------------------------------
# Dashboard & Core Course Routes
# ---------------------------------------------------------------------------
@app.route('/dashboard')
def dashboard_page():
    if 'username' not in session: 
        return redirect(url_for('login_page'))
    return render_template('pages/dashboard.html', username=session.get('username'))

@app.route('/progress')
def progress_page():
    if 'username' not in session: 
        return redirect(url_for('login_page'))
    return render_template('pages/progress.html', username=session.get('username'))

@app.route('/course/module/<int:module_id>')
def module_page(module_id):
    if 'username' not in session: 
        return redirect(url_for('login_page'))
    if not (0 <= module_id < len(MODULES)): 
        return redirect(url_for('dashboard_page'))
    
    completed = get_user_completed_modules()
    for i in range(module_id):
        if i not in completed: 
            return redirect(url_for('dashboard_page'))
    
    module = MODULES[module_id]
    content = MODULES_CONTENT.get(str(module_id), {})
    return render_template('pages/module.html', active_module=module_id, module=module, content=content)

@app.route('/course/module/<int:module_id>/quiz')
def quiz_page(module_id):
    if 'username' not in session:
        return redirect(url_for('login_page'))
    if not (0 <= module_id < len(MODULES)):
        return redirect(url_for('dashboard_page'))

    completed = get_user_completed_modules()
    for i in range(module_id):
        if i not in completed:
            return redirect(url_for('dashboard_page'))

    module = MODULES[module_id]
    content = MODULES_CONTENT.get(str(module_id), {})
    
    return render_template('pages/quiz.html', active_module=module_id, module=module, content=content, is_quiz=True)

# ---------------------------------------------------------------------------
# API Endpoints (Kuis Async & Progress Saving)
# ---------------------------------------------------------------------------
@app.route('/api/module/<int:module_id>/get_quiz', methods=['GET'])
def get_or_generate_quiz(module_id):
    """Mengambil kuis yang sudah tersimpan di database user atau men-generate baru menggunakan Gemini."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    username = session['username']
    users = load_users()
    user = users.get(username, {})
    
    # Inisialisasi map pencatatan kuis jika belum ada
    if 'generated_quizzes' not in user:
        user['generated_quizzes'] = {}

    str_module_id = str(module_id)
    
    # 1. Kuis sudah ada (Cache Hit): Kembalikan data kuis yang lama tanpa hit API ulang
    if str_module_id in user['generated_quizzes']:
        return jsonify({'success': True, 'quiz': user['generated_quizzes'][str_module_id]})

    # Ambil kuis default dari materi untuk skenario fallback jika AI bermasalah
    fallback_quiz = MODULES_CONTENT.get(str_module_id, {}).get('quiz', {})
    
    # 2. Ekstraksi seluruh teks materi dari modul ini sebagai bekal konteks untuk Gemini
    module_title = MODULES[module_id]['title']
    content_data = MODULES_CONTENT.get(str_module_id, {})
    
    materi_text = ""
    for section in content_data.get('sections', []):
        if section.get('title'):
            materi_text += f"\nBagian: {section['title']}\n"
        if section.get('text'):
            materi_text += f"{section['text']}\n"
        if section.get('bullets'):
            materi_text += "\n".join(section['bullets']) + "\n"
        if section.get('code'):
            materi_text += f"Contoh Kode:\n{section['code']}\n"

    # 3. Panggil Gemini API untuk generate soal kustom berdasarkan materi nyata
    try:
        ai_response = ask_ai(module_title, materi_text)
        
        # Sanitasi tag markdown pembungkus jika tidak sengaja dibuat oleh model AI
        clean_response = ai_response.strip().replace("```json", "").replace("```", "")
        quiz_data = json.loads(clean_response)
        
        # Validasi minimal key JSON agar compiler mockup tidak crash
        required_keys = ['title', 'instructions', 'starter_code', 'expected_output']
        if not all(k in quiz_data for k in required_keys):
            raise ValueError("Struktur JSON respon AI kurang lengkap")
            
    except Exception as e:
        # 4. Skenario FALLBACK: Jika AI error/timeout, gunakan soal dari modules_content.json
        print(f"[Fallback Active] Modul {module_id} memicu kuis bawaan. Alasan: {str(e)}")
        quiz_data = fallback_quiz

    # 5. Salin kuis ke data user dan amankan ke users.json agar tidak hilang saat di-refresh
    user['generated_quizzes'][str_module_id] = quiz_data
    users[username] = user
    save_users(users)

    return jsonify({'success': True, 'quiz': quiz_data})


@app.route('/api/module/<int:module_id>/verify', methods=['POST'])
def verify_user_code(module_id):
    """Endpoint API untuk mengevaluasi baris kode user menggunakan Gemini API Sandbox."""
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    user_code = data.get('code', '')
    quiz_title = data.get('quiz_title', 'Latihan Kode')

    username = session['username']
    users = load_users()
    user = users.get(username, {})
    
    str_module_id = str(module_id)
    saved_quiz = user.get('generated_quizzes', {}).get(str_module_id, {})
    
    # Ambil metadata pembanding kuis asli yang disimpan di user
    starter_code = saved_quiz.get('starter_code', '')
    expected_output = saved_quiz.get('expected_output', '')
    module_title = MODULES[module_id]['title']

    try:
        # Panggil Gemini sandbox eksekusi untuk memeriksa kode & menyusun output + hint
        ai_response_raw = verify_code(module_title, quiz_title, starter_code, expected_output, user_code)
        evaluation_data = json.loads(ai_response_raw)
        
        return jsonify({
            'success': True,
            'output': evaluation_data.get('output', ''),
            'is_correct': evaluation_data.get('is_correct', False),
            'hint': evaluation_data.get('hint', '')
        })
    except Exception as e:
        print(f"[API Verify Error]: {str(e)}")
        return jsonify({'success': False, 'error': 'Gagal memproses evaluasi kode.'}), 500


@app.route('/api/module/<int:module_id>/complete', methods=['POST'])
def complete_module(module_id):
    """Mencatat modul yang berhasil diselesaikan dan menambah XP user."""
    if 'username' not in session: 
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    users = load_users()
    username = session['username']
    user = users.get(username)
    if not user: 
        return jsonify({'success': False, 'error': 'User not found'}), 404

    completed = [int(m) for m in user.get('completed_modules', [])]
    
    # Cek prasyarat urutan modul
    for i in range(module_id):
        if i not in completed: 
            return jsonify({'success': False, 'error': f'Module {i} not yet completed'}), 403

    if module_id not in completed:
        completed.append(module_id)
        users[username]['completed_modules'] = completed
        save_users(users)

    return jsonify({'success': True, 'completed_modules': completed, 'xp': len(completed) * 100})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)