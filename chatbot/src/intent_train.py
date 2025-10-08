import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score
import json

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_DIR = os.path.join(BASE_DIR, "chatbot", "models", "intent_model")

TRAIN_PATH = os.path.join(DATA_DIR, "train.csv")
TEST_PATH = os.path.join(DATA_DIR, "test.csv")

os.makedirs(MODEL_DIR, exist_ok=True)

# --- Load datasets ---
train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

# Encode labels
label_encoder = LabelEncoder()
train_df["label"] = label_encoder.fit_transform(train_df["intent"])
test_df["label"] = label_encoder.transform(test_df["intent"])

# Save label map
label2id = {label: idx for idx, label in enumerate(label_encoder.classes_)}
id2label = {idx: label for label, idx in label2id.items()}

with open(os.path.join(MODEL_DIR, "label_map.json"), "w") as f:
    json.dump(label2id, f)

# --- Tokenizer ---
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def tokenize_data(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=64)

# Convert pandas → HuggingFace dataset
train_ds = Dataset.from_pandas(train_df)
test_ds = Dataset.from_pandas(test_df)

train_ds = train_ds.map(tokenize_data, batched=True)
test_ds = test_ds.map(tokenize_data, batched=True)

train_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
test_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

# --- Model ---
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(label2id),
    id2label=id2label,
    label2id=label2id
)

# --- Training args (safe for old versions) ---
args_kwargs = {
    "output_dir": os.path.join(BASE_DIR, "results"),
    "learning_rate": 2e-5,
    "per_device_train_batch_size": 8,
    "per_device_eval_batch_size": 8,
    "num_train_epochs": 3,
    "weight_decay": 0.01,
    "logging_dir": os.path.join(BASE_DIR, "logs"),
    "logging_steps": 10
}

# Try to add new args if available
try:
    training_args = TrainingArguments(
        **args_kwargs,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1
    )
except TypeError:
    print("Old Transformers version detected → skipping evaluation_strategy & save_strategy")
    training_args = TrainingArguments(**args_kwargs)

# --- Metrics ---
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    return {"accuracy": accuracy_score(labels, preds)}

# --- Trainer ---
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=test_ds,
    compute_metrics=compute_metrics
)

# --- Train & Save ---
trainer.train()
model.save_pretrained(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)
print(f"Model trained and saved at {MODEL_DIR}")
