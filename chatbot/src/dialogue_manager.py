import random
from transformers import pipeline

# Load BART model once (for fallback responses)
bart = pipeline("text2text-generation", model="facebook/bart-large-cnn")

# Store conversation context per user
user_contexts = {}

# Predefined responses for each intent
responses = {
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

    # --- Rule-based wellness intents ---
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

    # --- New ones ---
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


# --- Rule-based detector ---
def detect_rule_based_intent(user_msg: str):
    user_msg = user_msg.lower()

    if user_msg in ["yes", "yeah", "yep", "sure", "of course"]:
        return "affirm"
    if any(word in user_msg for word in ["stress", "stressed", "anxious", "pressure"]):
        return "stress"
    if any(word in user_msg for word in ["sleep", "sleepy", "tired", "insomnia"]):
        return "sleep"
    if any(word in user_msg for word in ["diet", "food", "eat", "meal", "nutrition"]):
        return "diet"
    if any(word in user_msg for word in ["motivation", "motivated", "inspired", "drive", "lazy"]):
        return "motivation"
    if any(word in user_msg for word in ["lonely", "alone", "isolated", "unloved"]):
        return "loneliness"
    if any(word in user_msg for word in ["suicide", "give up", "kill myself", "end my life", "die", "worthless", "hopeless"]):
        return "crisis"
    if any(word in user_msg for word in ["exercise", "workout", "gym", "fit"]):
        return "exercise"
    if any(word in user_msg for word in ["water", "drink", "hydrated", "thirsty"]):
        return "hydration"
    if any(word in user_msg for word in ["meditate", "mindful", "calm", "relax"]):
        return "mindfulness"
    if any(word in user_msg for word in ["focus", "study", "concentrate", "work"]):
        return "productivity"
    if any(word in user_msg for word in ["friend", "family", "love", "relationship"]):
        return "relationships"
    if any(word in user_msg for word in ["joke", "fun", "music", "movie"]):
        return "chitchat"
    if any(phrase in user_msg for phrase in ["how are you", "how r u", "how do you feel"]):
        return "bot_feeling"

    return None


# --- Dialogue Manager ---
def get_bot_reply(user_id: str, user_message: str, intent: str) -> str:
    """
    Dialogue management function:
    - Uses predicted intent from trained model
    - Rule-based overrides for wellness & safety
    - Predefined responses or BART fallback
    - Maintains user context
    """
    user_message = user_message.lower()
    context = user_contexts.get(user_id, {"last_intent": None})

    # Apply rule-based overrides
    rule_intent = detect_rule_based_intent(user_message)
    if rule_intent:
        intent = rule_intent

    if intent in responses:
        # Special handling: if user says "yes" after symptom, continue from ask_symptom
        if intent == "affirm" and context.get("last_intent") == "ask_symptom":
            response = "Okay 👍 Here are some quick self-care tips: drink water, rest your eyes, and take a short walk."
        else:
            response = random.choice(responses[intent])
    else:
        # --- Fallback with BART ---
        prompt = (
            f"The user said: '{user_message}'. "
            "Reply briefly in a supportive and friendly way."
        )
        bart_output = bart(prompt, max_new_tokens=60, do_sample=True, top_p=0.9, temperature=0.7)
        response = bart_output[0]["generated_text"]

    # Save context
    context["last_intent"] = intent
    user_contexts[user_id] = context
    return response
