import pandas as pd
from sklearn.model_selection import train_test_split

def preprocess():
    #Load dataset
    df = pd.read_csv("data/intent_dataset.csv")

    #Lowercase sentences
    df["sentence"] = df["sentence"].str.lower().str.strip()

    #Train/val/test split
    train_df, temp_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["intent"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df["intent"]
    )

    #Save splits
    train_df.to_csv("data/train.csv", index=False)
    val_df.to_csv("data/val.csv", index=False)
    test_df.to_csv("data/test.csv", index=False)

    print("Preprocessing done")
    print("Train size:", len(train_df))
    print("Val size:", len(val_df))
    print("Test size:", len(test_df))

if __name__ == "__main__":
    preprocess()
