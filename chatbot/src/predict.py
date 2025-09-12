import json
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

#Load model + tokenizer + label map
MODEL_PATH = "C:/Users/lenov/OneDrive/Desktop/Wellbot/chatbot/models/intent_model"


tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

with open(f"{MODEL_PATH}/label_map.json") as f:
    label2id = json.load(f)
id2label = {v: k for k, v in label2id.items()}

#Prediction function
def predict_intent(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=64)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_id = logits.argmax(dim=-1).item()
    intent = id2label[predicted_class_id]
    return intent

#Test
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Exiting...")
            break
        intent = predict_intent(user_input)
        print(f"Predicted intent → {intent}")
