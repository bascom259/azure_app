from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os

app = Flask(__name__)

# 🔑 Set your API key
genai.configure(api_key="AIzaSyCgCv_MCnL0tljYzqFCT7RNOLEQaay9gvM")

model = genai.GenerativeModel("gemini-2.5-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    response = model.generate_content(
        f"You are a friendly, casual chatbot. Reply naturally.\nUser: {user_msg}"
    )

    return jsonify({"reply": response.text})
