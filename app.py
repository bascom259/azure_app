from flask import Flask, request, render_template
from groq import Groq
import os
from db.database import save_chat, get_memory, init_db
from datetime import datetime
import time

app = Flask(__name__)

# Initialize database
init_db()

# Load Groq API key from environment
api_key = os.getenv("GROQ_API_KEY")
print("GROQ KEY LOADED:", "YES" if api_key else "NO")

client = Groq(api_key=api_key)


# =========================
# 🔥 LLM CALL (Groq)
# =========================
def generate_reply(messages):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # ✅ your requested model
        messages=messages,
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content


# =========================
# 🤖 AGENTIC LAYER
# =========================
def agent(user_msg):
    msg = user_msg.lower()

    if "time" in msg:
        return f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}"

    if "date" in msg:
        return f"📅 Today is {datetime.now().strftime('%Y-%m-%d')}"

    if "who are you" in msg:
        return "🤖 I'm your AI assistant powered by Groq ⚡"

    return None


# =========================
# 🌐 ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    try:
        data = request.get_json()
        user_msg = data.get("message", "")

        print("USER:", user_msg)

        # -------------------------
        # 🧠 Agent check
        # -------------------------
        agent_response = agent(user_msg)
        if agent_response:
            save_chat(user_msg, agent_response)

            def generate():
                for word in agent_response.split():
                    yield word + " "
                    time.sleep(0.02)

            return app.response_class(generate(), mimetype="text/plain")

        # -------------------------
        # 💾 Memory + LLM
        # -------------------------
        messages = [{
            "role": "system",
            "content": "You are a friendly, casual chatbot. Talk like a human."
        }]

        # Add past memory
        memory = get_memory()
        print("MEMORY:", memory)

        messages += memory

        # Add current message
        messages.append({"role": "user", "content": user_msg})

        # -------------------------
        # 🤖 LLM Response
        # -------------------------
        reply = generate_reply(messages)

        print("BOT:", reply)

        # Save to DB
        save_chat(user_msg, reply)

        # -------------------------
        # ⚡ Streaming response
        # -------------------------
        def generate():
            for word in reply.split():
                yield word + " "
                time.sleep(0.02)

        return app.response_class(generate(), mimetype="text/plain")

    except Exception as e:
        print("❌ ERROR:", str(e))
        return "⚠️ Error occurred"


# =========================
# 🚀 ENTRY POINT
# =========================
if __name__ == "__main__":
    app.run(debug=True)
