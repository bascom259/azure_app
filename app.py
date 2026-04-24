from flask import Flask, request, render_template
import google.generativeai as genai
import os
from db.database import save_chat, get_memory, init_db
from datetime import datetime
import time

app = Flask(__name__)

# Init DB
init_db()

# =========================
# 🔑 GEMINI SETUP
# =========================
api_key = os.getenv("GEMINI_API_KEY")
print("GEMINI KEY LOADED:", "YES" if api_key else "NO")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")  
# 👉 Change to "gemini-2.5-flash" if available in your account


# =========================
# 🔥 LLM CALL
# =========================
def generate_reply(messages):
    try:
        # Convert chat history → plain text (Gemini expects prompt style)
        prompt = ""
        for m in messages:
            if m["role"] == "user":
                prompt += f"User: {m['content']}\n"
            elif m["role"] == "assistant":
                prompt += f"Assistant: {m['content']}\n"

        prompt += "Assistant:"

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        print("GEMINI ERROR:", str(e))
        raise e


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
        return "🤖 I'm your AI assistant powered by Gemini ⚡"

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
        # 🧠 Agent
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
            "content": "You are a friendly, casual chatbot."
        }]

        memory = get_memory()
        print("MEMORY:", memory)

        messages += memory
        messages.append({"role": "user", "content": user_msg})

        # -------------------------
        # 🤖 Gemini Response
        # -------------------------
        reply = generate_reply(messages)

        print("BOT:", reply)

        save_chat(user_msg, reply)

        # -------------------------
        # ⚡ Streaming
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
# 🚀 ENTRY
# =========================
if __name__ == "__main__":
    app.run(debug=True)
