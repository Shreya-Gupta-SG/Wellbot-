
from knowledge_base import get_response_from_db

for intent in ["greet", "ask_symptom", "mood_check", "goodbye", "crisis", "give_tip", "hydration"]:
    print(intent, "->", get_response_from_db(intent))
