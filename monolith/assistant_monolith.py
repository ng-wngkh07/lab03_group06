import csv
import json
import os
import random
import re
import sys

# Smell 1: Hard-coded secret
API_KEY = "sk-test-2b7c1d9e4f0a"

# Smell 2: Configuration mixed with code
MODEL = "gpt-small"
DEBUG = True
RATE = 450000
RETAKE_RATE = 1.5
MAX_CREDITS = 30

# Smell 3: Global mutable state
history = []
offices = {}
handbook = []

# Smell 9: Paths built with string +
BASE = os.path.dirname(os.path.abspath(__file__))


def load():
    global offices, handbook
    try:
        # Smell 9
        with open(BASE + "/data/offices.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                offices[row["name"].lower()] = row
    except:
        # Smell 4: Bare except
        print("Warning: could not load offices")

    try:
        # Smell 9
        with open(BASE + "/data/handbook.json", "r", encoding="utf-8") as f:
            handbook = json.load(f)
    except:
        # Smell 4: Bare except
        print("Warning: could not load handbook")


# Smell 10: Non-deterministic behaviour with random.random()
def llm(prompt):
    if DEBUG:
        # Smell 1 & 7: Leaking key in debug output with print
        print(f"[debug] calling {MODEL} with key {API_KEY} prompt: {prompt[:35]}...")
    if random.random() < 0.05:
        return None
    return f"Here is what I found: ... (source: H26-5.3)"


# Smell 5: One function does everything (~65 lines)
# Smell 6: Magic strings / return values ("empty", "saved", "too many credits")
def handle(text):
    global history
    if not text:
        return "empty"

    t = text.lower().strip()
    if t in ["hi", "hello", "hey", "xin chao"]:
        return "Hello! I can help with offices, fees and rules."

    if "fee" in t or "tuition" in t:
        retake_match = re.search(r"(\d+)\s*retake", t)
        numbers = [int(n) for n in re.findall(r"\d+", t)]
        retake_n = int(retake_match.group(1)) if retake_match else 0
        others = list(numbers)
        if retake_match:
            others.remove(retake_n)
        if not others:
            return "How many credits?"
        credits = others[0]
        if credits > MAX_CREDITS or credits < 1:
            return "too many credits"
        cost = int(credits * RATE + retake_n * RATE * RETAKE_RATE)
        return f"Your tuition is {cost} VND"

    for name, info in offices.items():
        if name in t:
            return f"{info['name']}: room {info['room']}, open {info['hours']}"

    matched_rule = None
    for rule in handbook:
        words = set(re.findall(r"\w+", t))
        keywords = set([k.lower() for k in rule.get("keywords", [])])
        if words & keywords:
            matched_rule = rule
            break

    if matched_rule:
        prompt = f"Answer using this rule: {matched_rule['text']}"
        res = llm(prompt)
        if res:
            history.append((text, res))
            return res
        return f"Fallback: {matched_rule['title']}: {matched_rule['text']}"

    return "Sorry, I don't know that yet."


# Smell 8: Hand-made tests that print
def test():
    load()
    print(handle("hi"))
    print(handle("tuition for 18 credits and 2 retake"))
    print(handle("where is the library"))
    print(handle("thesis registration credits"))
    print(handle("tuition for 35 credits"))
    print(handle(""))


def main():
    try:
        load()
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            test()
            return
        if len(sys.argv) > 1:
            print(handle(" ".join(sys.argv[1:])))
        else:
            print("Usage: python assistant_monolith.py <query>")
    except:
        # Smell 4: Bare except
        pass


if __name__ == "__main__":
    main()
