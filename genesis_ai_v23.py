"""GENESIS v2.3: interfață Tkinter pentru logica locală din v2.0."""
import io
import json
import queue
import threading
import tkinter as tk
from contextlib import redirect_stdout
from pathlib import Path
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

import requests
import genesis_memory
from genesis_commands import este_comanda, executa_comanda

URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:4b"
BAZA = Path(__file__).resolve().parent
FISIER_MEMORIE = BAZA / "genesis_long_memory.json"
FISIER_ISTORIC = BAZA / "genesis_memory.json"
MEMORIE_INITIALA = {
    "nume": "Bogdan", "limba_preferata": "romana", "proiect": "PROJECT GENESIS"
}


def construieste_instructiuni(memorie):
    return f"""
Esti GENESIS, un asistent AI personal care ruleaza local.
IDENTITATE:
- Numele tau este GENESIS.
- Esti asistentul personal al utilizatorului.
- Campul "nume" din memoria permanenta reprezinta numele utilizatorului, nu numele tau.
- Nu te prezenta niciodata drept Bogdan.
- Cand esti intrebat cine esti, raspunde ca esti GENESIS.
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


def incarca_date(cale, implicit, tip):
    try:
        with cale.open(encoding="utf-8") as fisier:
            date = json.load(fisier)
    except FileNotFoundError:
        return implicit.copy()
    if not isinstance(date, tip):
        raise ValueError(f"Format invalid în {cale.name}")
    if tip is list and any(
        not isinstance(m, dict)
        or m.get("role") not in ("system", "user", "assistant")
        or not isinstance(m.get("content"), str)
        for m in date
    ):
        raise ValueError(f"Mesaje invalide în {cale.name}")
    return date


class GenesisApp:
    def __init__(self, root, memorie, istoric):
        self.root = root
        self.memorie = memorie
        self.istoric = istoric
        self.rezultate = queue.Queue()
        self.ocupat = False
        root.title("GENESIS AI v2.3")
        root.geometry("800x600")
        root.minsize(480, 320)
        root.configure(bg="#212121")
        stil_buton = {
            "bg": "#383838", "fg": "#eeeeee",
            "activebackground": "#4a4a4a", "activeforeground": "white",
            "disabledforeground": "#888888", "font": ("Sans", 11),
            "relief": tk.FLAT, "bd": 0, "padx": 14, "pady": 8,
            "cursor": "hand2"
        }
        antet = tk.Frame(root, bg="#212121")
        antet.pack(fill=tk.X, padx=16, pady=(16, 0))
        self.indicator_stare = tk.Label(
            antet, text="GENESIS — Pregătit", bg="#212121", fg="#eeeeee",
            font=("Sans", 11), anchor=tk.W
        )
        self.indicator_stare.pack(side=tk.LEFT)
        self.buton_conversatie_noua = tk.Button(
            antet, text="Conversație nouă", command=self.conversatie_noua,
            **stil_buton
        )
        self.buton_conversatie_noua.pack(side=tk.RIGHT)
        self.conversatie = ScrolledText(
            root, wrap=tk.WORD, state=tk.DISABLED, bg="#202020",
            fg="#eeeeee", insertbackground="white", font=("Sans", 11),
            padx=16, pady=16, relief=tk.FLAT, bd=0
        )
        self.conversatie.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        bara = tk.Frame(root, bg="#212121")
        bara.pack(fill=tk.X, padx=16, pady=(0, 16))
        self.intrare = tk.Entry(
            bara, bg="#303030", fg="white", insertbackground="white",
            disabledbackground="#303030", disabledforeground="#aaaaaa",
            font=("Sans", 11), relief=tk.FLAT, bd=0
        )
        self.intrare.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.intrare.bind("<Return>", self.trimite)
        self.buton = tk.Button(
            bara, text="Trimite", command=self.trimite, **stil_buton
        )
        self.buton.pack(side=tk.RIGHT, padx=(10, 0))
        for mesaj in istoric:
            if mesaj["role"] != "system":
                self.afiseaza("Tu" if mesaj["role"] == "user" else "GENESIS", mesaj["content"])
        self.afiseaza("GENESIS", "Scrie un mesaj sau /help pentru comenzile disponibile.")
        self.intrare.focus_set()
        root.after(100, self.verifica_rezultate)

    def afiseaza(self, autor, text):
        self.conversatie.configure(state=tk.NORMAL)
        self.conversatie.insert(tk.END, f"{autor}: {text}\n\n")
        self.conversatie.configure(state=tk.DISABLED)
        self.conversatie.see(tk.END)

    def seteaza_ocupat(self, ocupat):
        self.ocupat = ocupat
        self.indicator_stare.configure(
            text="GENESIS — Generează răspuns..." if self.ocupat else "GENESIS — Pregătit"
        )
        self.intrare.configure(state=tk.DISABLED if ocupat else tk.NORMAL)
        self.buton.configure(state=tk.DISABLED if ocupat else tk.NORMAL,
                             text="Așteaptă…" if ocupat else "Trimite")
        self.buton_conversatie_noua.configure(state=tk.DISABLED if ocupat else tk.NORMAL)
        if not ocupat:
            self.intrare.focus_set()

    def conversatie_noua(self):
        if self.ocupat:
            return
        try:
            self.comanda("/clear")
        except (OSError, ValueError, TypeError) as eroare:
            self.afiseaza("GENESIS", f"Operațiunea nu a reușit: {eroare}")
        self.intrare.focus_set()

    def salveaza_memoria(self, memorie):
        genesis_memory.salveaza_memoria(memorie, FISIER_MEMORIE)

    def salveaza_istoricul(self, istoric):
        genesis_memory.salveaza_istoricul(istoric, FISIER_ISTORIC)

    def propune_modificare(self, memorie, cheie, valoare):
        if not isinstance(valoare, str) or not valoare.strip():
            self.afiseaza("GENESIS", "Valoarea propusă nu este validă.")
            return
        valoare = valoare.strip()
        if not messagebox.askyesno(
            "Confirmare memorie",
            f"Cheie: {cheie}\nValoare veche: {memorie.get(cheie)}\n"
            f"Valoare nouă: {valoare}\n\nConfirmi modificarea?", parent=self.root
        ):
            self.afiseaza("GENESIS", "Modificarea a fost anulată.")
            return
        actualizata = dict(memorie)
        actualizata[cheie] = valoare
        self.salveaza_memoria(actualizata)
        memorie.clear()
        memorie.update(actualizata)
        self.afiseaza("GENESIS", "Memoria permanentă a fost actualizată.")

    def comanda(self, text):
        # Comenzile care folosesc input() sau șterg date sunt adaptate pentru GUI.
        if text in ("/reset", "/clear"):
            reset = text == "/reset"
            if messagebox.askyesno(
                "Confirmare", "Resetezi memoria permanentă?" if reset
                else "Ștergi istoricul conversației?", parent=self.root
            ):
                if reset:
                    self.salveaza_memoria(MEMORIE_INITIALA)
                    self.memorie.clear()
                    self.memorie.update(MEMORIE_INITIALA)
                else:
                    self.salveaza_istoricul([])
                    self.istoric.clear()
                    self.conversatie.configure(state=tk.NORMAL)
                    self.conversatie.delete("1.0", tk.END)
                    self.conversatie.configure(state=tk.DISABLED)
                self.afiseaza("GENESIS", "Memoria a fost resetată." if reset else "Istoricul a fost șters.")
            else:
                self.afiseaza("GENESIS", "Operațiunea a fost anulată.")
            return
        if text == "/status":
            self.afiseaza("GENESIS", f"Versiune: v2.3\nModel AI: {MODEL}\n"
                          f"Mesaje în istoric: {len(self.istoric)}\nMemorie permanentă: activă")
            return
        iesire = io.StringIO()
        with redirect_stdout(iesire):
            recunoscuta = executa_comanda(
                text, self.memorie, self.istoric, MODEL, FISIER_ISTORIC,
                self.propune_modificare, self.salveaza_istoricul, self.salveaza_memoria
            )
        if iesire.getvalue().strip():
            self.afiseaza("GENESIS", iesire.getvalue().strip())
        if not recunoscuta:
            self.afiseaza("GENESIS", "Comandă necunoscută. Scrie /help.")

    def trimite(self, event=None):
        if self.ocupat:
            return "break"
        text = self.intrare.get().strip()
        if not text:
            return "break"
        self.intrare.delete(0, tk.END)
        if text.lower() == "exit":
            self.root.destroy()
            return "break"
        self.afiseaza("Tu", text)
        try:
            if este_comanda(text):
                self.comanda(text)
            else:
                self.seteaza_ocupat(True)
                threading.Thread(
                    target=self.cere_raspuns,
                    args=(text, dict(self.memorie), list(self.istoric)), daemon=True
                ).start()
        except (OSError, ValueError, TypeError) as eroare:
            self.afiseaza("GENESIS", f"Operațiunea nu a reușit: {eroare}")
        return "break"

    def cere_raspuns(self, text, memorie, istoric):
        # Firul secundar comunică exclusiv prin coadă; nu accesează Tkinter.
        try:
            try:
                propunere = genesis_memory.interpreteaza_memorarea(text, memorie, MODEL, URL)
            except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
                propunere = None
                self.rezultate.put(("avertizare", "Analiza memorării nu a reușit; încerc răspunsul conversațional."))
            if propunere is not None:
                self.rezultate.put(("memorie", propunere))
                return
            istoric.append({"role": "user", "content": text})
            mesaje = [m for m in istoric if m["role"] != "system"][-4:]
            raspuns = requests.post(URL, json={
                "model": MODEL, "messages": [
                    {"role": "system", "content": construieste_instructiuni(memorie)}
                ] + mesaje, "stream": False, "think": False
            }, timeout=120)
            raspuns.raise_for_status()
            continut = raspuns.json()["message"]["content"]
            if not isinstance(continut, str):
                raise ValueError("Răspunsul Ollama nu este text.")
            if "</think>" in continut:
                continut = continut.split("</think>", 1)[1].strip()
            istoric.append({"role": "assistant", "content": continut})
            self.rezultate.put(("raspuns", (continut, istoric)))
        except requests.exceptions.Timeout:
            self.rezultate.put(("eroare", "Ollama răspunde prea greu. Încearcă din nou."))
        except requests.exceptions.ConnectionError:
            self.rezultate.put(("eroare", "Nu pot contacta Ollama. Verifică dacă serviciul este pornit."))
        except (requests.exceptions.RequestException, ValueError, KeyError, TypeError) as eroare:
            self.rezultate.put(("eroare", f"Eroare la cererea Ollama: {eroare}"))

    def verifica_rezultate(self):
        try:
            while True:
                tip, rezultat = self.rezultate.get_nowait()
                if tip == "avertizare":
                    self.afiseaza("GENESIS", rezultat)
                    continue
                try:
                    if tip == "memorie":
                        self.propune_modificare(self.memorie, rezultat["cheie"], rezultat["valoare"])
                    elif tip == "raspuns":
                        continut, istoric = rezultat
                        self.istoric = istoric
                        self.afiseaza("GENESIS", continut)
                        self.salveaza_istoricul(self.istoric)
                    else:
                        self.afiseaza("GENESIS", rezultat)
                except (OSError, ValueError, TypeError) as eroare:
                    self.afiseaza("GENESIS", f"Eroare la salvare: {eroare}. Poți reîncerca prin /save.")
                finally:
                    self.seteaza_ocupat(False)
        except queue.Empty:
            pass
        self.root.after(100, self.verifica_rezultate)


def main():
    root = tk.Tk()
    root.withdraw()
    try:
        memorie = incarca_date(FISIER_MEMORIE, {
            "nume": "Necunoscut", "limba_preferata": "romana", "proiect": "Necunoscut"
        }, dict)
        istoric = incarca_date(FISIER_ISTORIC, [], list)
    except (OSError, ValueError) as eroare:
        messagebox.showerror("Eroare la încărcare", str(eroare), parent=root)
        root.destroy()
        return
    GenesisApp(root, memorie, istoric)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
