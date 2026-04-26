from flask import Flask, request, render_template
import os
from datetime import datetime
import time
import traceback

# Gemini NEW SDK
from google import genai

from db.database import save_chat, get_memory, init_db

app = Flask(__name__)

# Init DB
init_db()

# Gemini setup
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# -------------------------
# GENERATE REPLY (FIXED)
# -------------------------
def generate_reply(messages):
    # Convert messages → plain prompt (Gemini needs string)
    prompt = "\n".join([m["content"] for m in messages])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# -------------------------
# AGENTIC LAYER
# -------------------------
def agent(user_msg):
    msg = user_msg.lower()

    if "time" in msg:
        return f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}"

    if "date" in msg:
        return f"📅 Today is {datetime.now().strftime('%Y-%m-%d')}"

    if "who are you" in msg:
        return "🤖 I'm your AI assistant running on Gemini ⚡"

    return None


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    try:
        data = request.get_json()
        user_msg = data.get("message", "").strip()

        if not user_msg:
            return "⚠️ Empty message"

        # -------------------------
        # AGENT RESPONSE
        # -------------------------
        agent_response = agent(user_msg)
        if agent_response:
            save_chat(user_msg, agent_response)

            def generate():
                for word in agent_response.split():
                    yield word + " "
                    time.sleep(0.02)

            return app.response_class(generate(), mimetype='text/plain')

        # -------------------------
        # MEMORY + MODEL
        # -------------------------
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        messages += get_memory()
        messages.append({"role": "user", "content": user_msg})

        reply = generate_reply(messages)

        save_chat(user_msg, reply)

        def generate():
            for word in reply.split():
                yield word + " "
                time.sleep(0.02)

        return app.response_class(generate(), mimetype='text/plain')

    except Exception as e:
        # 🔥 FULL DEBUG OUTPUT
        print("ERROR:", str(e))
        print(traceback.format_exc())

        return f"⚠️ {str(e)}"
