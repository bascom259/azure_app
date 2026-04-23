from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Chatbot is running!"

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    
    # Simple dummy response (replace with AI later)
    reply = f"You said: {user_msg}"
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)