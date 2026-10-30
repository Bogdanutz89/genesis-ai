"""GENESIS v2.9: interfață Tkinter cu context conversațional îmbunătățit."""
import io
import json
import queue
import re
import threading
import tkinter as tk
from time import monotonic
from contextlib import redirect_stdout
from pathlib import Path
from tkinter import messagebox

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
- Nu inventa informatii cand nu ai suficiente date.
- Recunoaste incertitudinea cand este justificata.
- Cere clarificari doar daca nu poti oferi un raspuns util fara ele.
- Nu pretinde ca ai verificat informatii pe internet daca nu ai accesat internetul.
- Acorda prioritate intrebarii actuale; foloseste istoricul doar pentru context relevant.

MEMORIE PE TERMEN LUNG:
{json.dumps(memorie, ensure_ascii=False, indent=2)}

REGULA IMPORTANTA:
Memoria permanenta contine informatiile confirmate.
Daca istoricul contrazice memoria permanenta,
foloseste memoria permanenta.

Nu pretinde ca ai modificat memoria daca Python
nu a confirmat salvarea.
"""


def pregateste_context(istoric):
    """Selectează ultimele 12 mesaje valide fără a modifica istoricul original."""
    mesaje = []
    for mesaj in istoric:
        if not isinstance(mesaj, dict):
            continue
        rol = mesaj.get("role")
        continut = mesaj.get("content")
        if rol not in ("user", "assistant") or not isinstance(continut, str):
            continue
        if rol == "assistant":
            marcaje = list(re.finditer(r"<\s*/?\s*think\b[^>]*(?:>|$)", continut, re.I))
            if marcaje:
                # Acceptăm numai delimitatori expliciți și o structură neambiguă.
                etichete = [m.group().lower() for m in marcaje]
                if any(e not in ("<think>", "</think>") for e in etichete):
                    continue
                if etichete == ["</think>"]:
                    # Format vechi: raționament fără eticheta de deschidere.
                    continut = continut[marcaje[0].end():]
                else:
                    pozitie = 0
                    sigur = len(marcaje) % 2 == 0
                    for i in range(0, len(marcaje) - 1, 2):
                        deschidere, inchidere = marcaje[i:i + 2]
                        if (etichete[i:i + 2] != ["<think>", "</think>"]
                                or continut[pozitie:deschidere.start()].strip()):
                            sigur = False
                            break
                        pozitie = inchidere.end()
                    if not sigur:
                        continue
                    continut = continut[pozitie:]
        if continut.strip():
            # Nu propagăm câmpuri suplimentare, de exemplu `thinking`.
            mesaje.append({"role": rol, "content": continut})
    return mesaje[-12:]


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
        self.raspuns_in_curs = False
        root.title("GENESIS AI v2.9")
        root.geometry("800x600")
        root.minsize(480, 320)
        fundal = "#0D0D0D"
        root.configure(bg=fundal)
        antet = tk.Frame(root, bg=fundal)
        antet.pack(fill=tk.X, padx=16, pady=(16, 0))
        self.buton_conversatie_noua = tk.Canvas(
            antet, width=36, height=36, bg=fundal, bd=0,
            highlightthickness=0, cursor="hand2", takefocus=1
        )
        self.buton_conversatie_noua.pack(side=tk.LEFT, padx=(0, 12))
        self.buton_conversatie_noua.create_line(
            18, 10, 9, 10, 9, 27, 26, 27, 26, 19,
            fill="#D4D4D4", disabledfill="#666666", width=2,
            capstyle=tk.ROUND, joinstyle=tk.ROUND
        )
        self.buton_conversatie_noua.create_polygon(
            17, 22, 18, 17, 27, 8, 31, 12, 22, 21,
            fill="", outline="#D4D4D4", disabledoutline="#666666",
            width=2, joinstyle=tk.ROUND
        )
        self.ajutor_conversatie_noua = tk.Label(
            root, text="Conversație nouă", bg="#262626", fg="#eeeeee",
            font=("Sans", 10), padx=8, pady=4, bd=0
        )

        def arata_ajutor_conversatie(event):
            if self.ocupat:
                return
            buton = self.buton_conversatie_noua
            buton.configure(bg="#242424")
            self.ajutor_conversatie_noua.place(
                x=buton.winfo_rootx() - root.winfo_rootx(),
                y=buton.winfo_rooty() - root.winfo_rooty() + 40
            )
            self.ajutor_conversatie_noua.lift()

        def ascunde_ajutor_conversatie(event=None):
            self.buton_conversatie_noua.configure(bg=fundal)
            self.ajutor_conversatie_noua.place_forget()

        def activeaza_conversatie_noua(event):
            ascunde_ajutor_conversatie()
            self.conversatie_noua()
            return "break"

        self.buton_conversatie_noua.bind("<Enter>", arata_ajutor_conversatie)
        self.buton_conversatie_noua.bind("<Leave>", ascunde_ajutor_conversatie)
        for eveniment in ("<Button-1>", "<Return>", "<space>"):
            self.buton_conversatie_noua.bind(eveniment, activeaza_conversatie_noua)
        self.indicator_stare = tk.Label(
            antet, text="GENESIS — Pregătit", bg=fundal, fg="#eeeeee",
            font=("Sans", 11), anchor=tk.W
        )
        self.indicator_stare.pack(side=tk.LEFT)
        zona_conversatie = tk.Frame(root, bg=fundal)
        zona_conversatie.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        defilement = tk.Scrollbar(
            zona_conversatie, orient=tk.VERTICAL, bg="#262626",
            troughcolor=fundal, activebackground="#383838",
            highlightthickness=0, bd=0
        )
        defilement.pack(side=tk.RIGHT, fill=tk.Y)
        coloana = tk.Frame(zona_conversatie, bg=fundal)
        coloana.pack(fill=tk.BOTH, expand=True)
        continut = tk.Frame(coloana, bg=fundal)
        continut.place(relx=0.5, y=0, anchor=tk.N, relheight=1)
        coloana.bind(
            "<Configure>",
            lambda event: continut.place_configure(width=min(event.width, 960))
        )
        self.conversatie = tk.Text(
            continut, wrap=tk.WORD, state=tk.DISABLED, bg=fundal,
            fg="#eeeeee", insertbackground="white", font=("Sans", 13),
            padx=16, pady=16, spacing1=4, spacing3=4, relief=tk.FLAT, bd=0,
            highlightthickness=0, yscrollcommand=defilement.set
        )
        self.conversatie.tag_configure("utilizator", foreground="#A8D5FF")
        self.conversatie.tag_configure("genesis", foreground="#ECECEC")
        defilement.configure(command=self.conversatie.yview)
        bara = tk.Canvas(
            continut, bg=fundal, height=68, highlightthickness=0, bd=0
        )
        bara.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 16))
        def rotunjeste_bara(event):
            latime, inaltime, raza = event.width, event.height, 30
            bara.delete("fundal")
            bara.create_polygon(
                raza, 0, latime-raza, 0, latime, 0, latime, raza,
                latime, inaltime-raza, latime, inaltime,
                latime-raza, inaltime, raza, inaltime, 0, inaltime,
                0, inaltime-raza, 0, raza, 0, 0,
                smooth=True, fill="#242424", outline="", tags="fundal"
            )
            bara.tag_lower("fundal")

        bara.bind("<Configure>", rotunjeste_bara)
        self.conversatie.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        self.text_intrare = tk.StringVar()
        self.intrare = tk.Entry(
            bara, bg="#242424", fg="#F5F5F5", insertbackground="#F5F5F5",
            disabledbackground="#242424", disabledforeground="#9B9B9B",
            font=("Sans", 14), relief=tk.FLAT, bd=0, highlightthickness=0,
            textvariable=self.text_intrare
        )
        self.intrare.place(x=22, rely=0.5, anchor=tk.W, relwidth=1, width=-90)
        self.intrare.bind("<Return>", self.trimite)
        self.buton = tk.Canvas(
            bara, width=44, height=44, bg="#242424", bd=0,
            highlightthickness=0, cursor="hand2", takefocus=1
        )
        self.buton.place(relx=1, x=-12, rely=0.5, anchor=tk.E)
        self.buton.create_oval(
            0, 0, 43, 43, fill="#F5F5F5", outline="",
            disabledfill="#9B9B9B"
        )
        self.buton.create_text(
            22, 22, text="↑", font=("Sans", 22), fill="#171717"
        )
        self.buton.bind("<Button-1>", self.trimite)
        self.buton.bind("<Return>", self.trimite)
        self.buton.bind("<space>", self.trimite)
        bara.bind("<Button-1>", lambda event: self.intrare.focus_set())
        ajutor = tk.Label(
            self.intrare, text="Scrie un mesaj pentru GENESIS...",
            bg="#242424", fg="#9B9B9B", font=("Sans", 14),
            anchor=tk.W, padx=0, pady=0, cursor="xterm"
        )

        def actualizeaza_ajutor(*_):
            if self.text_intrare.get():
                ajutor.place_forget()
            else:
                ajutor.place(x=0, rely=0.5, anchor=tk.W, relwidth=1)

        ajutor.bind("<Button-1>", lambda event: self.intrare.focus_set())
        self.text_intrare.trace_add("write", actualizeaza_ajutor)
        actualizeaza_ajutor()
        for mesaj in istoric:
            if mesaj["role"] != "system":
                self.afiseaza("Tu" if mesaj["role"] == "user" else "GENESIS", mesaj["content"])
        self.afiseaza("GENESIS", "Scrie un mesaj sau /help pentru comenzile disponibile.")
        self.intrare.focus_set()
        root.after(100, self.verifica_rezultate)

    def afiseaza(self, autor, text):
        eticheta = "utilizator" if autor == "Tu" else "genesis"
        self.conversatie.configure(state=tk.NORMAL)
        self.conversatie.insert(tk.END, f"{autor}: {text}\n\n", eticheta)
        self.conversatie.configure(state=tk.DISABLED)
        self.conversatie.see(tk.END)

    def afiseaza_fragment(self, text):
        # Doar firul principal modifică textul, înaintea separatorului dintre mesaje.
        if not self.raspuns_in_curs:
            self.afiseaza("GENESIS", "")
            self.conversatie.mark_set("raspuns_start", "end-3c")
            self.conversatie.mark_gravity("raspuns_start", tk.LEFT)
            self.conversatie.mark_set("raspuns_final", "end-3c")
            self.conversatie.mark_gravity("raspuns_final", tk.RIGHT)
            self.raspuns_in_curs = True
        self.conversatie.configure(state=tk.NORMAL)
        self.conversatie.insert("raspuns_final", text, "genesis")
        self.conversatie.configure(state=tk.DISABLED)
        self.conversatie.see(tk.END)

    def seteaza_ocupat(self, ocupat):
        self.ocupat = ocupat
        self.indicator_stare.configure(
            text="GENESIS — Generează răspuns..." if self.ocupat else "GENESIS — Pregătit"
        )
        self.intrare.configure(state=tk.DISABLED if ocupat else tk.NORMAL)
        self.buton.configure(state=tk.DISABLED if ocupat else tk.NORMAL)
        self.buton_conversatie_noua.configure(state=tk.DISABLED if ocupat else tk.NORMAL)
        self.buton_conversatie_noua.configure(
            bg="#0D0D0D", cursor="arrow" if ocupat else "hand2",
            takefocus=0 if ocupat else 1
        )
        self.ajutor_conversatie_noua.place_forget()
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
            self.afiseaza("GENESIS", f"Versiune: v2.9\nModel AI: {MODEL}\n"
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
            mesaje = pregateste_context(istoric)
            fragmente = []
            finalizat = False
            with requests.post(URL, json={
                "model": MODEL, "messages": [
                    {"role": "system", "content": construieste_instructiuni(memorie)}
                ] + mesaje, "stream": True, "think": True
            }, stream=True, timeout=120) as raspuns:
                raspuns.raise_for_status()
                for linie in raspuns.iter_lines(chunk_size=1):
                    if not linie:
                        continue
                    eveniment = json.loads(linie)
                    if not isinstance(eveniment, dict):
                        raise ValueError("Fragment JSON Ollama invalid.")
                    if "error" in eveniment:
                        raise ValueError(str(eveniment["error"]))
                    mesaj = eveniment.get("message", {})
                    if not isinstance(mesaj, dict):
                        raise ValueError("Mesaj Ollama invalid.")
                    # Ollama poate trimite raționamentul separat în `thinking`.
                    # Numai `content` este eligibil pentru afișare și istoric.
                    fragment = mesaj.get("content", "")
                    if not isinstance(fragment, str):
                        raise ValueError("Răspunsul Ollama nu este text.")
                    if fragment:
                        fragmente.append(fragment)
                        self.rezultate.put(("fragment", fragment))
                    if eveniment.get("done") is True:
                        finalizat = True
                        break
                if not finalizat:
                    raise ValueError("Fluxul s-a închis fără confirmarea finalizării (done).")
            continut = "".join(fragmente)
            istoric.append({"role": "assistant", "content": continut})
            self.rezultate.put(("raspuns", (continut, istoric)))
        except requests.exceptions.Timeout:
            self.rezultate.put(("eroare", "Ollama răspunde prea greu. Încearcă din nou."))
        except requests.exceptions.ConnectionError:
            self.rezultate.put(("eroare", "Nu pot contacta Ollama. Verifică dacă serviciul este pornit."))
        except (requests.exceptions.RequestException, ValueError, KeyError, TypeError) as eroare:
            self.rezultate.put(("eroare", f"Eroare la cererea Ollama: {eroare}"))

    def verifica_rezultate(self):
        termen = monotonic() + 0.008
        coada_epuizata = False
        try:
            for _ in range(100):
                if monotonic() >= termen:
                    break
                tip, rezultat = self.rezultate.get_nowait()
                if tip == "fragment":
                    self.afiseaza_fragment(rezultat)
                    continue
                if tip == "avertizare":
                    self.afiseaza("GENESIS", rezultat)
                    continue
                try:
                    if tip == "memorie":
                        self.propune_modificare(self.memorie, rezultat["cheie"], rezultat["valoare"])
                    elif tip == "raspuns":
                        continut, istoric = rezultat
                        self.istoric = istoric
                        if not self.raspuns_in_curs:
                            self.afiseaza("GENESIS", continut)
                        self.salveaza_istoricul(self.istoric)
                    else:
                        if self.raspuns_in_curs:
                            rezultat = ("Răspuns întrerupt; textul parțial de mai sus "
                                        "nu a fost salvat în istoric. " + rezultat)
                        self.afiseaza("GENESIS", rezultat)
                except (OSError, ValueError, TypeError) as eroare:
                    self.afiseaza("GENESIS", f"Eroare la salvare: {eroare}. Poți reîncerca prin /save.")
                finally:
                    if self.raspuns_in_curs:
                        self.conversatie.mark_unset("raspuns_start", "raspuns_final")
                        self.raspuns_in_curs = False
                    self.seteaza_ocupat(False)
        except queue.Empty:
            coada_epuizata = True
        if coada_epuizata:
            self.root.after(100, self.verifica_rezultate)
        else:
            # Permite redesenarea Tk înainte de următorul lot, fără pauze
            # artificiale între fragmentele deja disponibile.
            self.root.after_idle(self.verifica_rezultate)


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
