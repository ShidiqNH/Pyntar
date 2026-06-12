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