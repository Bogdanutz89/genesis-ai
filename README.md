# PROJECT GENESIS

**GENESIS** este un asistent AI local, dezvoltat în Python, care utilizează Ollama pentru comunicarea cu modele lingvistice.

Aplicația funcționează în terminal și oferă conversații cu un model AI local, un sistem de comenzi, istoric conversațional persistent și memorie permanentă.

**Versiune publică: v2.0**

## Funcționalități

- **AI local** — comunicare cu modelul `qwen3:4b` prin API-ul Ollama.
- **Interfață în terminal** — conversație text cu asistentul.
- **Istoric conversațional** — salvarea mesajelor în format JSON.
- **Memorie permanentă** — păstrarea informațiilor între sesiuni.
- **Actualizarea memoriei cu confirmare** — modificările necesită acordul utilizatorului.
- **Comenzi dedicate** — administrarea istoricului și a memoriei.
- **Context conversațional** — utilizarea mesajelor recente și identificarea informațiilor relevante din istoric.
- **Căutare semantică asistată de LLM** — identificarea informațiilor relevante cu ajutorul modelului local, fără embeddings.
- **Gestionarea erorilor** — tratarea problemelor de conexiune, timeout și salvare.

## Cerințe

Pentru rularea GENESIS v2.0 sunt necesare:

- Python 3
- Ollama
- Modelul `qwen3:4b`
- Biblioteca Python `requests`

Aplicația a fost dezvoltată și testată într-un mediu Linux.

## Instalare

### 1. Clonează repository-ul

```bash
git clone <URL_REPOSITORY>
cd genesis-ai
```

Înlocuiește `<URL_REPOSITORY>` cu adresa repository-ului public.

### 2. Creează mediul virtual Python

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalează dependența Python

```bash
python -m pip install requests
```

### 4. Pregătește Ollama

Instalează Ollama folosind instrucțiunile oficiale.

Descarcă modelul:

```bash
ollama pull qwen3:4b
```

Asigură-te că serviciul Ollama este pornit.

## Pornirea aplicației

Din directorul proiectului, cu mediul virtual activat:

```bash
python genesis_ai_v20.py
```

La pornire, aplicația afișează:

```text
=== GENESIS AI v2.0 ===
```

GENESIS utilizează implicit API-ul Ollama disponibil la:

```text
http://127.0.0.1:11434/api/chat
```

## Comenzi disponibile

| Comandă | Descriere |
|---|---|
| `/help` | Afișează comenzile disponibile |
| `/memory` | Afișează memoria permanentă |
| `/set cheie valoare` | Propune modificarea unei informații din memorie |
| `/clear` | Șterge istoricul conversației |
| `/status` | Afișează starea asistentului |
| `/save` | Salvează istoricul și memoria permanentă |
| `/reset` | Resetează memoria permanentă, cu confirmare |
| `exit` | Închide aplicația |

## Exemplu de utilizare

```text
Tu: /set proiect GENESIS

GENESIS: Valoare veche: Necunoscut
GENESIS: Valoare noua: GENESIS
GENESIS: Confirmi modificarea? (da/nu): DA

GENESIS: Memoria permanenta a fost actualizata!

Tu: /memory

=== MEMORIE PERMANENTA ===
nume: Necunoscut
limba_preferata: romana
proiect: GENESIS
```

## Arhitectură

GENESIS v2.0 utilizează trei module principale:

```text
genesis-ai/
├── genesis_ai_v20.py
├── genesis_commands.py
├── genesis_memory.py
├── README.md
└── .gitignore
```

Repository-ul conține și fișiere istorice care documentează evoluția aplicației.

### genesis_ai_v20.py

Modulul principal al aplicației.

Responsabilități:

- Interacțiunea cu utilizatorul în terminal.
- Construirea contextului conversațional.
- Comunicarea HTTP cu Ollama.
- Procesarea și afișarea răspunsurilor AI.
- Integrarea sistemelor de comenzi și memorie.

### genesis_commands.py

Modulul responsabil pentru identificarea și executarea comenzilor utilizatorului.

### genesis_memory.py

Modulul responsabil pentru operațiile asupra istoricului conversațional și memoriei permanente.

## Persistența datelor

GENESIS stochează local informațiile în două fișiere JSON:

| Fișier | Rol |
|---|---|
| `genesis_memory.json` | Istoricul conversațiilor |
| `genesis_long_memory.json` | Memoria permanentă |

Datele sunt păstrate între sesiuni.

Ambele fișiere sunt excluse din repository prin `.gitignore`, deoarece pot conține informații personale.

## Evoluția proiectului

Repository-ul păstrează istoricul dezvoltării aplicației, de la **GENESIS v1.0 până la GENESIS v2.0**.

Etapele principale includ:

- **v1.0–v1.5:** dezvoltarea sistemului de comenzi.
- **v1.6–v1.7:** separarea comenzilor și a sistemului de memorie în module Python.
- **v1.8:** îmbunătățirea contextului conversațional.
- **v1.9:** îmbunătățirea stabilității și gestionării erorilor.
- **v2.0:** extinderea memoriei permanente.

Fișierele istorice `genesis_ai_v*.py` documentează evoluția implementării.

## Limitări

- GENESIS v2.0 funcționează exclusiv în terminal.
- Aplicația necesită un serviciu Ollama funcțional.
- Performanța depinde de modelul utilizat și de resursele sistemului.
- Căutarea semantică este realizată cu ajutorul modelului lingvistic local, nu prin embeddings.
- Nu există interfață grafică în această versiune.

## Stadiul proiectului

**GENESIS v2.0 — versiune locală, cu interfață în terminal.**

Funcționalitățile de conversație, actualizare a memoriei și persistență au fost verificate într-un mediu local.

## Licență

Licența proiectului nu a fost stabilită.








---

## GENESIS v3.0 — Versiunea curentă

GENESIS v3.0 este un asistent AI local cu interfață grafică Tkinter, dezvoltat în Python și integrat cu Ollama.

### Funcționalități

- Interfață grafică dark mode.
- Conversații locale cu modelul `gemma3:12b`.
- Afișarea progresivă a răspunsurilor AI (streaming).
- Istoric conversațional și memorie locală.
- Sistem de comenzi.
- Încărcarea documentelor `.txt`, `.md`, `.py` și `.json`.
- Documente UTF-8 de maximum 32 KiB.

Suportul PDF nu este inclus în v3.0.

### Instalare pe Ubuntu

1. Instalează pachetele necesare:

    sudo apt update
    sudo apt install git python3 python3-venv python3-tk

2. Clonează repository-ul:

    git clone https://github.com/Bogdanutz89/genesis-ai.git
    cd genesis-ai

3. Creează mediul virtual și instalează dependența Python:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install requests

4. Instalează Ollama folosind instrucțiunile oficiale și descarcă modelul:

    ollama pull gemma3:12b

5. Asigură-te că Ollama rulează, apoi pornește GENESIS:

    python genesis_ai_v30.py

### Configurare

- Fișier principal: `genesis_ai_v30.py`
- Model AI: `gemma3:12b`
- API Ollama: `http://127.0.0.1:11434/api/chat`
- Istoric local: `genesis_memory.json`
- Memorie locală: `genesis_long_memory.json`

Fișierele de memorie sunt excluse din Git.

### Colaborare

Fiecare colaborator instalează local Python, Ollama și modelul AI.

Modelul `gemma3:12b` necesită resurse hardware adecvate.

Instalarea pe calculatorul unui colaborator nu a fost încă testată.

Versiunile anterioare rămân disponibile pentru studierea evoluției proiectului.

---

**PROJECT GENESIS — Versiune curentă: v3.0**
