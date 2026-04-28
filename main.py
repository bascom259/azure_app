from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# 🔑 Load API Key from environment
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 🧠 In-memory chat history (short-term memory)
chat_history = []

# 🧾 System prompt for clean formatting
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

    # Add user message to history
    chat_history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + chat_history,
            temperature=0.7,
            max_tokens=1024
        )

        bot_reply = response.choices[0].message.content

        # Save bot response
        chat_history.append({"role": "assistant", "content": bot_reply})

        return jsonify({"response": bot_reply})

    except Exception as e:
        return jsonify({"response": f"⚠️ Error: {str(e)}"})

# 🔥 Important for Azure
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
