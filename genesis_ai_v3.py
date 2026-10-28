import requests

print("=== GENESIS AI v0.3 ===")
print("Scrie 'exit' pentru a inchide programul.")

url = "http://127.0.0.1:11434/api/generate"

while True:
    intrebare = input("\nTu: ")

    if intrebare.lower() == "exit":
        print("GENESIS: La revedere!")
        break

    date = {
        "model": "qwen3:4b",
        "prompt": "/no_think\nRaspunde intotdeauna in limba romana, clar si concis.\n\nIntrebarea utilizatorului: " + intrebare,
        "stream": False,
        "think": False
    }

    try:
        raspuns = requests.post(url, json=date, timeout=120)
        raspuns.raise_for_status()

        rezultat = raspuns.json()
        text_ai = rezultat["response"]

        if "</think>" in text_ai:
            text_ai = text_ai.split("</think>", 1)[1].strip()

        print("\nGENESIS:", text_ai)

    except requests.exceptions.RequestException as eroare:
        print("Eroare de comunicare cu Ollama:", eroare)