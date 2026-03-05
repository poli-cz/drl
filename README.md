# DRL-Domain v1.2 — learned-atoms storage + plug-in interface

This pack extends DRL-Domain with:
- **Atom definition storage** (what atoms mean, where they come from, parameters, versioning).
- **Atom value storage** (optional cache of computed atoms per domain to avoid recomputation).
- **Provider plug-in interface** to add *learned atoms* (e.g., ML model scores → boolean atoms).

Generated: 2026-03-05

## Quick start (concept)
1. Start with a feature row for a domain (your existing CSV/parquet features).
2. Run `AtomEngine`:
   - Base/handcrafted atoms (thresholds)
   - Learned atoms from plug-in providers (models/heuristics)
   - Optionally cache results in `AtomValueStore` (SQLite)
3. Feed `ATTRIBUTES` + `ATOMIZATION` into the Reasoning LLM prompt (DRL/1.2).
4. Fire rules using the combined atom set.

## Files
- `drl_domain_system_prompt.txt` — DRL/1.2 prompt with learned-atom conventions
- `drl_domain_spec.md` — DSL spec + storage & plugin conventions
- `atoms/atoms_registry.json` — canonical atom definitions + provenance (editable)
- `atoms/atoms_base.json` — base atoms shipped with DRL (threshold-derived)
- `atoms/atoms_learned_examples.json` — example learned atoms (probability thresholds etc.)
- `atom_store.py` — AtomValueStore (SQLite cache) + AtomDefinitionStore
- `atom_engine.py` — AtomEngine that runs providers and merges atoms
- `providers/` — plug-in providers (base + learned examples)
- `rule_engine_reference.py` — reference rule engine updated to accept external atoms
- `HOWTO_plug_atoms.md` — step-by-step integration guide

> Tip: treat *learned atoms* as a stable interface between ML outputs and symbolic rules.
