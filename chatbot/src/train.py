import pandas as pd
from datasets import Dataset
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch

full_df = pd.read_csv("data/intent_dataset.csv")
labels_list = full_df["intent"].unique().tolist()  
label2id = {label: i for i, label in enumerate(labels_list)}
id2label = {i: label for label, i in label2id.items()}

#Load splits
train_df = pd.read_csv("data/train.csv")
val_df = pd.read_csv("data/val.csv")

train_df["label"] = train_df["intent"].map(label2id)
val_df["label"] = val_df["intent"].map(label2id)

train_ds = Dataset.from_pandas(train_df[["sentence", "label"]])
val_ds = Dataset.from_pandas(val_df[["sentence", "label"]])

tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["sentence"], padding="max_length", truncation=True, max_length=64)

train_ds = train_ds.map(tokenize, batched=True)
val_ds = val_ds.map(tokenize, batched=True)

model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(labels_list),
    id2label=id2label,
    label2id=label2id,
)

training_args = TrainingArguments(
    output_dir="models/intent_model",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=15,  
    weight_decay=0.01,
    logging_dir="models/logs",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
)

#Metrics
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

#Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

#Train
trainer.train()

#Save model + label mapping
trainer.save_model("models/intent_model")
tokenizer.save_pretrained("models/intent_model")

import json
with open("models/intent_model/label_map.json", "w") as f:
    json.dump(label2id, f)

print("Training complete. Model saved in models/intent_model/")
