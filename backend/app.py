#This is the starter code to import the API

#This imports the tools
from flask import Flask, request, jsonify
from flask_cors import CORS
import groq
from groq import Groq
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred)

def verify_token():
    from firebase_admin import auth
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    try:
        decoded_token = auth.verify_id_token(token)
    except Exception:
        return None
    return decoded_token


# This is the system prompt that guides the AI's behavior in the career advice application
SYSTEM_PROMPT = """- Ask one simple follow-up question at a time to keep the conversation going, instead of asking many questions in a row.
- Avoid sounding robotic, generic, or like a search engine. Sound like a real person who genuinely cares.
- Never make the student feel behind, wrong, or like they should already know the answer.
- Before asking your next question, always react first to what the student just said - reflect it back briefly, show genuine curiosity, relate to it, or comment on it like a friend would. Never jump straight from their answer into your next question with no acknowledgment - that's what makes it feel like a survey instead of a conversation.
- Vary how you transition into questions. Don't always end every message with a question mark right after a single acknowledging sentence - sometimes share a brief thought or observation that naturally leads into what you're curious about next.
- Keep replies to about 2-4 sentences. Long enough to react genuinely and not feel curt, but short enough to stay easy to read and not overwhelm the student.

How to figure out the student's interests:
- Never ask big, vague questions like 'What are your interests?' or 'What do you want to do with your life?' - these are overwhelming and hard to answer.
- Instead, ask small, specific, easy questions, one at a time, such as: do they prefer working with people or alone, indoors or outdoors, hands-on tasks or computers, creative work or structured/logical work, what subjects in school they enjoy most, or what they like doing in their free time.
- Also gently ask, one small question at a time (not as one big question), how much time they're open to spending training or studying for a career (e.g. a short certificate, a 2-year program, a 4-year degree, or more), and roughly what kind of income feels important to them long-term, if they are unsure then ask small questions to find out the kind of lifestyle they want to have in the future and then slightly say that according to their wanted lifestyle this amount of income would be okay
- When choosing which careers to suggest, factor in current technology trends and which fields are growing or in demand right now, so your suggestions are realistic and valuable for the long term, not based on stated interests alone.
- Also gently ask, one small question at a time, about the kind of workplace environment and schedule they'd want — for example, a structured 9-to-5 versus flexible hours, working remotely versus in person, and how important work-life balance is to them, if they are unsure discover by short small simple answers.
- Build up a picture of the student gradually over several small questions before suggesting any careers - don't suggest a career after just one answer.
- Once you've asked enough small questions to see a clear pattern, suggest one or two career paths that fit what they've told you, and explain briefly and simply why those fit, in plain language without jargon. Additionally, add you don't have to like these careers right away and they aren't the only options - there are many other careers that could also be a good fit, and they can explore those later.

What to do when you are done discovering interests:
- When you are suggesting a career path, explain briefly and simply why that career fits what they've told you, in plain language without jargon. Additionally, add you don't have to like this career right away and it isn't the only option - there are many other careers that could also be a good fit, and they can explore those later.
- Only suggest 3 career paths at a time, but if you meet a situation where 3 is too many, you can suggest 1 or 2 instead. If you suggest fewer than 3, explain why you are suggesting fewer and that there are many other careers that could also be a good fit, and they can explore those later.
- Once you've suggested a career path, ask if they want to learn more about it. If they say yes, provide a brief overview of the career, including what the work is like, what skills are needed, and what the job outlook is. If they say no, ask if they want to explore other career options instead, and if so, go back to asking small questions to discover more about their interests.
- If they want to explore other career options, repeat the process of asking small questions to discover their interests, and then suggest one or two more career paths that fit what they've told you, explaining briefly and simply why those fit, in plain language without jargon. Again, add that they don't have to like these careers right away and they aren't the only options - there are many other careers that could also be a good fit, and they can explore those later.
- If at any point the student seems unsure or confused, ask clarifying questions to help them articulate their thoughts and feelings. Avoid making assumptions about their interests or abilities, and instead focus on listening and understanding their perspective.
- If the student expresses interest in a career path that doesn't seem to fit their interests or abilities, gently explain why it may not be the best fit and suggest alternative options that align better with their interests and strengths. Emphasize that there are many paths to success and fulfillment, and that it's important to find a career that aligns with their unique skills and passions and goals.

Always respond using this exact JSON structures:
- Shape 1 -still asking discovery questions:
type: "question"
content: (the actual question text, e.g., "Do you prefer working with people or alone?")
- Shape 2 -ready to suggest careers:
type: "suggestion"
careers: a list of one or more career forms, where each one has:
  - title
  - description
  - why_it_matches_you
  - environment
  - salary_range
  - try_it_out: a specific, concrete, actionable way to actually try out or explore this career right now - e.g. a particular free online course, a specific project to build, a club/competition to join, a tool to experiment with, or someone to shadow for a day. Never a vague encouragement like "explore this further" or "this might be right for you" - always name an actual concrete action. """


#This loads the environment variables
load_dotenv()

#This creates the actual server and name it app
app = Flask(__name__)
CORS(app)
#Integrate SQLAlchemy for database management
from flask_sqlalchemy import SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pathfinder.db"
db = SQLAlchemy(app)

#This defines the SavedCareer model for storing saved career suggestions in the database
class SavedCareer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    why_it_matches_you = db.Column(db.String)
    environment = db.Column(db.String)
    salary_range = db.Column(db.String)
    try_it_out = db.Column(db.String)



#This logs into Groq using the API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.route("/career-advice", methods=["POST"])
def career_advice():
    #This checks for a Firebase token, but doesn't require one (first 10 messages are free for guests)
    decoded_token = verify_token()
    data = request.json
    messages = data.get("messages", [])

    #This generates the AI response
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages = full_messages,
            response_format = {"type": "json_object"}
        )
    except groq.APIError:
        return jsonify({"error": "The AI is temporarily busy, please try again shortly."}), 503

    try:
        advice = response.choices[0].message.content
    except Exception:
        advice = str(response)
    
    try:
        parsed_advice = json.loads(advice)
        if "type" not in parsed_advice or ("content" not in parsed_advice and "careers" not in parsed_advice):
            raise ValueError("AI response is missing required fields")
    except (json.JSONDecodeError, ValueError):
        return jsonify({"error": "The AI's response got garbled, please try sending that again."}), 502

    ready_to_suggest = parsed_advice.get("type") == "suggestion"
    latest_reply = parsed_advice

    messages.append({"role": "assistant", "content": advice})
    return jsonify({"messages": messages, "ready_to_suggest": ready_to_suggest, "latest_reply": latest_reply})


#This is the star button's backend for saving career suggestions
@app.route("/save-career", methods=["POST"])
def save_career():
    decoded_token = verify_token()
    if decoded_token is None:
        return jsonify({"error": "Invalid or missing token"}), 401

    data = request.json
    title = data.get("title")

    # Avoid duplicate rows when the same career appears more than once in a
    # conversation (e.g. the AI re-suggests it) and gets starred from each instance
    existing = SavedCareer.query.filter_by(user_id=decoded_token["uid"], title=title).first()
    if existing:
        return jsonify({"message": "Career already saved!", "id": existing.id})

    new_career = SavedCareer(
        user_id=decoded_token["uid"],
        title=title,
        description=data.get("description"),
        why_it_matches_you=data.get("why_it_matches_you"),
        environment=data.get("environment"),
        salary_range=data.get("salary_range"),
        try_it_out=data.get("try_it_out"),
    )
    db.session.add(new_career)
    db.session.commit()
    return jsonify({"message": "Career saved!", "id": new_career.id})

#This is the star button's backend for un-saving a career (clicking an already-saved star)
@app.route("/save-career/<int:career_id>", methods=["DELETE"])
def delete_saved_career(career_id):
    decoded_token = verify_token()
    if decoded_token is None:
        return jsonify({"error": "Invalid or missing token"}), 401

    career = SavedCareer.query.filter_by(id=career_id, user_id=decoded_token["uid"]).first()
    if career is None:
        return jsonify({"error": "Saved career not found"}), 404

    db.session.delete(career)
    db.session.commit()
    return jsonify({"message": "Career removed!"})

#This lists all saved career suggestions for the logged-in user
@app.route("/saved-careers", methods=["GET"])
def get_saved_careers():
    decoded_token = verify_token()
    if decoded_token is None:
        return jsonify({"error": "Invalid or missing token"}), 401

    saved_careers = SavedCareer.query.filter_by(user_id=decoded_token["uid"]).all()

    results = []
    for career in saved_careers:
        results.append({
            "id": career.id,
            "title": career.title,
            "description": career.description,
            "why_it_matches_you": career.why_it_matches_you,
            "environment": career.environment,
            "salary_range": career.salary_range,
            "try_it_out": career.try_it_out,
        })

    return jsonify({"saved_careers": results})

#This is the backend for the career details page, which provides deeper information about a specific career
CAREER_DETAILS_PROMPT = """You are a supportive career advisor giving a student deeper detail about one specific career they're interested in.
Always respond using this exact JSON structure:
education_needed: a short explanation of the typical education path (e.g. degree type, certifications)
skills_to_gain: a list of short plain text strings, one per skill worth developing - never objects, just strings
university_programs: a list of short plain text strings, one per specific degree/program name that leads well into this career - never objects, just strings
extracurriculars: a list of short plain text strings, one per specific club, project, or activity a high schooler could pursue now to prepare for this career - never objects, just strings"""

@app.route("/career-details", methods=["POST"])
def career_details():
    decoded_token = verify_token()
    if decoded_token is None:
        return jsonify({"error": "Invalid or missing token"}), 401

    data = request.json
    title = data.get("title", "")
    description = data.get("description", "")

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": CAREER_DETAILS_PROMPT},
                {"role": "user", "content": f"The career is: {title}. Description: {description}"}
            ],
            response_format={"type": "json_object"}
        )
    except groq.APIError:
        return jsonify({"error": "The AI is temporarily busy, please try again shortly."}), 503

    try:
        details = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return jsonify({"error": "The AI's response got garbled, please try again."}), 502

    return jsonify({"details": details})

#This is for the Progress page and designing the AI analysis
PROGRESS_PROMPT = """You are a supportive, encouraging career advisor reflecting on a student's conversation so far.
Based on the full conversation history provided, respond using this exact JSON structure:
feeling: a short, warm description of their general emotional state about their future/career search (e.g. "curious and a little excited, with some uncertainty about narrowing things down")
values: a list of themes or values they've expressed (e.g. "helping people", "working creatively", "avoiding a desk job")
patterns: a list of recurring interests or ideas that kept coming up across the conversation
career_paths_explored: a list of the career titles that have been suggested or discussed so far
next_step: one gentle, concrete, low-pressure thing they could try or think about next
Be warm and encouraging throughout, never clinical or judgmental."""

@app.route("/progress", methods=["POST"])
def progress():
    decoded_token = verify_token()
    if decoded_token is None:
        return jsonify({"error": "Invalid or missing token"}), 401

    data = request.json
    messages = data.get("messages", [])

    analysis_messages = [{"role": "system", "content": PROGRESS_PROMPT}] + messages
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=analysis_messages,
            response_format={"type": "json_object"}
        )
    except groq.APIError:
        return jsonify({"error": "The AI is temporarily busy, please try again shortly."}), 503

    try:
        progress_data = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return jsonify({"error": "The AI's response got garbled, please try again."}), 502

    return jsonify({"progress": progress_data})

if __name__ == "__main__":
    #This creates the database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)


