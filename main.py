from flask import Flask, render_template, request, jsonify
from groq import Groq
import os



app = Flask(__name__)

# ✅ GROQ ONLY
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_history = []

SYSTEM_PROMPT = """
Format responses using proper Markdown:
- Use headings
- Use bullet points
- Keep it clean
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    chat_history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + chat_history
        )

        reply = response.choices[0].message.content

        chat_history.append({"role": "assistant", "content": reply})

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"response": f"⚠️ {str(e)}"})
