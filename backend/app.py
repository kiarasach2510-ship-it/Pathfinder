from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from groq import Groq

# Reads the GROQ_API_KEY value out of your .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # lets your frontend (a separate file/port) call this server

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Keeps every message of the conversation so the AI remembers context.
# "system" is an instruction the AI follows but the student never sees.
chat_history = [
    {"role": "system", "content": (
        "You are Pathfinder, a warm and encouraging career guidance assistant for students "
        "who feel lost or unsure about their future. Many students talking to you feel anxious "
        "or pressured about picking the 'right' path, so your job is to make them feel calm, "
        "supported, and capable - never judged or rushed.\n\n"
        "Guidelines for how you talk:\n"
        "- Be warm, friendly, and encouraging, like a supportive mentor, not a corporate advisor.\n"
        "- Validate feelings first before giving advice (e.g. acknowledge that it's normal and "
        "okay to feel unsure).\n"
        "- Keep responses short - 1 to 2 short sentences per reply, never a long paragraph. "
        "If you have more to say, save it for your next reply instead of cramming it all in at once.\n"
        "- Ask one simple follow-up question at a time to keep the conversation going, instead "
        "of asking many questions in a row.\n"
        "- Avoid sounding robotic, generic, or like a search engine. Sound like a real person who "
        "genuinely cares.\n"
        "- Never make the student feel behind, wrong, or like they should already know the answer."
    )}
]

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    chat_history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_history,
    )

    ai_reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": ai_reply})

    return jsonify({"reply": ai_reply})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
