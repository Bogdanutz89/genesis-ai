# PROJECT GENESIS

**GENESIS** is a local AI assistant developed in Python that uses Ollama to communicate with language models.

The v2.0 application runs in the terminal and provides conversations with a local AI model, a command system, persistent conversation history, and long-term memory.

**Version documented in the following historical section: v2.0.** For the current version, see [GENESIS v3.0](#genesis-v30--current-version) below.

## Features (v2.0)

- **Local AI** — communication with the `qwen3:4b` model through the Ollama API.
- **Terminal interface** — text-based conversations with the assistant.
- **Conversation history** — messages saved in JSON format.
- **Long-term memory** — information preserved between sessions.
- **Memory updates with confirmation** — changes require user approval.
- **Dedicated commands** — conversation history and memory management.
- **Conversational context** — use of recent messages and identification of relevant information from history.
- **LLM-assisted semantic search** — identification of relevant information using the local language model, without embeddings.
- **Error handling** — handling connection problems, timeouts, and saving errors.

## Requirements (v2.0)

GENESIS v2.0 requires:

- Python 3
- Ollama
- The `qwen3:4b` model
- The Python `requests` library

The application was developed and tested in a Linux environment.

## Installation (v2.0)

### 1. Clone the repository

```bash
git clone https://github.com/Bogdanutz89/genesis-ai.git
cd genesis-ai
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the Python dependency

```bash
python -m pip install requests
```

### 4. Set up Ollama

Install Ollama following the official installation instructions.

Download the model:

```bash
ollama pull qwen3:4b
```

Make sure the Ollama service is running.

## Running the Application (v2.0)

From the project directory, with the virtual environment activated:

```bash
python genesis_ai_v20.py
```

At startup, the application displays:

```text
=== GENESIS AI v2.0 ===
```

GENESIS uses the Ollama API available by default at:

```text
http://127.0.0.1:11434/api/chat
```

## Available Commands (v2.0)

| Command | Description |
|---|---|
| `/help` | Displays available commands |
| `/memory` | Displays long-term memory |
| `/set key value` | Proposes changing a value stored in memory |
| `/clear` | Clears conversation history |
| `/status` | Displays assistant status |
| `/save` | Saves conversation history and long-term memory |
| `/reset` | Resets long-term memory, with confirmation |
| `exit` | Exits the application |

## Usage Example (v2.0)

The following example is translated for readability; the application's actual prompts may appear in Romanian.

```text
You: /set proiect GENESIS

GENESIS: Previous value: Unknown
GENESIS: New value: GENESIS
GENESIS: Confirm the change? (yes/no): YES

GENESIS: Long-term memory has been updated!

You: /memory

=== LONG-TERM MEMORY ===
nume: Necunoscut
limba_preferata: romana
proiect: GENESIS
```

## Architecture (v2.0)

GENESIS v2.0 uses three main modules:

```text
genesis-ai/
├── genesis_ai_v20.py
├── genesis_commands.py
├── genesis_memory.py
├── README.md
└── .gitignore
```

The repository also contains historical files documenting the application's evolution.

### genesis_ai_v20.py

The application's main module. Responsibilities:

- Terminal-based user interaction.
- Building conversational context.
- HTTP communication with Ollama.
- Processing and displaying AI responses.
- Integrating the command and memory systems.

### genesis_commands.py

The module responsible for identifying and executing user commands.

### genesis_memory.py

The module responsible for operations involving conversation history and long-term memory.

## Data Persistence

GENESIS stores information locally in two JSON files:

| File | Purpose |
|---|---|
| `genesis_memory.json` | Conversation history |
| `genesis_long_memory.json` | Long-term memory |

Data is preserved between sessions. Both files are excluded from the repository through `.gitignore` because they may contain personal information.

## Project Evolution (through v2.0)

The repository preserves the application's development history. The milestones through **GENESIS v2.0** include:

- **v1.0–v1.5:** development of the command system.
- **v1.6–v1.7:** separation of commands and memory management into Python modules.
- **v1.8:** improvements to conversational context.
- **v1.9:** stability and error-handling improvements.
- **v2.0:** expansion of long-term memory.

Historical `genesis_ai_v*.py` files document the implementation's evolution.

## Limitations (v2.0)

- GENESIS v2.0 runs exclusively in the terminal.
- The application requires a functioning Ollama service.
- Performance depends on the selected model and available system resources.
- Semantic search is performed using the local language model, not embeddings.
- This version does not include a graphical interface.

## Project Status (v2.0)

**GENESIS v2.0 — local version with a terminal interface.**

Conversation functionality, memory updates, and data persistence were verified in a local environment.

## License

A license has not yet been selected.

---

## GENESIS v3.0 — Current Version

GENESIS v3.0 is a local AI assistant with a Tkinter graphical interface, developed in Python and integrated with Ollama.

### Features

- Dark-mode graphical interface.
- Local conversations using the `gemma3:12b` model.
- Streaming AI responses.
- Conversation history and local memory.
- Command system.
- Support for loading `.txt`, `.md`, `.py`, and `.json` documents.
- UTF-8 text documents up to 32 KiB.

PDF support is not included in v3.0.

### Installation on Ubuntu

**1. Install the required packages:**

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-tk
```

**2. Clone the repository:**

```bash
git clone https://github.com/Bogdanutz89/genesis-ai.git
cd genesis-ai
```

**3. Create a virtual environment and install the Python dependency:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install requests
```

**4. Install Ollama** using the official installation instructions.

Download the required model:

```bash
ollama pull gemma3:12b
```

**5. Make sure Ollama is running, then launch GENESIS:**

```bash
python genesis_ai_v30.py
```

### Configuration

- **Main application file:** `genesis_ai_v30.py`
- **AI model:** `gemma3:12b`
- **Ollama API:** `http://127.0.0.1:11434/api/chat`
- **Local conversation history:** `genesis_memory.json`
- **Local long-term memory:** `genesis_long_memory.json`

Memory files are excluded from Git.

### Collaboration

Each collaborator installs Python, Ollama, and the AI model locally.

The `gemma3:12b` model requires adequate hardware resources.

Installation on a collaborator's computer has not yet been tested.

Previous versions remain available in the repository for studying the project's development.

---

**PROJECT GENESIS — Current Version: v3.0**
