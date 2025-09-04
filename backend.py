from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import sqlite3
import bcrypt
import pandas as pd

# Initialize FastAPI
app = FastAPI(title="WellBot Backend")

user_contexts = {}

class ChatRequest(BaseModel):
    user_id: str  # We use username or session ID to track conversation
    message: str

def wellbot_reply(user_id: str, user_message: str):
    user_message = user_message.lower()

    # Get previous context for this user
    context = user_contexts.get(user_id, {"last_topic": None})

    # Simple intent detection
    if "stress" in user_message:
        context["last_topic"] = "stress"
        reply = "I understand stress can be tough. Try deep breathing for 5 minutes. 🌬️"
    elif "sleep" in user_message:
        context["last_topic"] = "sleep"
        reply = "Good sleep hygiene is important. Avoid screens 1 hour before bed. 😴"
    elif "exercise" in user_message:
        context["last_topic"] = "exercise"
        reply = "Regular exercise can boost mood and reduce stress. 🚴"
    elif "what should i do" in user_message or "help me" in user_message:
        # Use last topic if available
        if context["last_topic"] == "stress":
            reply = "Since you mentioned stress earlier, you can also try journaling or a quick walk."
        elif context["last_topic"] == "sleep":
            reply = "Try a consistent bedtime routine and keep your room cool and dark."
        elif context["last_topic"] == "exercise":
            reply = "Start with 20 minutes of walking daily and build from there!"
        else:
            reply = "Could you tell me what’s bothering you — stress, sleep, or something else?"
    elif "hello" in user_message or "hi" in user_message:
        reply = "Hello! How are you feeling today? 😊"
    else:
        reply = "I'm here to help you with wellness tips. Can you tell me more?"

    # Save updated context back
    user_contexts[user_id] = context
    return reply

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    reply = wellbot_reply(request.user_id, request.message)
    return {"response": reply}

# --- Enable CORS so frontend can call backend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT UNIQUE,
    password BLOB
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles(
    username TEXT,
    name TEXT,
    age_group TEXT,
    language TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
)
""")
conn.commit()

# --- Models ---
class User(BaseModel):
    username: str
    password: str

class Profile(BaseModel):
    username: str
    name: str
    age_group: str
    language: str

class ChatMessage(BaseModel):
    message: str

# --- Auth Routes ---
@app.post("/register")
def register(user: User):
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (user.username, hashed_pw))
        conn.commit()
        return {"message": "User registered successfully!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/login")
def login(user: User):
    cursor.execute("SELECT password FROM users WHERE username=?", (user.username,))
    row = cursor.fetchone()
    if row and bcrypt.checkpw(user.password.encode('utf-8'), row[0]):
        return {"message": "Login successful!"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

# --- Profile Routes ---
@app.post("/profile")
def save_profile(profile: Profile):
    cursor.execute("SELECT 1 FROM users WHERE username=?", (profile.username,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("DELETE FROM profiles WHERE username=?", (profile.username,))
    cursor.execute(
        "INSERT INTO profiles(username, name, age_group, language) VALUES (?, ?, ?, ?)",
        (profile.username, profile.name, profile.age_group, profile.language)
    )
    conn.commit()
    return {"message": "Profile saved successfully!"}

@app.get("/profile/{username}")
def get_profile(username: str):
    cursor.execute("SELECT name, age_group, language FROM profiles WHERE username=?", (username,))
    row = cursor.fetchone()
    if row:
        return {"name": row[0], "age_group": row[1], "language": row[2]}
    raise HTTPException(status_code=404, detail="Profile not found")

# --- ML Model for Chat ---
try:
    df = pd.read_csv("intents.csv")
except FileNotFoundError:
    raise RuntimeError("intents.csv file not found!")

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df["text"])
model = LogisticRegression()
model.fit(X, df["intent"])

responses = {
    "greet": "👋 Hello! I'm WellBot, your wellness companion. How are you feeling today?",
    "stress": "😌 I hear you’re stressed. Try 5 minutes of deep breathing — inhale slowly, hold, exhale.",
    "exercise": "💪 Exercise keeps the body strong! Start with 20 minutes of walking or light yoga.",
    "sleep": "🌙 Sleep is vital! Avoid screens before bed and try calming music.",
    "nutrition": "🥗 A balanced diet works wonders! Add more fruits, veggies, and drink enough water.",
}

@app.post("/chat")
def chat(msg: ChatMessage):
    user_msg = msg.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    X_test = vectorizer.transform([user_msg])
    predicted_intent = model.predict(X_test)[0]
    bot_reply = responses.get(predicted_intent, "🤔 I'm not sure, but I can keep learning.")

    return {"user": user_msg, "intent": predicted_intent, "bot": bot_reply}
