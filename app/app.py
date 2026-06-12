import os
import json
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import pooling

# 1. Memuat File .env (Pastikan dipanggil paling atas)
from dotenv import load_dotenv
load_dotenv()

# Import fungsi ask_ai dan verify_code dari modul ai_engine
from ai_engine import ask_ai, verify_code

app = Flask(__name__)
CORS(app)

# Ambil SECRET_KEY dari .env, berikan fallback jika tidak ditemukan
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'test-index-secret-key-12345')

# ---------------------------------------------------------------------------
# Konfigurasi & Pooling Koneksi MySQL
# ---------------------------------------------------------------------------
db_config = {
    "host": os.environ.get("DB_HOST", os.environ.get("DATABASE_HOST", "localhost")),
    "user": os.environ.get("DB_USER", os.environ.get("DATABASE_USER", "root")),
    "password": os.environ.get("DB_PASSWORD", os.environ.get("DATABASE_PASSWORD", "")),
    "database": os.environ.get("DB_NAME", os.environ.get("DATABASE_NAME", "pyntardb")),
    "port": int(os.environ.get("DB_PORT", os.environ.get("DATABASE_PORT", 3306))),
    "connection_timeout": 5  
}

# Definisikan variabel pool secara global
db_pool = None

def init_database():
    """Menginisialisasi connection pool dan merakit struktur tabel DDL secara aman."""
    global db_pool
    try:
        print(f"[Database Init] Mencoba menghubungkan ke MySQL: host={db_config.get('host')}, user={db_config.get('user')}, database={db_config.get('database')}, port={db_config.get('port')}")
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="pyntar_pool",
            pool_size=5,
            pool_reset_session=True,
            **db_config
        )
        
        # Lakukan pembuatan tabel otomatis saat pool pertama kali terbentuk
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        
        # 1. Membuat Tabel Utama: users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `users` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `username` VARCHAR(50) NOT NULL UNIQUE,
            `email` VARCHAR(100) NOT NULL UNIQUE,
            `password` VARCHAR(255) NOT NULL,
            `completed_modules` TEXT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # 2. Membuat Tabel Relasi: user_quizzes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `user_quizzes` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `module_id` INT NOT NULL,
            `title` VARCHAR(150) NOT NULL,
            `read_time` VARCHAR(20) DEFAULT '5 min',
            `difficulty` VARCHAR(50) NULL,
            `text` TEXT NOT NULL,
            `instructions` TEXT NOT NULL,
            `tip` TEXT NULL,
            `badge` VARCHAR(50) NULL,
            `starter_code` TEXT NOT NULL,
            `expected_output` TEXT NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY `user_module_unique` (`user_id`, `module_id`),
            CONSTRAINT `fk_quiz_user` FOREIGN KEY (`user_id`) 
                REFERENCES `users` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("[Database Init] Struktur tabel 'users' & 'user_quizzes' siap digunakan.")
    except mysql.connector.Error as err:
        print(f"[Database Init Error] Gagal membuat Connection Pool / DDL Migration: {err}")
        import traceback
        traceback.print_exc()
        db_pool = None

@app.before_request
def setup_on_first_request():
    """Menjalankan inisialisasi database hanya saat ada request pertama kali masuk."""
    global db_pool
    if db_pool is None:
        init_database()

# Path data materi modul static
json_path = os.path.join(os.path.dirname(__file__), 'modules_content.json')
with open(json_path, 'r', encoding='utf-8') as f:
    MODULES_CONTENT = json.load(f)

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

def get_user_completed_modules():
    """Mengambil list ID modul yang selesai milik user langsung dari tabel MySQL."""
    if 'username' not in session or not db_pool:
        return []
    
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT completed_modules FROM users WHERE username = %s", (session['username'],))
        row = cursor.fetchone()
        if row and row['completed_modules']:
            return json.loads(row['completed_modules'])
    except Exception as e:
        print(f"Error fetching completed modules: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    return []

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

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/health")
def health():
    return "OK", 200

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST' and db_pool:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['user_id'] = user['id']  # Menyimpan user_id untuk relasi foreign key kuis
            return redirect(url_for('dashboard_page'))
        return render_template('pages/login.html', error='Username atau password salah!')
        
    if 'username' in session: 
        return redirect(url_for('dashboard_page'))
    return render_template('pages/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST' and db_pool:
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip()
        password = request.form.get('password', '').strip()
        if not username or not email or not password:
            return render_template('pages/register.html', error='Semua kolom input wajib diisi!')
        
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Cek ketersediaan username atau email
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            return render_template('pages/register.html', error='Username atau alamat email sudah digunakan!')
        
        # Simpan user baru ke tabel MySQL
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password, completed_modules) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, "[]")
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        return render_template('pages/login.html', success='Registrasi berhasil! Silakan masuk.')
        
    if 'username' in session: 
        return redirect(url_for('dashboard_page'))
    return render_template('pages/register.html')

@app.route('/logout')
def logout():
    session.clear()
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
# API Endpoints (Kuis Async & Progress Saving via MySQL)
# ---------------------------------------------------------------------------
@app.route('/api/module/<int:module_id>/get_quiz', methods=['GET'])
def get_or_generate_quiz(module_id):
    """Mengambil kuis dari tabel user_quizzes atau men-generate baru menggunakan Gemini."""
    if 'username' not in session or not db_pool:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    user_id = session.get('user_id')
    str_module_id = str(module_id)
    
    conn = db_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Cek apakah kuis untuk user dan modul ini sudah tersimpan di database
    cursor.execute("SELECT * FROM user_quizzes WHERE user_id = %s AND module_id = %s", (user_id, module_id))
    saved_quiz = cursor.fetchone()
    
    if saved_quiz:
        cursor.close()
        conn.close()
        # Rekonstruksi model data kuis ke format JSON standar agar frontend tidak berubah
        quiz_data = {
            "title": saved_quiz["title"],
            "read_time": saved_quiz["read_time"],
            "difficulty": saved_quiz["difficulty"],
            "text": saved_quiz["text"],
            "instructions": json.loads(saved_quiz["instructions"]),
            "tip": saved_quiz["tip"],
            "badge": saved_quiz["badge"],
            "starter_code": saved_quiz["starter_code"],
            "expected_output": saved_quiz["expected_output"]
        }
        return jsonify({'success': True, 'quiz': quiz_data})

    # Siapkan kuis default statis sebagai skenario fallback keselamatan
    fallback_quiz = MODULES_CONTENT.get(str_module_id, {}).get('quiz', {})
    
    # 2. Ekstraksi seluruh teks materi dari berkas JSON static sebagai basis konteks AI
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

    # 3. Panggil Gemini API untuk generate soal kustom berbasis materi modul
    try:
        ai_response = ask_ai(module_title, materi_text)
        clean_response = ai_response.strip().replace("```json", "").replace("```", "")
        quiz_data = json.loads(clean_response)
        
        required_keys = ['title', 'instructions', 'starter_code', 'expected_output']
        if not all(k in quiz_data for k in required_keys):
            raise ValueError("Struktur JSON respon AI kurang lengkap")
            
    except Exception as e:
        print(f"[Fallback MySQL Active] Modul {module_id} memicu kuis bawaan. Alasan: {str(e)}")
        quiz_data = fallback_quiz

    # 4. Amankan kuis baru (Hasil AI / Fallback) ke dalam tabel user_quizzes di MySQL
    try:
        cursor.execute(
            """INSERT INTO user_quizzes 
            (user_id, module_id, title, read_time, difficulty, text, instructions, tip, badge, starter_code, expected_output) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                user_id, module_id,
                quiz_data.get('title', 'Latihan Kode'),
                quiz_data.get('read_time', '5 min'),
                quiz_data.get('difficulty', 'Beginner'),
                quiz_data.get('text', ''),
                json.dumps(quiz_data.get('instructions', [])),
                quiz_data.get('tip', ''),
                quiz_data.get('badge', ''),
                quiz_data.get('starter_code', ''),
                quiz_data.get('expected_output', '')
            )
        )
        conn.commit()
    except Exception as db_err:
        print(f"Gagal menyimpan kuis baru ke MySQL: {db_err}")
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': True, 'quiz': quiz_data})


@app.route('/api/module/<int:module_id>/verify', methods=['POST'])
def verify_user_code(module_id):
    """Endpoint API untuk mengevaluasi baris kode user menggunakan Gemini API Sandbox."""
    if 'username' not in session or not db_pool:
        print(f"[API Verify Error] Request ditolak karena session/db_pool tidak siap. session_has_username={'username' in session}, db_pool_is_none={db_pool is None}")
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    user_code = data.get('code', '')
    quiz_title = data.get('quiz_title', 'Latihan Kode')
    user_id = session.get('user_id')

    conn = db_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil metadata pembanding kuis asli langsung dari baris data MySQL
    cursor.execute("SELECT starter_code, expected_output FROM user_quizzes WHERE user_id = %s AND module_id = %s", (user_id, module_id))
    saved_quiz = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not saved_quiz:
        print(f"[API Verify Error] Data referensi kuis tidak ditemukan di MySQL untuk user_id={user_id}, module_id={module_id}")
        return jsonify({'success': False, 'error': 'Data referensi kuis tidak ditemukan.'}), 404
        
    starter_code = saved_quiz['starter_code']
    expected_output = saved_quiz['expected_output']
    module_title = MODULES[module_id]['title']

    try:
        print(f"[API Verify] Mengevaluasi kode user untuk module_id={module_id}: {quiz_title}")
        # Kirim kode langsung ke Gemini untuk dievaluasi output beserta hint-nya secara cloud sandbox
        ai_response_raw = verify_code(module_title, quiz_title, starter_code, expected_output, user_code)
        evaluation_data = json.loads(ai_response_raw)
        
        return jsonify({
            'success': True,
            'output': evaluation_data.get('output', ''),
            'is_correct': evaluation_data.get('is_correct', False),
            'hint': evaluation_data.get('hint', '')
        })
    except Exception as e:
        print(f"[API Verify MySQL Error] Gagal memproses evaluasi kode oleh AI: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Gagal memproses evaluasi kode oleh AI.'}), 500


@app.route('/api/module/<int:module_id>/complete', methods=['POST'])
def complete_module(module_id):
    """Mencatat modul yang berhasil diselesaikan ke database MySQL dan menambah progress user."""
    if 'username' not in session or not db_pool: 
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    user_id = session.get('user_id')
    completed = get_user_completed_modules()
    
    # Cek prasyarat urutan modul
    for i in range(module_id):
        if i not in completed: 
            return jsonify({'success': False, 'error': f'Module {i} not yet completed'}), 403

    if module_id not in completed:
        completed.append(module_id)
        
        # Perbarui kolom completed_modules dalam bentuk string JSON terkompresi
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET completed_modules = %s WHERE id = %s", (json.dumps(completed), user_id))
            conn.commit()
        except Exception as e:
            print(f"Error updating completed modules to database: {e}")
            return jsonify({'success': False, 'error': 'Database error'}), 500
        finally:
            cursor.close()
            conn.close()

    return jsonify({'success': True, 'completed_modules': completed, 'xp': len(completed) * 100})


if __name__ == '__main__':
    # Membaca port dinamis dari OS, default ke 5000 jika tidak diatur
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)