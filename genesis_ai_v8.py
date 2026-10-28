import json
import requests

print("=== GENESIS AI v0.8 ===")
print("Scrie 'exit' pentru a inchide programul.")
print("Scrie '/memory' pentru a vedea memoria permanenta.")
print("Scrie '/set cheie valoare' pentru a modifica memoria.")

url = "http://127.0.0.1:11434/api/chat"

fisier_memorie = "genesis_memory.json"
fisier_memorie_lunga = "genesis_long_memory.json"


# ==========================================
# FUNCTIE: CONSTRUIM INSTRUCTIUNILE PENTRU AI
# ==========================================

def construieste_instructiuni(memorie):
    instructiuni = f"""
Esti GENESIS, un asistent AI local.
Raspunde intotdeauna in limba romana, clar si concis.

MEMORIE PE TERMEN LUNG:
Nume: {memorie.get("nume", "Necunoscut")}
Limba preferata: {memorie.get("limba_preferata", "romana")}
Proiect: {memorie.get("proiect", "Necunoscut")}

REGULA IMPORTANTA:
Cand informatiile din istoricul vechi contrazic memoria pe termen lung,
foloseste informatiile confirmate din memoria pe termen lung.

Daca utilizatorul doreste modificarea memoriei permanente,
explica-i ca poate folosi comanda /set.
Nu pretinde ca ai salvat o informatie daca programul nu a salvat-o.
"""
    return instructiuni


# ==========================================
# INCARCAM MEMORIA PE TERMEN LUNG
# ==========================================

try:
    with open(fisier_memorie_lunga, "r", encoding="utf-8") as fisier:
        memorie_lunga = json.load(fisier)

    print("Memoria pe termen lung a fost incarcata!")

except FileNotFoundError:
    memorie_lunga = {
        "nume": "Necunoscut",
        "limba_preferata": "romana",
        "proiect": "Necunoscut"
    }

    print("Nu exista memorie pe termen lung.")
    print("Am creat o memorie initiala in RAM.")


# ==========================================
# INCARCAM ISTORICUL CONVERSATIEI
# ==========================================

try:
    with open(fisier_memorie, "r", encoding="utf-8") as fisier:
        istoric = json.load(fisier)

    print("Istoricul conversatiei a fost incarcat!")

except FileNotFoundError:
    istoric = []

    print("Nu exista istoric. Pornim o conversatie noua.")


# ==========================================
# PORNIM CONVERSATIA
# ==========================================

while True:

    intrebare = input("\nTu: ").strip()

    # --------------------------------------
    # COMANDA EXIT
    # --------------------------------------

    if intrebare.lower() == "exit":
        print("GENESIS: La revedere!")
        break

    # --------------------------------------
    # COMANDA /MEMORY
    # --------------------------------------

    if intrebare == "/memory":

        print("\n=== MEMORIE PERMANENTA ===")

        for cheie, valoare in memorie_lunga.items():
            print(f"{cheie}: {valoare}")

        continue

    # --------------------------------------
    # COMANDA /SET
    # --------------------------------------

    if intrebare == "/set" or intrebare.startswith("/set "):

        parti = intrebare.split(maxsplit=2)

        if len(parti) != 3:
            print("GENESIS: Format corect: /set cheie valoare")
            continue

        cheie = parti[1]
        valoare = parti[2]

        if cheie not in memorie_lunga:
            print("GENESIS: Aceasta informatie nu exista in memorie.")
            continue

        valoare_veche = memorie_lunga[cheie]

        print("\nGENESIS: Valoare veche:", valoare_veche)
        print("GENESIS: Valoare noua:", valoare)

        confirmare = input(
            "GENESIS: Confirmi modificarea? (da/nu): "
        )

        if confirmare.strip().lower() == "da":

            memorie_lunga[cheie] = valoare

            try:
                with open(
                    fisier_memorie_lunga,
                    "w",
                    encoding="utf-8"
                ) as fisier:

                    json.dump(
                        memorie_lunga,
                        fisier,
                        ensure_ascii=False,
                        indent=4
                    )

                print("GENESIS: Memoria permanenta a fost actualizata!")

            except OSError as eroare:
                memorie_lunga[cheie] = valoare_veche
                print("GENESIS: Eroare la salvarea memoriei:", eroare)

        else:
            print("GENESIS: Modificarea a fost anulata.")

        continue

    # --------------------------------------
    # CONVERSATIE NORMALA CU OLLAMA
    # --------------------------------------

    istoric.append({
        "role": "user",
        "content": intrebare
    })

    # Reconstruim instructiunile la fiecare intrebare.
    # Astfel, AI foloseste memoria actualizata.

    instructiuni = construieste_instructiuni(memorie_lunga)

    # Pastram mesajul system si ultimele 10 mesaje
    # din conversatie.

    mesaje_conversatie = [
        mesaj for mesaj in istoric
        if mesaj["role"] != "system"
    ]

    context = [
        {
            "role": "system",
            "content": instructiuni
        }
    ] + mesaje_conversatie[-10:]

    date = {
        "model": "qwen3:4b",
        "messages": context,
        "stream": False,
        "think": False
    }

    try:

        raspuns = requests.post(
            url,
            json=date,
            timeout=120
        )

        raspuns.raise_for_status()

        rezultat = raspuns.json()

        text_ai = rezultat["message"]["content"]

        if "</think>" in text_ai:
            text_ai = text_ai.split("</think>", 1)[1].strip()

        print("\nGENESIS:", text_ai)

        # Salvam raspunsul AI in istoric

        istoric.append({
            "role": "assistant",
            "content": text_ai
        })

        # Salvam istoricul conversatiei

        with open(
            fisier_memorie,
            "w",
            encoding="utf-8"
        ) as fisier:

            json.dump(
                istoric,
                fisier,
                ensure_ascii=False,
                indent=4
            )

    except requests.exceptions.RequestException as eroare:
        print("GENESIS: Eroare de comunicare cu Ollama:", eroare)

    except (KeyError, ValueError) as eroare:
        print("GENESIS: Eroare la procesarea raspunsului:", eroare)

    except OSError as eroare:
        print("GENESIS: Eroare la salvarea istoricului:", eroare)
