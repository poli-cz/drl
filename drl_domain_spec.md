# DRL-Domain v1.2 (DRL/1.2)

v1.2 adds a **standard storage format for atoms** and a **plug-in interface** for learned atoms.

## Two kinds of storage

### 1) Atom Definition Store (registry)
Stores *what an atom means*:
- name, type, description
- provider id + provider version
- parameters (thresholds, model name, calibration)
- expected inputs (which attributes are required)

File: `atoms/atoms_registry.json` (authoritative)

### 2) Atom Value Store (cache)
Stores computed atoms per entity:
- entity key (domain)
- timestamp
- provider_id@version
- atom_name → value
- optional confidence/probability + explanation

Implementation: `AtomValueStore` in `atom_store.py` uses SQLite (built-in).

## Plug-in providers

A provider is a Python module in `providers/` that exposes:

- `PROVIDER_ID` (string)
- `PROVIDER_VERSION` (string)
- `required_attributes()` → set[str]
- `compute(domain: str, attributes: dict) -> list[Atom]`

Where `Atom` is a dict:
- atom (str)
- value (bool|int|float|str)
- from (e.g., learned:ml_phish@1.0.0)
- note (short)

Providers are loaded by `AtomEngine` from `atom_engine.py`.

## How rules use learned atoms

Rules can reference learned atoms exactly like base atoms, e.g.:
- if `ML_PHISH_PROB_GE_0_9` and `DNS_NO_MX` -> phishing +2

But:
- keep weights moderate (1–3) unless the learned atom is well-calibrated & validated
- log conflicts: strong benign atoms + strong learned phishing atoms → confidence drop

## Recommended convention for learned atom naming

Use deterministic names:
- `ML_PHISH_PROB_GE_0_9`
- `ML_MALWARE_PROB_GE_0_85`
- `CAL_RISK_GE_0_7`
- `EMB_CLUSTER_ID_12` + `EMB_CLUSTER_IS_PHISHING`

This makes atoms stable and easy to query.
