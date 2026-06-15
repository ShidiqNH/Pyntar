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
    Kamu adalah AI pembuat kuis koding interaktif untuk platform pembelajaran Python bernama 'Pyntar'.
    Tugasmu adalah membuat sebuah soal latihan koding (praktik menulis kode) yang spesifik berdasarkan materi modul yang diberikan di bawah ini.

    --- MATERI MODUL YANG SEDANG DIPELAJARI USER ---
    Judul Modul: {module_title}
    Konten Materi:
    {materi_text}
    ------------------------------------------------

    Wajib ikuti aturan pembuatan kuis ini:
    1. Buatlah kuis yang meminta user untuk melengkapi atau menulis kode Python sederhana yang langsung berkaitan dengan materi di atas.
    2. Soal harus bisa dievaluasi secara eksak lewat output cetak terminal (fungsi print()).
    3. `expected_output` harus berupa string keluaran yang statis, ringkas, dan jelas hasil dari eksekusi `starter_code` jika diselesaikan dengan benar.
    4. Hindari membuat soal yang membutuhkan input interaktif (seperti fungsi input()) karena sistem terminal kami menggunakan interpreter mockup statis.
    5. Berikan instruksi langkah-demi-langkah yang ramah bagi pemula.

    Kamu WAJIB mengembalikan respons dalam format JSON murni dengan struktur persis seperti di bawah ini:
    {{
        "title": "Judul kuis kustom yang menarik dan relevan",
        "read_time": "5 min",
        "difficulty": "Sesuai tingkat kesulitan materi",
        "text": "Deskripsi masalah atau perintah koding yang harus diselesaikan user.",
        "instructions": [
            "Langkah 1: Perhatikan kode di sebelah kanan...",
            "Langkah 2: Selesaikan bagian...",
            "Langkah 3: Jalankan kode untuk melihat hasilnya."
        ],
        "tip": "Tips opsional, misalnya: 'Ingat untuk memperhatikan indentasi/titik dua'.",
        "badge": "kata_kunci_fitur",
        "starter_code": "# Tulis kode awal atau komentar petunjuk di sini\\n",
        "expected_output": "Hasil output print yang diharapkan"
    }}
    
    Ingat: Jangan berikan teks penjelasan apa pun di luar objek JSON. Jangan gunakan markdown block seperti ```json ... ```. Langsung kembalikan raw teks JSON.
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
    Kamu adalah Python Code Checker sekaligus Asisten Pengajar untuk platform 'Pyntar'.
    Tugasmu adalah menganalisis, mensimulasikan eksekusi, dan mengevaluasi kode Python yang ditulis oleh siswa secara kritis.

    --- KONTEKS KUIS ---
    Modul: {module_title}
    Judul Latihan: {quiz_title}
    Starter Code Awal: 
    {starter_code}
    
    Output Akhir yang Diharapkan (Expected): "{expected_output}"

    --- KODE YANG SEBENARNYA DITULIS SISWA ---
    {user_code}
    -------------------------------

    TUGAS EVALUASI MUTLAK:
    1. Simulasikan eksekusi kode siswa. Tulis apa isi output terminal (stdout) asli yang dihasilkan di kolom "output". Jika kodenya error, tulis pesan error interpreter Python di kolom "output" secara ringkas.
    2. Periksa STRUKTUR LOGIKA kodenya secara kritis, bukan hanya output teks akhirnya saja!
       - JIKA instruksi meminta membuat variabel atau logika tertentu (kondisional/perulangan), periksa apakah siswa benar-benar mendeklarasikannya di dalam baris kode mereka.
       - JIKA siswa melakukan "kecurangan logis" dengan langsung melakukan hardcode teks output lewat fungsi print() tanpa mengikuti aturan logika/variabel yang diminta, maka siswa tersebut DIANGGAP SALAH.
    3. Tentukan status kelulusan ("is_correct"):
       - Set "is_correct" menjadi true HANYA JIKA output terminalnya sama eksak DAN struktur kodenya patuh terhadap instruksi logika kuis.
       - Set "is_correct" menjadi false JIKA output salah, memicu syntax error, ATAU output benar tapi dicurangi dengan teknik hardcode langsung.
    4. Jika "is_correct" bernilai false, berikan 1 atau 2 kalimat petunjuk (hint) dalam Bahasa Indonesia. Tegur siswa secara halus jika mereka melakukan hardcode langsung (contoh: "Output kamu sudah sesuai, tetapi kamu belum membuat variabel yang diminta. Yuk ikuti instruksinya!"). JANGAN memberikan atau membocorkan kode solusi di dalam hint.
    5. Jika "is_correct" bernilai true, kosongkan bagian "hint" ("").

    Kamu WAJIB mengembalikan respons dalam format JSON murni dengan struktur persis seperti ini:
    {{
        "output": "Isi cetakan terminal atau ringkasan error koding siswa",
        "is_correct": false,
        "hint": "Kalimat bimbingan / teguran halus jika struktur salah, atau kosongkan jika benar"
    }}
    
    Ingat: Jangan berikan teks penjelasan apa pun di luar objek JSON murni. Jangan gunakan markdown block seperti ```json ... ```. Langsung kembalikan raw teks JSON.
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
        "expected_output": "Deskripsi singkat hasil/file output yang diharapkan setelah proyek dijalankan"
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