import requests

print("=== GENESIS AI v0.1 ===")

url = "http://127.0.0.1:11434/api/generate"

date = {
    "model": "qwen3:4b",
    "prompt": "Salut! Prezinta-te in limba romana, in maximum doua propozitii.",
    "stream": False,
    "think": False
}

try:
    raspuns = requests.post(url, json=date, timeout=120)
    raspuns.raise_for_status()

    rezultat = raspuns.json()

    print("AI:", rezultat["response"])

except requests.exceptions.RequestException as eroare:
    print("Eroare de comunicare cu Ollama:", eroare)