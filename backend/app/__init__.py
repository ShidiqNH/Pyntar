from flask import Flask, request, jsonify
from flask_cors import CORS
from ai import ask_ai

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "PyLearn AI Backend Running"

# 🔹 AI Tutor
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    prompt = f"""
    Kamu adalah tutor Python.
    Jelaskan dengan sederhana + contoh kode:
    {question}
    """

    result = ask_ai(prompt)
    return jsonify({"response": result})


# 🔹 Code Analyzer
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    code = data.get("code")

    prompt = f"""
    Analisa kode Python berikut:
    - Jelaskan fungsi kode
    - Berikan saran perbaikan
    - Deteksi error jika ada

    Code:
    {code}
    """

    result = ask_ai(prompt)
    return jsonify({"result": result})


# 🔹 Quiz Generator
@app.route("/quiz", methods=["POST"])
def quiz():
    data = request.json
    topic = data.get("topic")

    prompt = f"""
    Buat 3 soal Python tentang {topic}.
    Sertakan jawaban.
    """

    result = ask_ai(prompt)
    return jsonify({"quiz": result})


if __name__ == "__main__":
    app.run(debug=True)