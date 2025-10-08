import json
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# --- Model Path ---
MODEL_PATH = "C:/Users/lenov/OneDrive/Desktop/Wellbot/chatbot/models/intent_model"

# --- Load Model & Tokenizer ---
print("Loading model...")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()  # set to evaluation mode

# --- Load Label Map ---
with open(f"{MODEL_PATH}/label_map.json") as f:
    label2id = json.load(f)
id2label = {int(v): k for k, v in label2id.items()}  # ensure keys are int

# --- Prediction Function ---
def predict_intent(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=64)
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_class_id = outputs.logits.argmax(dim=-1).item()
    return id2label[predicted_class_id]

# --- Interactive Test Loop ---
if __name__ == "__main__":
    print("Chatbot intent tester. Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Exiting...")
            break
        intent = predict_intent(user_input)
        print(f"Predicted intent → {intent}")
