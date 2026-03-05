from __future__ import annotations
import importlib.util
import os
from typing import Any, Dict, List, Optional

from atom_store import AtomDefinitionStore, AtomValueStore

class AtomEngine:
    """Runs atom providers (base + learned) and merges atoms with provenance."""

    def __init__(self, providers: List[Any], registry: Optional[AtomDefinitionStore] = None):
        self.providers = providers
        self.registry = registry

    @staticmethod
    def load_providers_from_folder(folder: str) -> List[Any]:
        providers = []
        for fn in sorted(os.listdir(folder)):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            path = os.path.join(folder, fn)
            mod_name = f"provider_{os.path.splitext(fn)[0]}"
            spec = importlib.util.spec_from_file_location(mod_name, path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore

            if hasattr(module, "get_provider"):
                providers.append(module.get_provider())
        return providers

    @classmethod
    def load_default(cls, base_dir: str = ".") -> "AtomEngine":
        providers_folder = os.path.join(base_dir, "providers")
        registry_path = os.path.join(base_dir, "atoms", "atoms_registry.json")
        registry = AtomDefinitionStore(registry_path).load()
        providers = cls.load_providers_from_folder(providers_folder)
        return cls(providers=providers, registry=registry)

    def compute_atoms(
        self,
        domain: str,
        attributes: Dict[str, Any],
        store: Optional[AtomValueStore] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []

        for p in self.providers:
            provider_key = f"{p.PROVIDER_ID}@{p.PROVIDER_VERSION}"

            # Cache path: for learned providers you can reuse cached values.
            if store is not None and use_cache and getattr(p, "CACHEABLE", False):
                cached = store.fetch(domain, provider_key=provider_key)
                if cached:
                    out.extend(cached)
                    continue

            atoms = p.compute(domain=domain, attributes=attributes)

            # Optional registry validation for governance (can disable for prototyping)
            if self.registry is not None and getattr(p, "VALIDATE_WITH_REGISTRY", True):
                for a in atoms:
                    # validate only atom name exists; skip in early dev if needed
                    self.registry.validate_atom(type("Tmp", (), {"atom": a["atom"]}))

            out.extend(atoms)

            if store is not None and getattr(p, "CACHEABLE", False):
                store.upsert(domain, provider_key=provider_key, atoms=atoms)

        return out
