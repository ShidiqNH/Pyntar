import google.generativeai as genai

# SET API KEY
genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-pro")

def ask_ai(prompt):
    response = model.generate_content(prompt)
    return response.text