from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os

app = Flask(__name__)

# 🔐 Read API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not set")

genai.configure(api_key=API_KEY)

# Use a stable fast model
model = genai.GenerativeModel("gemini-2.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.json.get("message")

        response = model.generate_content(
            f"You are a friendly, casual chatbot. Keep replies short and natural.\nUser: {user_msg}"
        )

        return jsonify({"reply": response.text})

    except Exception as e:
        print("ERROR:", str(e))  # shows in Azure logs
        return jsonify({"reply": "⚠️ Something went wrong. Try again."})
