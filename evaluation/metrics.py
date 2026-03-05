
from collections import Counter

def compute_metrics(results):

    total = len(results)
    correct = sum(1 for r in results if r["predicted_label"] == r["true_label"])

    acc = correct / total if total else 0

    labels = Counter(r["predicted_label"] for r in results)

    return {
        "accuracy": acc,
        "prediction_distribution": dict(labels),
        "total": total
    }
