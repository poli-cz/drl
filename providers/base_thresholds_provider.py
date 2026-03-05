from __future__ import annotations
from typing import Any, Dict, List

class BaseThresholdProvider:
    PROVIDER_ID = "base_thresholds"
    PROVIDER_VERSION = "1.2.0"
    CACHEABLE = False
    VALIDATE_WITH_REGISTRY = True

    def compute(self, domain: str, attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
        a = attributes
        atoms: List[Dict[str, Any]] = []

        def add(name: str, value: Any, note: str):
            atoms.append({"atom": name, "value": value, "from": f"derived:{self.PROVIDER_ID}@{self.PROVIDER_VERSION}", "note": note})

        # RDAP
        age = a.get("rdap_domain_age")
        if age is not None:
            try:
                age = float(age)
                add("RDAP_NEW_DOMAIN", age < 180, "rdap_domain_age < 180")
                add("RDAP_YOUNG_DOMAIN", age < 365, "rdap_domain_age < 365")
                add("RDAP_OLD_DOMAIN", age >= 1825, "rdap_domain_age >= 1825")
            except Exception:
                pass

        # DNS
        mx = int(a.get("dns_MX_count", 0) or 0)
        ns = int(a.get("dns_NS_count", 0) or 0)
        add("DNS_NO_MX", mx == 0, "dns_MX_count == 0")
        add("DNS_HAS_MX", mx > 0, "dns_MX_count > 0")
        add("DNS_NS_OK", ns >= 2, "dns_NS_count >= 2")

        # TLS
        tls = bool(a.get("tls_has_tls", False))
        self_signed = float(a.get("tls_is_self_signed", 0) or 0)
        expired = float(a.get("tls_expired_chain", 0) or 0)
        add("TLS_PRESENT", tls, "tls_has_tls == True")
        add("TLS_SUSPICIOUS", bool((tls and (self_signed > 0 or expired > 0))), "expired/self-signed TLS")

        # Lexical
        name_len = int(a.get("lex_name_len", 0) or 0)
        add("LEX_LONG_NAME", name_len >= 30, "lex_name_len >= 30")

        return atoms

def get_provider():
    return BaseThresholdProvider()
