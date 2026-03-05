from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Tuple

@dataclass
class Rule:
    rule_id: str
    category: str
    weight: float
    claim: str
    evidence_atoms: List[str]
    cond: Callable[[Dict[str, Any], Dict[str, Any]], bool]
    note: str = ""

def score_rules(attributes: Dict[str, Any], atoms: Dict[str, Any], rules: List[Rule]) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    fired: List[Dict[str, Any]] = []
    scores = {"benign":0.0,"phishing":0.0,"malware":0.0,"generic_risk":0.0}

    for r in rules:
        if r.cond(attributes, atoms):
            fired.append({
                "rule_id": r.rule_id,
                "claim": r.claim,
                "category": r.category,
                "weight": r.weight,
                "evidence_atoms": r.evidence_atoms,
                "note": r.note or "-"
            })
            scores[r.category] += r.weight
    return fired, scores

def decide(scores: Dict[str, float]) -> Tuple[str, str]:
    cls = {k: scores[k] for k in ("benign","phishing","malware")}
    top = max(cls, key=cls.get)
    topv = cls[top]
    second = sorted(cls.values(), reverse=True)[1]
    margin = topv - second

    if topv >= 4.0 and margin >= 1.0:
        pred = top
    else:
        pred = "unknown"

    if pred == "unknown":
        conf = "low" if topv < 6 else "medium"
    else:
        conf = "high" if (topv >= 7 and margin >= 2) else ("medium" if (topv >= 5 and margin >= 1) else "low")
    return pred, conf

def default_rules() -> List[Rule]:
    R: List[Rule] = []
    def add(rule_id, cat, w, claim, atoms_needed, cond, note=""):
        R.append(Rule(rule_id, cat, float(w), claim, list(atoms_needed), cond, note))

    # --- Example: learned-atom integration rules (keep weights moderate) ---
    add("L01","phishing",2.0,
        "Model indicates high phishing probability (learned evidence).",
        ["ML_PHISH_PROB_GE_0_9"],
        lambda a,atoms: atoms.get("ML_PHISH_PROB_GE_0_9") is True)

    add("L02","malware",2.0,
        "Model indicates high malware probability (learned evidence).",
        ["ML_MALWARE_PROB_GE_0_85"],
        lambda a,atoms: atoms.get("ML_MALWARE_PROB_GE_0_85") is True)

    add("L03","generic_risk",2.0,
        "High calibrated risk score (learned evidence).",
        ["CAL_RISK_GE_0_7"],
        lambda a,atoms: atoms.get("CAL_RISK_GE_0_7") is True)

    # You would also include your existing B/P/M/G base rules here.
    return R
