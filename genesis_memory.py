import json
import requests


def salveaza_memoria(memorie, fisier_memorie_lunga):
    with open(fisier_memorie_lunga, "w", encoding="utf-8") as fisier:
        json.dump(memorie, fisier, ensure_ascii=False, indent=4)


def salveaza_istoricul(istoric, fisier_memorie):
    with open(fisier_memorie, "w", encoding="utf-8") as fisier:
        json.dump(istoric, fisier, ensure_ascii=False, indent=4)

def propune_modificare(memorie, cheie, valoare, fisier_memorie_lunga):

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
        salveaza_memoria(memorie, fisier_memorie_lunga)
        print("GENESIS: Memoria permanenta a fost actualizata!")

    except OSError as eroare:
        memorie[cheie] = valoare_veche
        print("GENESIS: Eroare la salvarea memoriei:", eroare)

def interpreteaza_memorarea(text, memorie,model,url):

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
