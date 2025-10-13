import random
import re
from typing import List, Dict, Tuple
from .knowledge_base import load_kb, format_health_info

# -------------------- Load Knowledge Base -------------------- #
KB = load_kb()

# -------------------- Symptom to Illness Mapping -------------------- #
SYMPTOM_TO_ILLNESSES = {}
for illness, info in KB.items():
    for sym in info.get("symptoms", []):
        SYMPTOM_TO_ILLNESSES.setdefault(sym.lower(), set()).add(illness)

# -------------------- Session Data -------------------- #
user_sessions: Dict[str, Dict] = {}

# -------------------- Conversation Phrases -------------------- #
GREETINGS = [
    "Hello! How are you feeling today?",
    "Hi there — tell me what symptoms you are experiencing.",
    "Hey! I'm here to help. What symptoms do you have?"
]

GOODBYES = [
    "Goodbye! Take care and stay healthy.",
    "See you soon — stay safe!",
    "Bye! Wishing you good health."
]

MORE_SYMPTOMS = [
    "Can you tell me more symptoms?",
    "Any other symptoms you're feeling?",
    "What else are you experiencing?"
]

DISCLAIMER = (
    " *Disclaimer:* I'm not a medical professional. "
    "I can only suggest possible conditions based on your symptoms, "
    "but please consult a healthcare provider for accurate diagnosis."
)

# -------------------- Regex for Entity Extraction -------------------- #
duration_pattern = re.compile(r"\bfor\s+(\d+)\s+days?\b")
severity_pattern = re.compile(r"\b(mild|moderate|severe)\b")

# -------------------- Helper Functions -------------------- #
def extract_entities(text: str) -> Dict[str, str]:
    entities = {}
    d = duration_pattern.search(text)
    s = severity_pattern.search(text)
    if d:
        entities["duration"] = f"{d.group(1)} days"
    if s:
        entities["severity"] = s.group(1)
    return entities

def extract_symptoms(text: str) -> List[str]:
    found = []
    lower_text = text.lower()
    for symptom in SYMPTOM_TO_ILLNESSES.keys():
        if symptom in lower_text and symptom not in found:
            found.append(symptom)
    return found

def add_symptoms(user_id: str, symptoms: List[str], entities: Dict[str, str]):
    session = user_sessions.setdefault(user_id, {"symptoms": set(), "entities": {}})
    for s in symptoms:
        session["symptoms"].add(s)
    for k, v in entities.items():
        if k not in session["entities"]:
            session["entities"][k] = v

def detect_possible_illnesses(symptoms: List[str]) -> List[Tuple[str, int]]:
    matches = []
    sym_set = set(symptoms)
    for illness, info in KB.items():
        ill_syms = set(s.lower() for s in info.get("symptoms", []))
        common = sym_set & ill_syms
        if common:
            matches.append((illness, len(common)))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

def suggest_more_symptoms(current: List[str]) -> List[str]:
    all_syms = set(SYMPTOM_TO_ILLNESSES.keys())
    remaining = list(all_syms - set(current))
    random.shuffle(remaining)
    return remaining[:3]

# -------------------- Intent Detection -------------------- #
def detect_rule_based_intent(msg: str) -> str:
    m = msg.lower()
    if any(w in m for w in ["hi", "hello", "hey", "namaste", "नमस्ते"]):
        return "greet"
    if any(w in m for w in ["bye", "goodbye", "see you", "tata", "फिर मिलेंगे"]):
        return "goodbye"
    if any(w in m for w in ["stress", "anxious", "sad", "depressed", "tension", "तनाव", "उदास"]):
        return "stress"
    if any(w in m for w in ["sleep", "tired", "insomnia", "नींद", "थकान"]):
        return "sleep"
    if any(w in m for w in ["exercise", "workout", "gym", "योग", "फिटनेस"]):
        return "exercise"
    if any(p in m for p in ["what do i have", "diagnose", "so what do i have", "कौन सी बीमारी"]):
        return "diagnosis_query"
    return None

# -------------------- Language Detection -------------------- #
def detect_language(msg: str) -> str:
    if re.search(r"[ऀ-ॿ]", msg):
        return "hi"
    return "en"

# -------------------- Diagnosis Response -------------------- #
def build_diagnosis_and_reset(user_id: str, matches: List[Tuple[str, int]], language: str) -> str:
    top_matches = [m[0] for m in matches[:3]]
    user_sessions.pop(user_id, None)

    if language == "hi":
        illnesses = ", ".join(top_matches)
        response = f"⚠️ कृपया डॉक्टर से परामर्श लें। संभावित बीमारियां: {illnesses}\n\n"
        for ill in top_matches:
            info = KB.get(ill, {})
            response += format_health_info(info, illness=ill, language="hi") + "\n\n"
        return response.strip()

    response_parts = [DISCLAIMER, ""]
    for ill in top_matches:
        info = KB.get(ill, {})
        response_parts.append(format_health_info(info, illness=ill, language="en"))
        response_parts.append("")
    response_parts.append(f"**Possible conditions:** {', '.join(top_matches)}")
    return "\n".join(response_parts)

# -------------------- Core Chatbot Logic -------------------- #
def get_bot_reply(user_id: str, user_message: str) -> str:
    msg = user_message.strip()
    language = detect_language(msg)

    # Greeting / Goodbye always handled first
    intent = detect_rule_based_intent(msg)
    if intent == "greet":
        if user_id not in user_sessions:
            user_sessions[user_id] = {"symptoms": set(), "entities": {}}
        return random.choice(GREETINGS) if language == "en" else "नमस्ते! आप आज कैसा महसूस कर रहे हैं?"
    if intent == "goodbye":
        user_sessions.pop(user_id, None)
        return random.choice(GOODBYES) if language == "en" else "अलविदा! स्वस्थ रहें!"

    # -------------------- Symptom Handling -------------------- #
    new_syms = extract_symptoms(msg)
    ents = extract_entities(msg)
    if new_syms or ents:
        add_symptoms(user_id, new_syms, ents)

    sess = user_sessions.get(user_id, {"symptoms": set()})
    all_syms = list(sess["symptoms"])

    # If enough symptoms, give diagnosis
    if len(all_syms) >= 2:
        matches = detect_possible_illnesses(all_syms)
        if matches and matches[0][1] >= 2:
            return build_diagnosis_and_reset(user_id, matches, language)

    # If only 1 symptom, ask for more
    if len(all_syms) < 2:
        return random.choice(MORE_SYMPTOMS) if language == "en" else "क्या आप मुझे और लक्षण बता सकते हैं?"

    # Suggest additional symptoms if needed
    remaining = suggest_more_symptoms(all_syms)
    if remaining:
        return f"Do you also have {remaining[0]}?" if language == "en" else f"क्या आपको {remaining[0]} भी है?"

    # -------------------- Lifestyle / Emotional / Sleep Queries -------------------- #
    if intent in ["stress", "sleep", "exercise"]:
        info = KB.get(intent, {})
        return format_health_info(info, topic=intent, language=language)

    # -------------------- Diagnosis Request -------------------- #
    if intent == "diagnosis_query":
        if not all_syms:
            return (
                "I don’t have enough symptoms yet. Please tell me what you’re feeling."
                if language == "en"
                else "मुझे अभी आपके लक्षणों की पूरी जानकारी नहीं है। कृपया अपने लक्षण बताएं।"
            )
        matches = detect_possible_illnesses(all_syms)
        if not matches:
            return (
                "I need a few more symptoms to make a suggestion."
                if language == "en"
                else "मुझे सुझाव देने के लिए कुछ और लक्षणों की आवश्यकता है।"
            )
        return build_diagnosis_and_reset(user_id, matches, language)

    # Default fallback
    return (
        "I need a bit more information. " + random.choice(MORE_SYMPTOMS)
        if language == "en"
        else "मुझे और जानकारी चाहिए। कृपया कुछ और लक्षण बताएं।"
    )

