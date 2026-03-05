# HOWTO — store learned atoms & plug them into DRL

## A) Add a learned-atom provider

1) Create `providers/ml_probs_provider.py` (example included).
2) Decide what inputs it needs:
   - Option 1: model outputs already present in ATTRIBUTES (e.g., `ml_phish_prob`)
   - Option 2: provider loads a model and computes outputs from features
3) Convert model outputs into **atoms** using thresholds.
4) Return atoms with provenance: `from: learned:<provider_id>@<version>`.

## B) Register the atoms (definition storage)

Edit `atoms/atoms_registry.json`:
- add each learned atom with:
  - `name`, `type`, `description`
  - `provider_id`, `provider_version`
  - `params` (e.g., threshold 0.9)
  - `requires` (required attributes)

This is important for governance & audit.

## C) Persist computed atoms (value storage)

Use `AtomValueStore` (SQLite):
- `store.upsert(domain, provider_key, atoms)`
- `store.fetch(domain)` to reuse cached atoms

This lets you:
- compute learned atoms once during ingestion
- reuse them for repeated reasoning prompts without running models again

## D) Plug atoms into reasoning

Pipeline:
1) Collect raw features → ATTRIBUTES
2) AtomEngine:
   - base atoms (threshold)
   - learned atoms (providers)
   - optional cache
3) Pass ATOMS into the LLM prompt
4) Run rules (symbolic) using the combined atom dict

## E) Minimal integration snippet

```python
from atom_engine import AtomEngine
from atom_store import AtomValueStore

engine = AtomEngine.load_default()
store = AtomValueStore("atoms_cache.sqlite")

domain = row["domain"]
attributes = row.to_dict()

atoms = engine.compute_atoms(domain, attributes, store=store, use_cache=True)

# Now build DRL input:
# - ATTRIBUTES: attributes
# - ATOMS: atoms (with provenance)
```
