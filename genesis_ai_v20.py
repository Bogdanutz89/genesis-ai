import json
import requests
import genesis_memory
from genesis_commands import este_comanda, executa_comanda


print("=== GENESIS AI v2.0 ===")
print("Scrie 'exit' pentru a inchide programul.")
print("Scrie '/memory' pentru a vedea memoria permanenta.")
print("Scrie '/set cheie valoare' pentru a modifica memoria.")
print("Poti spune si: Tine minte ca proiectul meu se numeste ...")


url = "http://127.0.0.1:11434/api/chat"

fisier_memorie = "genesis_memory.json"
fisier_memorie_lunga = "genesis_long_memory.json"

model = "qwen3:4b"
limita_context = 4


# ==========================================
# INSTRUCTIUNI PENTRU GENESIS
# ==========================================

def cauta_in_istoric(istoric, cuvant):

    rezultate = []

    for mesaj in istoric:
        if (
    mesaj["role"] == "user"
    and cuvant.lower() in mesaj["content"].lower()
        ):
            rezultate.append(mesaj)

    return rezultate

def calculeaza_scor(intrebare, mesaj):
    cuvinte = intrebare.lower().replace("?", "").split()

    text_mesaj = mesaj["content"].lower()

    potriviri = [c for c in cuvinte if c in text_mesaj]

    return len(potriviri)

def gaseste_mesaj_relevant(istoric, intrebare):
    mesaj_relevant = None
    scor_maxim = 0

    for mesaj in istoric:
        if mesaj["role"] != "user":
            continue

        scor = calculeaza_scor(intrebare, mesaj)

        if scor > scor_maxim:
            scor_maxim = scor
            mesaj_relevant = mesaj

    return mesaj_relevant
def cauta_semantic(istoric, intrebare, url):
    mesaje = [
        mesaj for mesaj in istoric
        if mesaj["role"] == "user"
        and mesaj["content"].strip().lower() != intrebare.strip().lower()
    ]

    if not mesaje:
        return None

    lista_mesaje = "\n".join(
        f"{i}: {mesaj['content']}"
        for i, mesaj in enumerate(mesaje)
    )

    instructiune = f"""
Esti un sistem de cautare in memoria unei conversatii.

Sarcina ta este sa identifici mesajul utilizatorului
care contine informatia necesara pentru a raspunde la intrebare.

REGULI:
1. Cauta semnificatia, nu doar cuvintele identice.
2. O intrebare poate fi formulata diferit fata de informatia salvata.
3. Preferintele utilizatorului sunt informatii relevante.
4. Nu alege intrebari sau mesaje fara informatii utile.
5. Daca gasesti raspunsul, indica numarul mesajului si informatia gasita.
6. Foloseste -1 numai daca informatia nu exista in mesaje.

EXEMPLU:
Intrebare: Ce animal imi place cel mai mult?
Mesaje:
0: Salut!
1: Animalul meu preferat este delfinul.
2: Ce este gravitatia?

Raspuns:
{{"alegere": 1, "informatie": "Animalul preferat este delfinul."}}

ACUM ANALIZEAZA:

Intrebare: {intrebare}

Mesaje:
{lista_mesaje}

Returneaza exclusiv obiectul JSON cerut.
"""

    try:
        raspuns = requests.post(
            url,
            json={
                "model": "qwen3:4b",
                "messages": [
                    {"role": "user", "content": instructiune}
                ],
                "stream": False,
                "think": False,
                "format": {
                    "type": "object",
                    "properties": {
                        "alegere": {"type": "integer"},
                        "informatie": {"type": "string"}
                    },
                    "required": ["alegere", "informatie"],
                    "additionalProperties": False
                }
            },
            timeout=120
        )

        raspuns.raise_for_status()

        continut = raspuns.json()["message"]["content"]
        print("DEBUG JSON:", continut)
        alegere = int(json.loads(continut)["alegere"])
        

        if 0 <= alegere < len(mesaje):
            return mesaje[alegere]

    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        TypeError
    ) as eroare:
        print("DEBUG SEMANTIC: metoda de rezerva folosita:", eroare)
        return gaseste_mesaj_relevant(mesaje, intrebare)

    return None

def construieste_instructiuni(memorie):
    return f"""
Esti GENESIS, un asistent AI personal care ruleaza local.
Comunica intotdeauna in limba romana.

REGULI DE CONVERSATIE:
- Foloseste o romana naturala, corecta gramatical si usor de inteles.
- Evita traducerile mot-a-mot din engleza.
- Nu confunda persoana I cu persoana a II-a.
- Tu esti asistentul, iar utilizatorul este persoana pe care o ajuti.
- Raspunde clar, concis si direct la intrebare.
- Evita formularile artificiale si repetitiile inutile.
- Nu incepe fiecare raspuns cu un salut.

MEMORIE PE TERMEN LUNG:
{json.dumps(memorie, ensure_ascii=False, indent=2)}

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

    except requests.exceptions.RequestException:
        print("GENESIS: Nu pot verifica memoria deoarece Ollama nu raspunde.")

    except (ValueError, KeyError, TypeError):
        print("GENESIS: Am intampinat o problema la analiza memoriei.")

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

    # PASTRAM ULTIMELE MESAJE
    mesaje_recente = mesaje_conversatie[-limita_context:]

    # V2.0: folosim memoria permanenta organizata
    mesaj_relevant = None

    # CONSTRUIM CONTEXTUL PENTRU OLLAMA
    context = [
        {
            "role": "system",
            "content": instructiuni
        }
    ]

    if mesaj_relevant is not None:
        context.append(mesaj_relevant)

    context.extend(mesaje_recente)


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

    except requests.exceptions.ConnectionError:
        print("GENESIS: Nu pot contacta Ollama. Verifica daca serviciul este pornit.")
    except requests.exceptions.Timeout:
        print("GENESIS: Ollama raspunde prea greu. Incearca din nou.")

    except requests.exceptions.RequestException as eroare:
        print("GENESIS: Eroare de comunicare cu Ollama:", eroare)

    except (KeyError, ValueError) as eroare:
        print("GENESIS: Eroare la procesarea raspunsului:", eroare)

    except OSError as eroare:
        print("GENESIS: Eroare la salvarea istoricului:", eroare)
