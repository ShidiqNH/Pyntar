import os
import google.generativeai as genai

# =========================
# CONFIG (FIXED - NO HEAVY CALL)
# =========================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY tidak ditemukan di environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# FIXED MODEL (NO list_models -> biar tidak timeout di AWS)
MODEL_NAME = "gemini-2.5-flash"


# =========================
# AI QUIZ GENERATOR
# =========================
def ask_ai(module_title, materi_text):
    model = genai.GenerativeModel(MODEL_NAME)

    prompt = f"""
    Kamu adalah AI pembuat kuis koding interaktif untuk platform 'Pyntar'.

    --- MATERI ---
    Judul: {module_title}
    Isi:
    {materi_text}

    Buat soal latihan koding Python.

    WAJIB JSON MURNI:
    {{
        "title": "judul",
        "read_time": "5 min",
        "difficulty": "easy",
        "text": "soal",
        "instructions": ["step1", "step2"],
        "tip": "tips",
        "badge": "python",
        "starter_code": "# code\\n",
        "expected_output": "output"
    }}
    """

    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.7
        }
    )

    return response.text


# =========================
# AI CODE VERIFIER
# =========================
def verify_code(module_title, quiz_title, starter_code, expected_output, user_code):
    model = genai.GenerativeModel(MODEL_NAME)

    prompt = f"""
    Kamu adalah AI evaluator kode Python.

    Modul: {module_title}
    Quiz: {quiz_title}

    Starter:
    {starter_code}

    Expected:
    {expected_output}

    User code:
    {user_code}

    Output JSON:
    {{
        "output": "hasil atau error",
        "is_correct": true,
        "hint": "hint jika salah"
    }}
    """

    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    )

    return response.text


# =========================
# AI FINAL PROJECT GENERATOR
# =========================
def generate_final_project_task():
    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = """
    Kamu adalah AI pembuat kuis koding interaktif untuk platform 'Pyntar'.
    Tugasmu adalah membuat soal Proyek Akhir (Final Project) yang menantang dan komprehensif untuk menguji pemahaman siswa setelah mempelajari 10 modul dasar Python:
    1. Variabel & Tipe Data
    2. Kondisional (If-Else)
    3. List & Array
    4. Perulangan (Loops)
    5. Fungsi & Kode Modular
    6. Manipulasi String
    7. Dictionary & Set
    8. Exception Handling
    9. File Handling
    10. Built-in Libraries (seperti math, random, datetime, json)

    Rancanglah sebuah tugas proyek kecil (misal: Sistem Manajemen Kontak, Penganalisis Teks, Simulator Kasir, Game Tebak Kata Lanjutan, atau Pengelola Catatan Keuangan) yang mengharuskan siswa menggunakan minimal 5-6 konsep di atas secara bersamaan.

    Tugas ini dikerjakan dengan menulis file python (.py) utuh secara lokal lalu diunggah.

    WAJIB JSON MURNI:
    {
        "title": "Judul Proyek Akhir (misal: Sistem Catatan Keuangan Pribadi)",
        "read_time": "30 min",
        "difficulty": "Intermediate",
        "text": "Deskripsi singkat tentang apa proyek ini, latar belakang kasus, dan tujuannya.",
        "instructions": [
            "Buat struktur data untuk menyimpan informasi menggunakan list/dictionary.",
            "Terapkan fungsi-fungsi modular untuk menambah, menghapus, atau menampilkan data.",
            "Gunakan exception handling (try-except) saat menangani input dari user agar program tidak crash.",
            "Gunakan file handling (open/write/read) untuk menyimpan dan memuat data secara otomatis ke file .txt atau .json.",
            "Gunakan built-in library (seperti datetime untuk tanggal atau json untuk format penyimpanan) jika relevan."
        ],
        "tip": "Mulailah dengan membuat alur menu utama menggunakan loop while True dan input pilihan user.",
        "badge": "Final Project",
        "starter_code": "# Tulis Proyek Akhir Anda di sini dan simpan sebagai file .py untuk diunggah\n",
        "expected_output": "Menghasilkan file Python fungsional yang berjalan dengan baik."
    }
    """
    
    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.8
        }
    )
    return response.text


# =========================
# AI FINAL PROJECT EVALUATOR
# =========================
def evaluate_final_project(project_title, project_instructions, file_content):
    model = genai.GenerativeModel(MODEL_NAME)
    
    prompt = f"""
    Kamu adalah Asesor Senior dan Code Reviewer Python untuk platform 'Pyntar'.
    Tugasmu adalah menilai file proyek akhir (final_project.py) yang dikirimkan oleh user.
    
    --- PROYEK AKHIR ---
    Judul Tugas: {project_title}
    Instruksi Tugas:
    {project_instructions}
    
    --- KODE USER (final_project.py) ---
    {file_content}
    
    Lakukan review kode tersebut secara kritis. Periksa apakah kode tersebut memenuhi seluruh instruksi tugas, bebas dari syntax error, menggunakan struktur logika yang efisien (seperti perulangan, kondisi, fungsi, penanganan error jika relevan), dan memiliki gaya penulisan kode yang baik (PEP 8).
    
    WAJIB JSON MURNI:
    {{
        "is_correct": true atau false,
        "score": nilai dari 0 sampai 100,
        "feedback": "Tulis ulasan/umpan balik detail yang edukatif, sebutkan kelebihan kode, serta kekurangan atau bagian yang perlu diperbaiki (jika ada)."
    }}
    """
    
    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    )
    
    return response.text