import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

# Paths
TRAIN_PATH = "data/train_data.xlsx"
TEST_PATH = "data/test_data.xlsx"
MODEL_OUTPUT_PATH = "model/rf_model.pkl"

def load_data():
    train_df = pd.read_excel(TRAIN_PATH)
    test_df = pd.read_excel(TEST_PATH)
    return train_df, test_df

def train_and_save_model():
    train_df, test_df = load_data()

    # Features and target
    X_train = train_df.drop(columns=["prognosis"])
    y_train = train_df["prognosis"]

    X_test = test_df.drop(columns=["prognosis"])
    y_test = test_df["prognosis"]

    # Train model
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Predictions
    preds = model.predict(X_test)

    # Metrics
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="weighted")
    report = classification_report(y_test, preds)
    cm = confusion_matrix(y_test, preds, labels=model.classes_)
    
    print(f"\n✅ Accuracy: {acc:.4f}")
    print(f"✅ F1 Score (weighted): {f1:.4f}")
    print("\n📊 Classification Report:\n", report)
    print("📉 Confusion Matrix:\n", cm)

    # Save model
    joblib.dump(model, MODEL_OUTPUT_PATH)
    print(f"\n✅ Model saved to {MODEL_OUTPUT_PATH}")

    # Confusion Matrix Plot (Fix label overlap + blank issue)
    fig, ax = plt.subplots(figsize=(14, 12))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
    disp.plot(ax=ax, cmap="Blues", colorbar=False, xticks_rotation=45)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.show()

    # Plot Feature Importances
    feature_importances = pd.Series(model.feature_importances_, index=X_train.columns)
    top_features = feature_importances.sort_values(ascending=False).head(15)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_features.values, y=top_features.index, palette="viridis")
    plt.title("Top 15 Feature Importances")
    plt.xlabel("Importance")
    plt.ylabel("Features")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    train_and_save_model()
