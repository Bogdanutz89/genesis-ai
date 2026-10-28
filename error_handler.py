print("=== GENESIS ERROR HANDLER ===")

try:
    with open("memorie_inexistenta.txt", "r") as fisier:
        continut = fisier.read()

    print(continut)

except FileNotFoundError:
    print("EROARE: Memoria solicitata nu exista!")

print("GENESIS este in continuare operational.")