import json
import requests


def salveaza_memoria(memorie, fisier_memorie_lunga):
    with open(fisier_memorie_lunga, "w", encoding="utf-8") as fisier:
        json.dump(memorie, fisier, ensure_ascii=False, indent=4)


def salveaza_istoricul(istoric, fisier_memorie):
    with open(fisier_memorie, "w", encoding="utf-8") as fisier:
        json.dump(istoric, fisier, ensure_ascii=False, indent=4)

def propune_modificare(memorie, cheie, valoare, fisier_memorie_lunga):


    if not isinstance(valoare, str) or not valoare.strip():
        print("GENESIS: Valoarea propusa nu este valida.")
        return

    valoare = valoare.strip()
    valoare_veche = memorie.get(cheie)

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
        if valoare_veche is None:
            memorie.pop(cheie, None)
        else:
            memorie[cheie] = valoare_veche

        print("GENESIS: Eroare la salvarea memoriei:", eroare)

def interpreteaza_memorarea(text, memorie,model,url):

    chei_existente = list(memorie.keys())

    instructiuni = f"""
Esti un analizor de cereri de memorare.

Stabileste daca utilizatorul cere EXPLICIT sa memorezi
sau sa actualizezi o informatie permanenta.

Chei deja existente:
{json.dumps(chei_existente, ensure_ascii=False)}

Daca informatia se refera la o cheie existenta,
foloseste acea cheie.

Daca este o informatie noua, creeaza o cheie scurta,
descriptiva, folosind litere mici si underscore.

Exemplu:
Utilizator: Tine minte ca animalul meu preferat este delfinul.
Raspuns:
{{"actiune": "actualizare_memorie", "cheie": "animal_preferat", "valoare": "delfinul"}}

Daca mesajul nu cere explicit memorarea:
{{"actiune": "nimic", "cheie": "", "valoare": ""}}

REGULI:
- Nu inventa informatii.
- Nu modifica memoria direct.
- Nu interpreta intrebarile ca cereri de memorare.
- Returneaza exclusiv JSON.
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

    if analiza.get("actiune") not in ("actualizare_memorie", "creare_memorie"):
        return None

    cheie = analiza.get("cheie")
    valoare = analiza.get("valoare")

    if not isinstance(cheie, str):
        return None

    if not isinstance(valoare, str):
        return None

    if not cheie or not cheie.isidentifier() or not cheie.islower():
        return None

    if not valoare.strip():
        return None

    return {
        "cheie": cheie,
        "valoare": valoare.strip()
    }
