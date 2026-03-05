import argparse
import pandas as pd
from tqdm import tqdm
import json

from gpt_reasoner import GPTReasoner
from metrics import compute_metrics

import re


def detect_domain_column(df):
    # 1) common names
    candidates = [
        "fqdn",
        "domain_name",
        "hostname",
        "host",
        "qname",
        "name",
        "sld",
        "domain_sld",
        "registered_domain",
    ]
    for c in candidates:
        if c in df.columns:
            return c

    # 2) heuristic: string column where most rows contain a dot and no spaces
    best_col = None
    best_score = -1

    for c in df.columns:
        if df[c].dtype != "object":
            continue
        s = df[c].dropna().astype(str).head(200)
        if len(s) == 0:
            continue

        score = 0
        for v in s:
            v = v.strip()
            if " " in v:
                continue
            if "." in v and len(v) >= 4:
                score += 1

        if score > best_score:
            best_score = score
            best_col = c

    if best_col is None:
        raise ValueError(f"Could not detect domain column. Columns: {list(df.columns)}")

    return best_col


def build_prompt(row):

    # print all columns and values for debugging

    prompt = f"""
        Analyze the following domain attributes and decide if the domain is benign, phishing, or malware.

        Domain: {row['domain_name']}

        Attributes:
        rdap_domain_age = {row.get('rdap_domain_age')}
        dns_MX_count = {row.get('dns_MX_count')}
        dns_NS_count = {row.get('dns_NS_count')}
        tls_has_tls = {row.get('tls_has_tls')}
        lex_name_len = {row.get('lex_name_len')}
        ml_phish_prob = {row.get('ml_phish_prob')}
        ml_malware_prob = {row.get('ml_malware_prob')}

        Return predicted_label and confidence.
        """

    return prompt


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--output", default="results.json")

    args = parser.parse_args()

    df = pd.read_parquet(args.dataset)

    reasoner = GPTReasoner(args.model)

    results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):

        prompt = build_prompt(row)

        reasoning = reasoner.reason(prompt)

        # naive parse
        predicted = "unknown"
        if "phishing" in reasoning.lower():
            predicted = "phishing"
        elif "malware" in reasoning.lower():
            predicted = "malware"
        elif "benign" in reasoning.lower():
            predicted = "benign"

        results.append(
            {
                "domain": row["domain_name"],
                "true_label": row.get("label"),
                "predicted_label": predicted,
                "reasoning": reasoning,
            }
        )

        print(results[-1])

    metrics = compute_metrics(results)

    with open(args.output, "w") as f:
        json.dump({"metrics": metrics, "results": results}, f, indent=2)


if __name__ == "__main__":
    main()
