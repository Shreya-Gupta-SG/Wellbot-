

import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.db")

def get_response_from_db(intent):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT response FROM kb_responses WHERE intent=?", (intent,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return None
    return random.choice([r[0] for r in rows])

def add_response(intent, response):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO kb_responses (intent, response) VALUES (?, ?)", (intent, response))
    conn.commit()
    conn.close()
