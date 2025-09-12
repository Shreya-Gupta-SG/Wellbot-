
import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.db")

seed_data = {
    "greet": [
        "👋 Hello! I'm WellBot. How are you feeling today?",
        "Hi there! 😊 I’m doing well, thanks for asking. How about you?",
        "Hey! I’m here to chat and support you. How are things going?"
    ],
    "positive_mood": [
        "😊 That’s wonderful to hear! Keep spreading the good vibes!",
        "Awesome! What made you feel this way today?",
        "Glad you’re feeling good 💙. Stay positive!"
    ],
    "ask_symptom": [
        "🩺 Thanks for sharing. Mild headaches can sometimes be caused by stress or dehydration. Try drinking some water and resting.",
        "That sounds uncomfortable. If it continues, it’s a good idea to consult a doctor.",
        "It seems like you’re sharing a symptom. Would you like me to suggest some quick self-care tips?"
    ],
    "mood_check": [
        "💙 I hear you. Feeling low can be tough. Do you want me to share some coping strategies?",
        "I’m sorry you’re feeling this way. Remember, it’s okay to not be okay. You’re not alone.",
        "Sometimes expressing your feelings can help. Want me to suggest some relaxation or mindfulness activities?"
    ],
    "give_tip": [
        "💡 Fitness tip: Start with short daily walks or stretching. Consistency matters more than intensity.",
        "Remember to stay hydrated and get enough sleep — they’re as important as exercise.",
        "Healthy eating + regular movement = better energy. Do you want me to suggest a simple workout plan?"
    ],
    "thanks": [
        "You’re welcome! 💙",
        "Glad I could help! 😊",
        "Anytime! Take care of yourself."
    ],
    "goodbye": [
        "Goodbye! 👋 Take care of yourself.",
        "See you later! Stay positive 🌟",
        "Bye for now! Remember, I’m here whenever you need me."
    ],
    "stress": [
        "😌 Stress is normal. Try deep breathing or a short walk — it helps!",
        "Stress can be tough. How about taking a 5-minute break?",
        "Relaxation tip: inhale deeply for 4s, hold 4s, exhale 4s."
    ],
    "sleep": [
        "🌙 Sleep is essential. Try to go to bed at the same time each night.",
        "Avoid screens 1 hour before sleep for better rest.",
        "A calm night routine helps. Want me to suggest one?"
    ],
    "diet": [
        "🥗 A balanced diet fuels your body. Include veggies, protein, and water!",
        "Skipping meals can make you tired. Try small, healthy snacks.",
        "Eat mindfully — enjoy your food without distractions."
    ],
    "motivation": [
        "🚀 You’ve got this! Take small steps and celebrate progress.",
        "Motivation comes and goes — discipline keeps you going 💪.",
        "Set one small goal for today and smash it!"
    ],
    "loneliness": [
        "💙 Feeling lonely is tough. Talking to a friend or journaling might help.",
        "You’re not alone. Would you like me to suggest calming activities?",
        "Sometimes connecting with nature or music can ease loneliness."
    ],
    "crisis": [
        "💙 I hear your pain. You are not alone. If you feel like giving up, please reach out to a trusted friend or professional immediately.",
        "If you are in danger of hurting yourself, please call your local emergency number. In India, you can call the AASRA helpline at +91-9820466726.",
        "You matter. Talking to someone can help — please don’t go through this alone."
    ],
    "exercise": [
        "💪 Exercise is great for both mind and body! Even 10 mins of stretching counts.",
        "Try to keep it fun — dance, yoga, or a quick walk!",
        "Fitness tip: set small, realistic goals so you stay consistent."
    ],
    "hydration": [
        "💧 Water keeps you energized! Aim for 6–8 glasses a day.",
        "Feeling low on energy? Try drinking a glass of water.",
        "Hydration tip: carry a water bottle to remind yourself."
    ],
    "mindfulness": [
        "🧘 Try this: Close your eyes, take a deep breath, and focus on your inhale and exhale for 1 minute.",
        "Mindfulness helps calm the mind. Want me to guide you through a short breathing exercise?",
        "Even 2 minutes of silence can refresh your mood."
    ],
    "productivity": [
        "📌 Try the Pomodoro technique: 25 mins focus, 5 mins break.",
        "Write down your top 3 tasks for today and focus on them.",
        "Small steps beat procrastination. What’s one thing you can do now?"
    ],
    "relationships": [
        "💙 Relationships can be tricky. It helps to talk openly about your feelings.",
        "Conflicts happen — listening calmly often makes things better.",
        "You deserve respect and kindness in relationships. Want me to share tips for handling conflicts?"
    ],
    "bot_feeling": [
        "I’m doing great, thanks for asking! 😊 How are you?",
        "I’m just a bot, but I feel happy chatting with you 💙",
        "Thanks for asking! I’m here and ready to listen to you 👂"
    ],
    "affirm": [
        "Great 👍 Let’s continue!",
        "Okay 💙, noted!",
        "Perfect! Do you want me to suggest something helpful?"
    ],
    "chitchat": [
        "Haha, that’s interesting! Tell me more 😊",
        "Oh nice! What else do you enjoy?",
        "😄 I like chatting with you. Want to talk about wellness or just random things?"
    ]
}

def create_and_seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS kb_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intent TEXT NOT NULL,
            response TEXT NOT NULL
        )
    """)
    c.execute("SELECT COUNT(1) FROM kb_responses")
    if c.fetchone()[0] == 0:
        rows = []
        for intent, resp_list in seed_data.items():
            for r in resp_list:
                rows.append((intent, r))
        c.executemany("INSERT INTO kb_responses (intent, response) VALUES (?, ?)", rows)
        conn.commit()
        print(f"Seeded {len(rows)} rows into {DB_PATH}")
    else:
        print("DB already seeded.")
    conn.close()

if __name__ == "__main__":
    create_and_seed()
