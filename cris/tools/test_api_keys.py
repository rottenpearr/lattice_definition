"""Quick test for MP and Anthropic API keys."""
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root regardless of cwd
load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

import os
import requests
import anthropic

# Test Materials Project
key = os.getenv("MP_API_KEY")
print(f"MP key: {key[:8]}..." if key else "MP key: NOT FOUND")
try:
    resp = requests.get(
        "https://api.materialsproject.org/materials/summary/?formula=NaCl&_limit=1",
        headers={"X-API-KEY": key},
        timeout=15,
    )
    print(f"MP status: {resp.status_code}")
    data = resp.json()
    items = data.get("data", [])
    print(f"MP data: {items[:1]}")
except Exception as e:
    print(f"MP error: {e}")

# Test Anthropic
ant_key = os.getenv("ANTHROPIC_API_KEY")
print(f"Anthropic key: {ant_key[:15]}..." if ant_key else "Anthropic key: NOT FOUND")
try:
    client = anthropic.Anthropic(api_key=ant_key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20,
        messages=[{"role": "user", "content": "Say OK"}],
    )
    print(f"Anthropic: {msg.content[0].text}")
except Exception as e:
    print(f"Anthropic error: {e}")
