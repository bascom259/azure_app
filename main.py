from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# 🔑 Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# 🧠 Chat history
chat_history = []

# 🧾 System prompt for formatting
SYSTEM_PROMPT = """
You are a helpful AI assistant.

Format responses using proper Markdown:
- Use headings (##, ###)
- Use bullet points
- Use spacing between paragraphs
- Keep answers clean and readable
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    # Add user input
    chat_history.append({"role": "user", "parts": [user_input]})

    try:
        # Convert history into Gemini format
        gemini_messages = [{"role": "user", "parts": [SYSTEM_PROMPT]}] + chat_history

        response = model.generate_content(gemini_messages)

        bot_reply = response.text

        # Save response
        chat_history.append({"role": "model", "parts": [bot_reply]})

        return jsonify({"response": bot_reply})

    except Exception as e:
        return jsonify({"response": f"⚠️ Error: {str(e)}"})

# 🔥 Azure entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
