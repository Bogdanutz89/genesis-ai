hardware = {
    "CPU": "Intel Core Ultra 5 235",
    "GPU": "NVIDIA RTX 5070",
    "RAM": 32,
    "VRAM": 12
}


def afiseaza_hardware():
    print("=== GENESIS SYSTEM MONITOR ===")

    for componenta, valoare in hardware.items():
        print(componenta, ":", valoare)


def verifica_memorie():
    if hardware["RAM"] >= 16:
        print("STATUS: Memorie RAM suficienta pentru AI local.")
    else:
        print("STATUS: Memorie RAM limitata.")

def verifica_vram():
    if hardware["VRAM"] >= 8:
        print("VRAM suficienta pentru testele AI")
    else:
        print("VRAM limitata")    

def salveaza_raport():
    with open("genesis_report.txt", "w") as fisier:
        fisier.write("=== GENESIS HARDWARE REPORT ===\n")

        for componenta, valoare in hardware.items():
            fisier.write(f"{componenta}: {valoare}\n")

    print("Raportul hardware a fost salvat!")


afiseaza_hardware()
verifica_memorie()
verifica_vram()
salveaza_raport()