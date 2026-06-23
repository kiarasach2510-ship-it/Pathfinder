#This is the starter code to import the API

#This imports the tools
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os

#This loads the environment variables
load_dotenv()

#This creates the actual server and name it app
app = Flask(__name__)
CORS(app)

#This logs into Groq using the API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/career-advice", methods=["POST"])
def career_advice():
    data = request.json
    messages = data.get("messages", [])

    #This generates the AI response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages = messages 
    )
    try:
        advice = response.choices[0].message.content
    except Exception:
        advice = str(response)
    messages.append({"role": "assistant", "content": advice})
    return jsonify({"messages": messages})

if __name__ == "__main__":
    app.run(debug=True)

