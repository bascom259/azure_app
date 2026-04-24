from flask import Flask, request, render_template, Response
import os
from datetime import datetime
import time
from google import genai

from db.database import save_chat, get_memory, init_db

app = Flask(__name__)

init_db()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# =========================
# AGENT
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
# GEMINI
# =========================
def generate_reply(messages):
    prompt = ""
    for m in messages:
        prompt += f"{m['role']}: {m['content']}\n"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    try:
        user_msg = request.json.get("message")

        # Agent
        agent_response = agent(user_msg)
        if agent_response:
            save_chat(user_msg, agent_response)

            def generate():
                for word in agent_response.split():
                    yield word + " "
                    time.sleep(0.03)

            return Response(generate(), mimetype='text/plain')

        # Memory + LLM
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        messages += get_memory()
        messages.append({"role": "user", "content": user_msg})

        reply = generate_reply(messages)

        save_chat(user_msg, reply)

        def generate():
            for word in reply.split():
                yield word + " "
                time.sleep(0.03)

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        print("ERROR:", str(e))
        return "⚠️ Error occurred"
