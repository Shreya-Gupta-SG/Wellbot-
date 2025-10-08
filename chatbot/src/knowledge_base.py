import json
import os
from typing import Dict, Any

# -------------------- Load Knowledge Base -------------------- #
KB_FILE = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

def load_kb() -> Dict[str, Any]:
    """Load the knowledge base from JSON file."""
    if not os.path.exists(KB_FILE):
        raise FileNotFoundError(f"Knowledge base file not found: {KB_FILE}")

    with open(KB_FILE, "r", encoding="utf-8") as f:
        kb = json.load(f)

    # Normalize all keys to lowercase for easier matching
    normalized_kb = {k.lower(): v for k, v in kb.items()}
    return normalized_kb


# -------------------- Format Health Info -------------------- #
def format_health_info(
    info: Dict[str, Any],
    illness: str = None,
    topic: str = None,
    language: str = "en"
) -> str:
    """
    Returns a clean, readable formatted string for chatbot display.
    Works in both English and Hindi.
    """
    lines = []

    # Illness / Topic Header
    if illness:
        lines.append(f"🩺 {'बीमारी' if language == 'hi' else 'Illness'}: {illness.capitalize()}")

    # Description
    desc = info.get("description", {})
    if isinstance(desc, dict):
        desc = desc.get(language, desc.get("en", ""))
    if desc:
        lines.append(f"{'🔹 विवरण' if language == 'hi' else '🔹 Description'}: {desc}")

    # Symptoms
    symptoms = info.get("symptoms", [])
    if symptoms:
        sym_display = ", ".join(symptoms[:12])  # limit long lists
        lines.append(f"{'💡 लक्षण' if language == 'hi' else '💡 Symptoms'}: {sym_display}")

    # Treatment
    treatment = info.get("treatment", {})
    if isinstance(treatment, dict):
        treatment = treatment.get(language, treatment.get("en", []))
    if treatment:
        lines.append("💊 उपचार:" if language == "hi" else "💊 Treatment:")
        for t in treatment:
            lines.append(f"  • {t}")

    # Warning
    warning = info.get("warning", {})
    if isinstance(warning, dict):
        warning = warning.get(language, warning.get("en", ""))
    if warning:
        lines.append(f"{'⚠️ चेतावनी' if language == 'hi' else '⚠️ Warning'}: {warning}")

    # Lifestyle topics like stress, sleep, etc.
    if topic and not illness:
        lines.append(f"\n💡 सुझाव ({topic}):" if language == "hi" else f"\n💡 Tips ({topic}):")
        if treatment:
            for t in treatment:
                lines.append(f"  • {t}")

    return "\n".join(lines)
