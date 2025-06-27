#!/usr/bin/env python3
import json
import sys
import argparse
import requests
from typing import Optional

# --------------------------------------------------------------------------------------------------
# Usage:
#   loader.py --json path/to/file.json --topic "Physical Terms" --info "Термины по физике"
# --------------------------------------------------------------------------------------------------

BASE_URL = "http://localhost:8000"  # adjust if your API lives elsewhere

def load_entries(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        sys.exit(1)

def create_topic(name: str, info: Optional[str]) -> str:
    payload = {"name": name}
    if info:
        payload["info"] = info
    r = requests.post(f"{BASE_URL}/topics", json=payload)
    r.raise_for_status()
    tid = r.json().get("id")
    print(f"→ created topic '{name}' with id {tid}")
    return tid

def create_term(topic_id: str, lang: str, raw_text: str) -> Optional[str]:
    payload = {
        "topic_id": topic_id,
        "language": lang,
        "raw_text": raw_text,
    }
    r = requests.post(f"{BASE_URL}/terms", json=payload)
    if not r.ok:
        print(f"[{lang}] term error '{raw_text}': {r.status_code} {r.text}", file=sys.stderr)
        return None
    return r.json().get("id")

def create_description(term_id: str, raw_text: str) -> None:
    payload = {"term_id": term_id, "raw_text": raw_text}
    r = requests.post(f"{BASE_URL}/descriptions", json=payload)
    if not r.ok:
        print(f" desc error for term_id={term_id}: {r.status_code} {r.text}", file=sys.stderr)

def main():
    p = argparse.ArgumentParser(description="Load terms/descriptions from JSON into your API")
    p.add_argument("--json",    required=True, help="Path to JSON file")
    p.add_argument("--topic",   required=True, help="Topic name")
    p.add_argument("--info",    default=None, help="Optional topic info")
    args = p.parse_args()

    entries = load_entries(args.json)
    topic_id = create_topic(args.topic, args.info)

    for e in entries:
        # Russian: translation → definition
        ru_term = e.get("translation", "").strip()
        ru_def  = e.get("definition", "").strip()
        if ru_term and ru_def:
            tid = create_term(topic_id, "russian", ru_term)
            if tid:
                create_description(tid, ru_def)

        # English: term → definition_translated
        en_term = e.get("term", "").strip()
        en_def  = e.get("definition_translated", "").strip()
        if en_term and en_def:
            tid = create_term(topic_id, "english", en_term)
            if tid:
                create_description(tid, en_def)

    print("Done loading", args.json)

if __name__ == "__main__":
    main()
