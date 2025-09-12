from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import bcrypt
import os
import json
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# --- Import Dialogue Manager ---
from chatbot.src.dialogue_manager import get_bot_reply, detect_rule_based_intent  

# --- Initialize FastAPI ---
app = FastAPI(title="WellBot Backend")

# --- Enable CORS (for frontend communication) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev (change to specific domain in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT UNIQUE,
    password BLOB
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS profiles(
    username TEXT,
    name TEXT,
    age_group TEXT,
    language TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS chat_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    question TEXT,
    answer TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)""")

conn.commit()

# --- Pydantic Models ---
class User(BaseModel):
    username: str
    password: str

class Profile(BaseModel):
    username: str
    name: str
    age_group: str
    language: str

class ChatMessage(BaseModel):
    user_id: str
    message: str

# --- Load Trained Intent Model ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "chatbot", "models", "intent_model")

if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"❌ Trained intent model not found at {MODEL_PATH}")

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

with open(os.path.join(MODEL_PATH, "label_map.json")) as f:
    label2id = json.load(f)
id2label = {v: k for k, v in label2id.items()}

# --- Intent Mapping (Model → Dialogue Manager) ---
intent_mapping = {
    "greeting": "greet",
    "mood_check": "mood_check",
    "ask_symptom": "ask_symptom",
    "feeling_bad": "negative_mood",
    "stress_issue": "stress",
    "sleep_issue": "sleep",
    "exercise_query": "exercise",
    "chitchat": "chitchat",
    "goodbye": "goodbye",
    "thanks": "thanks",
    "give_tip": "give_tip"
}

# --- Auth Routes ---
@app.post("/register")
def register(user: User):
    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
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
    if row and bcrypt.checkpw(user.password.encode("utf-8"), row[0]):
        return {"message": "Login successful!"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/profile")
def save_profile(profile: Profile):
    cursor.execute("SELECT 1 FROM users WHERE username=?", (profile.username,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("DELETE FROM profiles WHERE username=?", (profile.username,))
    cursor.execute(
        "INSERT INTO profiles(username, name, age_group, language) VALUES (?, ?, ?, ?)",
        (profile.username, profile.name, profile.age_group, profile.language),
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

# --- Chat Endpoint ---
@app.post("/chat")
def chat(msg: ChatMessage):
    user_msg = msg.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # --- Intent Detection ---
    rule_intent = detect_rule_based_intent(user_msg)

    if rule_intent:
        mapped_intent = rule_intent
    else:
        inputs = tokenizer(user_msg, return_tensors="pt", padding=True, truncation=True, max_length=64)
        with torch.no_grad():
            outputs = model(**inputs)
            predicted_class_id = outputs.logits.argmax(dim=-1).item()

        predicted_intent = id2label[predicted_class_id]
        mapped_intent = intent_mapping.get(predicted_intent, predicted_intent)

    # --- Get reply from dialogue manager ---
    bot_reply = get_bot_reply(user_id=msg.user_id, user_message=user_msg, intent=mapped_intent)

    # --- Store chat in DB ---
    cursor.execute(
        "INSERT INTO chat_history (user_id, question, answer) VALUES (?, ?, ?)",
        (msg.user_id, user_msg, bot_reply)
    )
    conn.commit()

    return {"user": user_msg, "intent": mapped_intent, "bot": bot_reply}

# --- Chat History Route (Optional for Debugging/UI) ---
@app.get("/chat/history/{user_id}")
def get_chat_history(user_id: str):
    cursor.execute("SELECT question, answer, timestamp FROM chat_history WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    return [{"question": q, "answer": a, "timestamp": t} for q, a, t in rows]
