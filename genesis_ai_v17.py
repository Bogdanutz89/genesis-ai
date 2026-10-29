import json
import requests
import genesis_memory
from genesis_commands import este_comanda, executa_comanda


print("=== GENESIS AI v1.7 ===")
print("Scrie 'exit' pentru a inchide programul.")
print("Scrie '/memory' pentru a vedea memoria permanenta.")
print("Scrie '/set cheie valoare' pentru a modifica memoria.")
print("Poti spune si: Tine minte ca proiectul meu se numeste ...")


url = "http://127.0.0.1:11434/api/chat"

fisier_memorie = "genesis_memory.json"
fisier_memorie_lunga = "genesis_long_memory.json"

model = "qwen3:4b"


# ==========================================
# INSTRUCTIUNI PENTRU GENESIS
# ==========================================

def construieste_instructiuni(memorie):
    return f"""
Esti GENESIS, un asistent AI local.
Raspunde intotdeauna in limba romana, clar si concis.

MEMORIE PE TERMEN LUNG:
Nume: {memorie.get("nume", "Necunoscut")}
Limba preferata: {memorie.get("limba_preferata", "romana")}
Proiect: {memorie.get("proiect", "Necunoscut")}

REGULA IMPORTANTA:
Memoria permanenta contine informatiile confirmate.
Daca istoricul contrazice memoria permanenta,
foloseste memoria permanenta.

Nu pretinde ca ai modificat memoria daca Python
nu a confirmat salvarea.
"""


# ==========================================
# SALVAREA MEMORIEI PERMANENTE
# ==========================================

def salveaza_memoria(memorie):
    genesis_memory.salveaza_memoria(memorie, fisier_memorie_lunga)

def salveaza_istoricul(istoric):
    genesis_memory.salveaza_istoricul(istoric, fisier_memorie)


# ==========================================
# PROPUNEREA UNEI MODIFICARI
# ==========================================

def propune_modificare(memorie, cheie, valoare):
    genesis_memory.propune_modificare(
        memorie,
        cheie,
        valoare,
        fisier_memorie_lunga
    )


# ==========================================
# INTERPRETAREA CERERILOR DE MEMORARE
# ==========================================

def interpreteaza_memorarea(text, memorie):
    return genesis_memory.interpreteaza_memorarea(
        text,
        memorie,
        model,
        url
    )



# ==========================================
# SISTEMUL DE COMENZI - NOU IN v1.0
# ==========================================



# ==========================================
# INCARCAREA MEMORIEI PERMANENTE
# ==========================================

try:
    with open(
        fisier_memorie_lunga,
        "r",
        encoding="utf-8"
    ) as fisier:

        memorie_lunga = json.load(fisier)

    print("Memoria pe termen lung a fost incarcata!")

except FileNotFoundError:

    memorie_lunga = {
        "nume": "Necunoscut",
        "limba_preferata": "romana",
        "proiect": "Necunoscut"
    }

    print("Nu exista memorie permanenta.")
    print("Am creat memoria initiala in RAM.")


# ==========================================
# INCARCAREA ISTORICULUI
# ==========================================

try:
    with open(
        fisier_memorie,
        "r",
        encoding="utf-8"
    ) as fisier:

        istoric = json.load(fisier)

    if istoric:
        print("Istoricul conversatiei a fost incarcat!")
    else:
        print("Istoricul este gol. Pornim o conversatie noua.")

except FileNotFoundError:

    istoric = []

    print("Nu exista istoric. Pornim o conversatie noua.")


# ==========================================
# BUCLEA PRINCIPALA
# ==========================================

while True:

    intrebare = input("\nTu: ").strip()

    # EXIT
    if intrebare.lower() == "exit":
        print("GENESIS: La revedere!")
        break

    # IGNORAM MESAJELE GOALE
    if not intrebare:
        continue

    # COMENZI
    if este_comanda(intrebare):

        if executa_comanda(intrebare, memorie_lunga,istoric,model,fisier_memorie,propune_modificare,salveaza_istoricul,salveaza_memoria):
            continue

    # INTERPRETARE MEMORIE NATURALA
    try:
        propunere = interpreteaza_memorarea(
            intrebare,
            memorie_lunga
        )

        if propunere is not None:

            propune_modificare(
                memorie_lunga,
                propunere["cheie"],
                propunere["valoare"]
            )

            continue

    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        TypeError
    ) as eroare:

        print(
            "GENESIS: Nu am putut analiza cererea de memorare:",
            eroare
        )

    # ADAUGAM MESAJUL UTILIZATORULUI IN ISTORIC
    istoric.append({
        "role": "user",
        "content": intrebare
    })

    # CONSTRUIM INSTRUCTIUNILE
    instructiuni = construieste_instructiuni(memorie_lunga)

    # ELIMINAM VECHILE MESAJE SYSTEM
    mesaje_conversatie = [
        mesaj
        for mesaj in istoric
        if mesaj["role"] != "system"
    ]

    # PASTRAM ULTIMELE 10 MESAJE
    context = [
        {
            "role": "system",
            "content": instructiuni
        }
    ] + mesaje_conversatie[-10:]

    # CERERE CATRE OLLAMA
    date = {
        "model": model,
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

        # ELIMINAM EVENTUALUL TEXT DE GANDIRE
        if "</think>" in text_ai:
            text_ai = text_ai.split("</think>", 1)[1].strip()

        print("\nGENESIS:", text_ai)

        # ADAUGAM RASPUNSUL IN ISTORIC
        istoric.append({
            "role": "assistant",
            "content": text_ai
        })

        # SALVAM ISTORICUL
        salveaza_istoricul(istoric)

    except requests.exceptions.RequestException as eroare:
        print("GENESIS: Eroare de comunicare cu Ollama:", eroare)

    except (KeyError, ValueError) as eroare:
        print("GENESIS: Eroare la procesarea raspunsului:", eroare)

    except OSError as eroare:
        print("GENESIS: Eroare la salvarea istoricului:", eroare)
