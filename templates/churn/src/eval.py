import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    auc,
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)

from src.data import event_type_to_int


def plot_eval(
    model,
    X_test_event: list[list[int]],
    X_test_time: list[list[float]],
    y_test: list[int],
    history: keras.callbacks.History,
) -> None:
    # Make predictions with dictionary input
    y_pred_proba = model.predict(
        {"event_input": X_test_event, "time_input": X_test_time}
    )
    y_pred = (y_pred_proba > 0.5).astype(int)

    # 1-4: Keep classification report, confusion matrix, ROC, and PR curves the same
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    plt.show()

    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(8, 6))
    plt.plot(
        fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {roc_auc:.2f})"
    )
    plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.show()

    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    average_precision = average_precision_score(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.step(recall, precision, color="b", alpha=0.2, where="post")
    plt.fill_between(recall, precision, step="post", alpha=0.2, color="b")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title(f"Precision-Recall curve: AP={average_precision:.2f}")
    plt.show()

    # 5. Feature Importance (updated for new layer name)
    event_importances = model.get_layer("event_embedding").get_weights()[0].sum(axis=1)
    event_types = list(event_type_to_int.keys()) + ["padding"]

    importance_df = pd.DataFrame(
        {"importance": event_importances, "event_type": event_types}
    ).sort_values("importance", ascending=True)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=importance_df, x="importance", y="event_type")
    plt.title("Event Type Importance")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.show()

    # 6. Learning Curves
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history["loss"], label="Training Loss")
    plt.plot(history.history["val_loss"], label="Validation Loss")
    plt.title("Model Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history["accuracy"], label="Training Accuracy")
    plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
    plt.title("Model Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.show()
