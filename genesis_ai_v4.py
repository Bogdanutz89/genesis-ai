import requests

print("=== GENESIS AI v0.4 ===")
print("Scrie 'exit' pentru a inchide programul.")

url = "http://127.0.0.1:11434/api/chat"

istoric = [
    {
        "role": "system",
        "content": "Raspunde intotdeauna in limba romana, clar si concis."
    }
]

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

    except requests.exceptions.RequestException as eroare:
        print("Eroare de comunicare cu Ollama:", eroare)