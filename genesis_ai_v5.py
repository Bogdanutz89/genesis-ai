import json
import requests

print("=== GENESIS AI v0.5 ===")
print("Scrie 'exit' pentru a inchide programul.")

url = "http://127.0.0.1:11434/api/chat"
fisier_memorie = "genesis_memory.json"

# Incarcam istoricul daca exista deja
try:
    with open(fisier_memorie, "r", encoding="utf-8") as fisier:
        istoric = json.load(fisier)

    print("Memoria anterioara a fost incarcata!")

except FileNotFoundError:
    istoric = [
        {
            "role": "system",
            "content": "Raspunde intotdeauna in limba romana, clar si concis."
        }
    ]

    print("Nu exista memorie salvata. Pornim o conversatie noua.")

# Pornim conversatia
while True:
    intrebare = input("\nTu: ")

    if intrebare.lower() == "exit":
        print("GENESIS: La revedere!")
        break

    istoric.append({
        "role": "user",
        "content": intrebare
    })

    date = {
        "model": "qwen3:4b",
        "messages": istoric,
        "stream": False,
        "think": False
    }

    try:
        raspuns = requests.post(url, json=date, timeout=120)
        raspuns.raise_for_status()

        rezultat = raspuns.json()
        text_ai = rezultat["message"]["content"]

        if "</think>" in text_ai:
            text_ai = text_ai.split("</think>", 1)[1].strip()

        print("\nGENESIS:", text_ai)

        istoric.append({
            "role": "assistant",
            "content": text_ai
        })

        # Salvam conversatia actualizata
        with open(fisier_memorie, "w", encoding="utf-8") as fisier:
            json.dump(istoric, fisier, ensure_ascii=False, indent=4)

    except requests.exceptions.RequestException as eroare:
        print("Eroare de comunicare cu Ollama:", eroare)