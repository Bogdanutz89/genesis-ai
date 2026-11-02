import json

def este_comanda(text):
    return text.startswith("/")
def executa_comanda(text, memorie,istoric,model,fisier_memorie,propune_modificare,salveaza_istoricul,salveaza_memoria):
 # COMANDA /help
    if text == "/help":
        print("\n=== COMENZI GENESIS ===")
        print("/help - Afiseaza comenzile disponibile")
        print("/memory - Afiseaza memoria permanenta")
        print("/set cheie valoare - Modifica memoria")
        print("/clear - Sterge istoricul conversatiei")
        print("/status - Afiseaza starea asistentului")
        print("/reset - Reseteaza memoria permanenta cu confirmare")
        print("/save - Salveaza istoricul si memoria permanenta")
        print("exit - Inchide programul")
        return True

    # COMANDA /memory
    if text == "/memory":

        print("\n=== MEMORIE PERMANENTA ===")

        for cheie, valoare in memorie.items():
            print(f"{cheie}: {valoare}")

        return True

    # COMANDA /set
    if text == "/set" or text.startswith("/set "):

        parti = text.split(maxsplit=2)

        if len(parti) != 3:
            print("GENESIS: Format: /set cheie valoare")
            return True

        cheie = parti[1]
        valoare = parti[2]

        propune_modificare(
            memorie,
            cheie,
            valoare
        )

        return True

    if text == "/clear":
        try:
            with open(fisier_memorie, "w", encoding="utf-8") as fisier:
                json.dump([], fisier, ensure_ascii=False, indent=4)

            istoric.clear()
            print("GENESIS: Istoricul conversatiei a fost sters.")
        except OSError as eroare:
            print("GENESIS: Eroare la stergerea istoricului:", eroare)

        return True

# COMANDA /status
    if text == "/status":
        print("\n=== STATUS GENESIS ===")
        print("Versiune: v2.0")
        print(f"Model AI: {model}")
        print(f"Mesaje in istoric: {len(istoric)}")
        print("Memorie permanenta: activa")
        return True

 # COMANDA /save
    if text == "/save":
        try:
            salveaza_istoricul(istoric)
            salveaza_memoria(memorie)
            print("GENESIS: Istoricul si memoria permanenta au fost salvate.")
        except OSError as eroare:
            print("GENESIS: Eroare la salvare:", eroare)

        return True

 # COMANDA /reset
    if text == "/reset":
        confirmare = input(
            "GENESIS: Resetezi memoria permanenta? (da/nu): "
        ).strip().lower()

        if confirmare != "da":
            print("GENESIS: Resetarea a fost anulata.")
            return True

        memorie_initiala = {
            "nume": "Bogdan",
            "limba_preferata": "romana",
            "proiect": "PROJECT GENESIS"
        }

        try:
            salveaza_memoria(memorie_initiala)
            memorie.clear()
            memorie.update(memorie_initiala)
            print("GENESIS: Memoria permanenta a fost resetata.")
        except OSError as eroare:
            print("GENESIS: Eroare la resetare:", eroare)

        return True


