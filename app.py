from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from db.database import save_chat, get_memory, init_db
from datetime import datetime
import time

app = Flask(__name__)

# Init DB
init_db()

# GROQ SETUP
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_reply(messages):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content


# AGENTIC LAYER
def agent(user_msg):
    msg = user_msg.lower()

    if "time" in msg:
        return f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}"

    if "date" in msg:
        return f"📅 Today is {datetime.now().strftime('%Y-%m-%d')}"

    if "who are you" in msg:
        return "🤖 I'm your AI assistant running on Groq ⚡"

    return None


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

            return app.response_class(generate(), mimetype='text/plain')

        # Memory
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        messages += get_memory()
        messages.append({"role": "user", "content": user_msg})

        reply = generate_reply(messages)

        save_chat(user_msg, reply)

        def generate():
            for word in reply.split():
                yield word + " "
                time.sleep(0.03)

        return app.response_class(generate(), mimetype='text/plain')

    except Exception as e:
        print("ERROR:", str(e))
        return "⚠️ Error occurred"
