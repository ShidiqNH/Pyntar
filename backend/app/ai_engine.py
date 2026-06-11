import os
import google.generativeai as genai

# 1. Konfigurasi API Key dari file .env
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_active_model():
    """
    Fungsi helper untuk mendeteksi secara dinamis model Gemini yang aktif 
    dan diizinkan oleh API Key user, mengutamakan seri 'flash' terbaru.
    """
    chosen_model = "gemini-2.5-flash"  # Default fallback terpopuler saat ini
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower():
                    chosen_model = m.name
                    break
    except Exception as e:
        print(f"[AI Engine Warning] Gagal list_models secara otomatis: {str(e)}")
    
    return chosen_model


def ask_ai(module_title, materi_text):
    """
    Menyusun prompt kuis berdasarkan materi modul dan meminta 
    respons JSON murni terstruktur dari Gemini API.
    """
    chosen_model = get_active_model()
    print(f"[AI Engine] Men-generate soal menggunakan model: {chosen_model}")

    # Rangkaian prompt utama untuk mengatur perilaku Gemini saat membuat kuis
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

    try:
        model = genai.GenerativeModel(chosen_model)
        
        generation_config = {
            "response_mime_type": "application/json",
            "temperature": 0.7, 
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        print(f"[AI Engine Error] Gagal memanggil Gemini API ({chosen_model}) untuk ask_ai: {str(e)}")
        raise e


def verify_code(module_title, quiz_title, starter_code, expected_output, user_code):
    """
    Mengirimkan kode user ke Gemini untuk dievaluasi langsung di sisi AI,
    sekaligus meminta hint edukatif jika hasil eksekusi masih salah.
    """
    chosen_model = get_active_model()
    print(f"[AI Engine] Mengevaluasi kode user menggunakan model: {chosen_model}")

    prompt = f"""
    Kamu adalah Python Code Execution Engine sekaligus Asisten Pengajar untuk platform 'Pyntar'.
    Tugasmu adalah menganalisis, mengeksekusi secara simulasi, dan mengevaluasi kode Python yang ditulis oleh siswa secara akurat.

    --- KONTEKS KUIS ---
    Modul: {module_title}
    Judul Latihan: {quiz_title}
    Starter Code Awal: 
    {starter_code}
    
    Output yang Diharapkan (Expected): "{expected_output}"

    --- KODE YANG DITULIS SISWA ---
    {user_code}
    -------------------------------

    Tugas Evaluasi:
    1. Simulasikan jalannya kode siswa dengan teliti. Tentukan apa isi output terminal (stdout) yang dihasilkan. Jika ada error logika/sintaksis/indentasi, tulis pesan error interpreter Python-nya secara ringkas di bagian "output".
    2. Bandingkan output kode siswa dengan "Output yang Diharapkan". Jika secara substansi/eksak sama (abaikan perbedaan spasi kosong di ujung akhir baris teks), set "is_correct" menjadi true. Jika berbeda atau memicu error, set menjadi false.
    3. Jika "is_correct" bernilai false, berikan 1 atau 2 kalimat petunjuk (hint) dalam Bahasa Indonesia yang membimbing siswa secara interaktif tanpa memberikan/membocorkan jawaban kodenya secara langsung (jangan berikan kode solusi di bagian hint).
    4. Jika "is_correct" bernilai true, kosongkan bagian "hint" ("").

    Kamu WAJIB mengembalikan respons dalam format JSON murni dengan struktur persis seperti ini:
    {{
        "output": "Isi output terminal hasil eksekusi kode siswa atau catatan error singkat",
        "is_correct": true/false,
        "hint": "Kalimat petunjuk interaktif pembimbing jika salah, atau kosongkan jika benar"
    }}
    
    Ingat: Jangan berikan teks penjelasan apa pun di luar objek JSON. Jangan gunakan markdown block seperti ```json ... ```. Langsung kembalikan raw teks JSON.
    """

    try:
        model = genai.GenerativeModel(chosen_model)
        
        generation_config = {
            "response_mime_type": "application/json",
            "temperature": 0.1,  # Set rendah agar evaluasi kode presisi dan deterministik
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        print(f"[AI Verifier Error] Gagal mengevaluasi kode via Gemini ({chosen_model}): {str(e)}")
        # Mengembalikan struktur JSON error standar agar frontend tidak mengalami crash/stuck
        return '{"output": "Error: Gagal terhubung ke AI Engine untuk evaluasi.", "is_correct": false, "hint": "Silakan coba klik Run Code kembali beberapa saat lagi."}'