import os
import sys
import json
import sqlite3
import bcrypt
import traceback
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Path setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "chatbot", "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

# --- Import dialogue manager ---
try:
    from chatbot.src.dialogue_manager import get_bot_reply
except ImportError:
    raise ImportError("❌ Could not import dialogue_manager.py. Ensure it's in chatbot/src.")

# --- FastAPI app ---
app = FastAPI(title="WellBot Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database setup ---
DB_PATH = os.path.join(BASE_DIR, "users.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# --- Tables ---
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT UNIQUE,
    password BLOB
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS profiles(
    username TEXT,
    name TEXT,
    age_group TEXT,
    language TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS chat_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    question TEXT,
    answer TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS feedback(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    question TEXT,
    answer TEXT,
    rating INTEGER,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS kb(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
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

# --- Auth routes ---
@app.post("/register")
def register(user: User):
    try:
        hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
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

# --- Chat Route ---
@app.post("/chat")
def chat(msg: ChatMessage):
    user_msg = msg.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        bot_reply = get_bot_reply(user_id=msg.user_id, user_message=user_msg)
    except Exception:
        traceback.print_exc()
        bot_reply = "⚠️ Sorry, there was an error processing your request."

    cursor.execute(
        "INSERT INTO chat_history(user_id, question, answer) VALUES (?, ?, ?)",
        (msg.user_id, user_msg, bot_reply),
    )
    conn.commit()

    return {"user": user_msg, "bot": bot_reply}

@app.get("/chat/history/{user_id}")
def get_chat_history(user_id: str):
    cursor.execute("SELECT question, answer, timestamp FROM chat_history WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    return [{"question": q, "answer": a, "timestamp": t} for q, a, t in rows]

# --- Feedback ---
@app.post("/feedback")
def save_feedback(data: dict):
    cursor.execute(
        "INSERT INTO feedback(user_id, question, answer, rating, comment) VALUES (?,?,?,?,?)",
        (data["user_id"], data["question"], data["answer"], data.get("rating", None), data.get("comment", "")),
    )
    conn.commit()
    return {"message": "Feedback saved!"}

@app.get("/feedback/{user_id}")
def get_feedback(user_id: str):
    cursor.execute("SELECT question, answer, rating, comment, timestamp FROM feedback WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    return [{"question": q, "answer": a, "rating": r, "comment": c, "timestamp": t} for q, a, r, c, t in rows]

# --- Analytics ---
@app.get("/analytics")
def get_analytics():
    # Total queries
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_queries = cursor.fetchone()[0]

    # Failed queries (bot replies with ⚠️)
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE answer LIKE '⚠️%'")
    failed_queries = cursor.fetchone()[0]

    # Daily queries
    cursor.execute("SELECT DATE(timestamp), COUNT(*) FROM chat_history GROUP BY DATE(timestamp)")
    daily_queries = {row[0]: row[1] for row in cursor.fetchall()}

    # Feedback
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating=1")
    thumbs_up = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating=0")
    thumbs_down = cursor.fetchone()[0]
    total_feedback = thumbs_up + thumbs_down
    feedback_percentage = int((thumbs_up / total_feedback) * 100) if total_feedback > 0 else 0

    # Top failed queries
    cursor.execute("SELECT question FROM chat_history WHERE answer LIKE '⚠️%'")
    failed_list = [row[0] for row in cursor.fetchall()]

    return {
        "total_queries": total_queries,
        "failed_queries": failed_queries,
        "daily_queries": daily_queries,
        "positive_feedback": thumbs_up,
        "negative_feedback": thumbs_down,
        "feedback_percentage": feedback_percentage,
        "failed_queries_list": failed_list
    }

# --- Knowledge Base management ---
@app.get("/kb")
def get_kb():
    cursor.execute("SELECT id, question, answer FROM kb")
    rows = cursor.fetchall()
    return [{"id": i, "question": q, "answer": a} for i, q, a in rows]

@app.post("/kb")
def add_kb(entry: dict):
    cursor.execute("INSERT INTO kb(question, answer) VALUES (?, ?)", (entry["question"], entry["answer"]))
    conn.commit()
    return {"message": "KB entry added!"}

@app.put("/kb/{entry_id}")
def edit_kb(entry_id: int, entry: dict):
    cursor.execute("UPDATE kb SET question=?, answer=? WHERE id=?", (entry["question"], entry["answer"], entry_id))
    conn.commit()
    return {"message": "KB entry updated!"}

@app.delete("/kb/{entry_id}")
def delete_kb(entry_id: int):
    cursor.execute("DELETE FROM kb WHERE id=?", (entry_id,))
    conn.commit()
    return {"message": "KB entry deleted!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port)


    

