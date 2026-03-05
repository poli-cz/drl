
# Domain Reasoning Language (DRL)
## Neuro-Symbolic Reasoning Language for Domain Reputation Analysis

DRL-Domain (Domain Reasoning Language) is a **neuro‑symbolic reasoning framework** designed for explainable analysis of internet domains.  
It combines **machine learning outputs, symbolic rules, and structured reasoning** to determine whether a domain is:

- **Benign**
- **Phishing**
- **Malware infrastructure**
- **Unknown / suspicious**

The system is designed for **security research, SOC pipelines, and explainable ML systems** where classification decisions must be **traceable and interpretable**.

---

# Core Idea

Traditional ML classifiers output a label or probability:

```
domain -> phishing (0.93)
```

But they do **not explain why**.

DRL-Domain introduces an intermediate reasoning layer:

```
Features → Atoms → Rules → Decision → Explanation
```

This creates a **structured reasoning trace** which can be audited, logged, and inspected.

Example reasoning flow:

```
domain: example-login-security.vercel.app

Attributes:
  rdap_domain_age = 45 days
  dns_MX_count = 0
  lex_name_len = 34
  ml_phish_prob = 0.93

Derived atoms:
  RDAP_NEW_DOMAIN = True
  DNS_NO_MX = True
  LEX_LONG_NAME = True
  ML_PHISH_PROB_GE_0_9 = True

Rules fired:
  G01 → generic risk (new domain)
  L01 → phishing signal (ML model)

Decision:
  classification = suspicious
```

The reasoning chain becomes **transparent and reproducible**.

---

# Architecture Overview

The repository implements four layers:

```
Raw Features
    ↓
Atom Engine
    ↓
Rule Engine
    ↓
Reasoning LLM
    ↓
Human Explanation
```

### 1. Raw Feature Layer
Your existing dataset or feature extractor provides attributes such as:

- DNS features
- TLS features
- RDAP / WHOIS features
- lexical features
- infrastructure features
- ML model outputs

Example attributes:

```
dns_MX_count
rdap_domain_age
lex_name_len
tls_has_tls
ml_phish_prob
ml_malware_prob
```

These are **raw facts**.

---

# Atoms

Atoms are **atomic reasoning facts** derived from attributes.

Example:

```
rdap_domain_age = 45
→ RDAP_NEW_DOMAIN = True
```

or

```
ml_phish_prob = 0.93
→ ML_PHISH_PROB_GE_0_9 = True
```

Atoms represent **boolean reasoning primitives** used by the rule engine.

Two categories exist:

### Base atoms
Derived deterministically from raw features.

Examples:

```
RDAP_NEW_DOMAIN
DNS_NO_MX
LEX_LONG_NAME
TLS_SUSPICIOUS
```

These are produced by:

```
providers/base_thresholds_provider.py
```

---

### Learned atoms

Produced by machine learning models or statistical signals.

Examples:

```
ML_PHISH_PROB_GE_0_9
ML_MALWARE_PROB_GE_0_85
CAL_RISK_GE_0_7
```

These come from providers such as:

```
providers/ml_probs_provider.py
providers/risk_calibration_provider.py
```

Learned atoms represent **model evidence**, not ground truth.

---

# Atom Storage System

DRL‑Domain introduces two storage layers for atoms.

## Atom Definition Store

File:

```
atoms/atoms_registry.json
```

This file defines what each atom means.

Example entry:

```json
{
  "name": "ML_PHISH_PROB_GE_0_9",
  "type": "bool",
  "description": "ML phishing probability >= 0.90",
  "provider_id": "ml_probs",
  "provider_version": "1.0.0",
  "requires": ["ml_phish_prob"]
}
```

Purpose:

- governance
- versioning
- documentation
- validation

This file should be **version controlled**.

---

## Atom Value Store

Implemented in:

```
atom_store.py
```

This stores **computed atoms for domains** using SQLite.

Example record:

```
domain = example.com
provider = ml_probs@1.0.0
atom = ML_PHISH_PROB_GE_0_9
value = True
timestamp = ...
```

Purpose:

- avoid recomputing ML outputs
- caching expensive computations
- enabling historical reasoning

---

# Atom Providers (Plugin System)

Atoms are computed by **providers**.

Providers live in:

```
providers/
```

Each provider implements:

```
compute(domain, attributes) → atoms
```

Example provider metadata:

```
PROVIDER_ID
PROVIDER_VERSION
CACHEABLE
```

Providers allow **plug‑in reasoning signals**.

Examples:

### Base Threshold Provider

```
providers/base_thresholds_provider.py
```

Produces atoms from deterministic rules.

Example:

```
rdap_domain_age < 180
→ RDAP_NEW_DOMAIN
```

---

### ML Probability Provider

```
providers/ml_probs_provider.py
```

Uses model outputs to produce atoms.

Example:

```
ml_phish_prob >= 0.9
→ ML_PHISH_PROB_GE_0_9
```

---

### Risk Calibration Provider

```
providers/risk_calibration_provider.py
```

Uses calibrated risk scores.

Example:

```
cal_risk_score >= 0.7
→ CAL_RISK_GE_0_7
```

---

# Atom Engine

File:

```
atom_engine.py
```

The Atom Engine orchestrates the system.

Responsibilities:

- load providers
- compute atoms
- validate atoms against registry
- cache atoms in SQLite
- merge base and learned atoms

Example pipeline:

```python
from atom_engine import AtomEngine
from atom_store import AtomValueStore

engine = AtomEngine.load_default()
store = AtomValueStore("atoms_cache.sqlite")

atoms = engine.compute_atoms(
    domain="example.com",
    attributes=row_features,
    store=store
)
```

Output:

```
[
 {atom: RDAP_NEW_DOMAIN, value: True},
 {atom: ML_PHISH_PROB_GE_0_9, value: True}
]
```

---

# Rule Engine

File:

```
rule_engine_reference.py
```

Rules convert atoms into **evidence scores**.

Example rule:

```
IF RDAP_NEW_DOMAIN
THEN generic_risk +3
```

Example learned‑atom rule:

```
IF ML_PHISH_PROB_GE_0_9
THEN phishing +2
```

Rules produce:

```
SCORES:
 benign
 phishing
 malware
 generic_risk
```

The system then chooses the best classification.

---

# DRL Language

The reasoning output is written in **DRL (Domain Reasoning Language)**.

Example structure:

```
DRL/1.2

ENTITY: domain("example.com")

ATTRIBUTES:
 ...

ATOMS:
 ...

RULES_FIRED:
 ...

SCORES:
 ...

DECISION:
 ...

OUTPUT:
 ...
```

This format allows:

- explainable logs
- dataset generation
- LLM reasoning integration

---

# Reasoning LLM

The repository includes a **system prompt** for a reasoning model.

File:

```
drl_domain_system_prompt.txt
```

The LLM takes:

```
attributes
atoms
rules
```

and produces:

- structured reasoning
- human explanation

This enables **AI explainability for cybersecurity decisions**.

---

# Repository Structure

```
atoms/
    atoms_registry.json
    atoms_base.json
    atoms_learned_examples.json

providers/
    base_thresholds_provider.py
    ml_probs_provider.py
    risk_calibration_provider.py

examples/
    example_with_learned_atoms.drl

atom_engine.py
atom_store.py
rule_engine_reference.py

drl_domain_spec.md
drl_domain_system_prompt.txt

HOWTO_plug_atoms.md
README.md
```

---

# Typical Pipeline

```
Dataset / Feature Extractor
        ↓
Atom Engine
        ↓
Rule Engine
        ↓
Reasoning LLM
        ↓
Human Explanation
```

Example:

```
domain features → atoms → rules → classification → explanation
```

---

# Use Cases

DRL‑Domain can be used for:

- SOC alert triage
- explainable phishing detection
- malware infrastructure analysis
- dataset auditing
- ML model explainability
- research on neuro‑symbolic reasoning

---

# Version History

### v1.0
Initial DRL reasoning language.

### v1.1
Expanded rule library and example reasoning.

### v1.2
Major architecture update:

- Atom definition registry
- Atom value storage (SQLite)
- Provider plugin system
- Learned atom support

---

# Philosophy

DRL‑Domain is built on three principles:

### Explainability
Every decision must be traceable.

### Modularity
New reasoning signals should plug in easily.

### Neuro‑Symbolic Hybrid
Combine ML predictions with symbolic reasoning.

---

# License

MIT License
