import json
import requests
from genesis_commands import este_comanda, executa_comanda


print("=== GENESIS AI v1.6 ===")
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
    with open(
        fisier_memorie_lunga,
        "w",
        encoding="utf-8"
    ) as fisier:
        json.dump(
            memorie,
            fisier,
            ensure_ascii=False,
            indent=4
        )

def salveaza_istoricul(istoric):
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


# ==========================================
# PROPUNEREA UNEI MODIFICARI
# ==========================================

def propune_modificare(memorie, cheie, valoare):

    if cheie not in memorie:
        print("GENESIS: Aceasta informatie nu exista in memorie.")
        return

    if not isinstance(valoare, str) or not valoare.strip():
        print("GENESIS: Valoarea propusa nu este valida.")
        return

    valoare = valoare.strip()
    valoare_veche = memorie[cheie]

    print("\nGENESIS: Valoare veche:", valoare_veche)
    print("GENESIS: Valoare noua:", valoare)

    confirmare = input(
        "GENESIS: Confirmi modificarea? (da/nu): "
    )

    if confirmare.strip().lower() != "da":
        print("GENESIS: Modificarea a fost anulata.")
        return

    memorie[cheie] = valoare

    try:
        salveaza_memoria(memorie)
        print("GENESIS: Memoria permanenta a fost actualizata!")

    except OSError as eroare:
        memorie[cheie] = valoare_veche
        print("GENESIS: Eroare la salvarea memoriei:", eroare)


# ==========================================
# INTERPRETAREA CERERILOR DE MEMORARE
# ==========================================

def interpreteaza_memorarea(text, memorie):

    chei_permise = list(memorie.keys())

    instructiuni = f"""
Esti un analizor de cereri de memorare.

Analizeaza mesajul utilizatorului si stabileste daca
acesta cere EXPLICIT modificarea memoriei permanente.

Chei permise: {json.dumps(chei_permise, ensure_ascii=False)}

Returneaza DOAR un obiect JSON cu aceste campuri:
- actiune
- cheie
- valoare

Pentru o cerere clara de memorare:
{{
    "actiune": "actualizare_memorie",
    "cheie": "proiect",
    "valoare": "EXEMPLU"
}}

Pentru un mesaj obisnuit sau o cerere neclara:
{{
    "actiune": "nimic",
    "cheie": "",
    "valoare": ""
}}

REGULI:
- Nu inventa informatii.
- Nu modifica memoria.
- Nu interpreta o intrebare ca pe o cerere de memorare.
- Foloseste doar cheile permise.
- Daca nu exista o cerere explicita, actiunea este "nimic".
"""

    date = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": instructiuni
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "stream": False,
        "think": False,
        "format": "json"
    }

    raspuns = requests.post(
        url,
        json=date,
        timeout=120
    )

    raspuns.raise_for_status()

    rezultat = raspuns.json()

    text_json = rezultat["message"]["content"]

    analiza = json.loads(text_json)

    if not isinstance(analiza, dict):
        return None

    if analiza.get("actiune") != "actualizare_memorie":
        return None

    cheie = analiza.get("cheie")
    valoare = analiza.get("valoare")

    if not isinstance(cheie, str):
        return None

    if not isinstance(valoare, str):
        return None

    if cheie not in memorie:
        return None

    if not valoare.strip():
        return None

    return {
        "cheie": cheie,
        "valoare": valoare.strip()
    }


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
