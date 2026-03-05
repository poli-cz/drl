from __future__ import annotations
from typing import Any, Dict, List

class MLProbThresholdProvider:
    """Example learned-atom provider.

    This provider assumes your pipeline already computed model probabilities and put them into ATTRIBUTES:
      - ml_phish_prob
      - ml_malware_prob

    If you prefer, replace this with a provider that loads a model (joblib/onnx) and computes these scores.
    """

    PROVIDER_ID = "ml_probs"
    PROVIDER_VERSION = "1.0.0"
    CACHEABLE = True
    VALIDATE_WITH_REGISTRY = True

    def compute(self, domain: str, attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
        atoms: List[Dict[str, Any]] = []

        def add(name: str, value: Any, note: str):
            atoms.append({"atom": name, "value": value, "from": f"learned:{self.PROVIDER_ID}@{self.PROVIDER_VERSION}", "note": note})

        # If attributes are missing, emit nothing; the caller can decide to request them.
        if "ml_phish_prob" in attributes:
            p = float(attributes["ml_phish_prob"])
            add("ML_PHISH_PROB_GE_0_9", p >= 0.90, f"ml_phish_prob={p:.3f} threshold=0.90")

        if "ml_malware_prob" in attributes:
            p = float(attributes["ml_malware_prob"])
            add("ML_MALWARE_PROB_GE_0_85", p >= 0.85, f"ml_malware_prob={p:.3f} threshold=0.85")

        return atoms

def get_provider():
    return MLProbThresholdProvider()
