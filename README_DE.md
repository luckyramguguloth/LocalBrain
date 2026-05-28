<div align="center">

<p align="center">
  <img src="assets/synapsecore_logo.png" alt="Logo" width="80" height="80" />
</p>
<h1 align="center">Local Brain</h1>

### Enterprise-KI-Plattform · On-Premise · 100% Privat

[![Lizenz: Apache 2.0](https://img.shields.io/badge/Lizenz-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](https://nextjs.org)
[![Ollama](https://img.shields.io/badge/Ollama-Lokales%20LLM-FF6B35)](https://ollama.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vektor--DB-6C5CE7)](https://qdrant.tech)
[![Neo4j](https://img.shields.io/badge/Neo4j-Wissensgraph-008CC1?logo=neo4j)](https://neo4j.com)

**Lade Dokumente hoch. Stelle Fragen. Erhalte präzise, zitierte Antworten — vollständig offline.**

*Keine Cloud. Keine Abonnements. Deine Daten verlassen niemals dein Gerät.*

---

[🇺🇸 English](README.md) · [🇪🇸 Español](README_ES.md) · 🇩🇪 **Deutsch** · [🇯🇵 日本語](README_JA.md)

</div>

---

## 🖥️ Live-Vorschau

> Local Brain läuft lokal — keine Cloud, 100% privat.

![Local Brain — Screenshot der Benutzeroberfläche](assets/localbrain_screenshot.png)

---

## 🚀 Was ist Local Brain?

Local Brain ist eine **private, selbst gehostete KI-Plattform**, die die Dokumente deiner Organisation in eine durchsuchbare, intelligente Wissensbasis verwandelt — vollständig betrieben von einem **lokalen LLM auf deiner eigenen Hardware**.

Du lädst Dateien hoch — PDFs, Word-Dokumente, Excel-Tabellen, CSVs, Markdown — und das System analysiert, zerlegt, indiziert und macht diese über eine moderne Chat-Oberfläche abfragbar. Die KI nutzt **fortgeschrittene semantische NLP** und **ruft niemals eine externe API auf**.

> **Ideal für Teams, die mit sensiblen Daten arbeiten** und keine Cloud-KI-Dienste nutzen können.

---

## 🏗️ Systemarchitektur

> Vektorscharfe, interaktive SVG-Systemarchitekturkarte. Vollständig skalierbar, reaktionsschnell und offline-kompatibel.
> **Hinweis:** Für IDEs oder Nur-Text-Reader klicken Sie unten, um die Mermaid-Darstellung anzuzeigen.

<details>
<summary>💻 Mermaid-Diagrammcode anzeigen</summary>

```mermaid
graph TB
    subgraph NUTZER["👤 Benutzeroberfläche"]
        UI["🖥️ Next.js 14 Chat-UI<br/>Glassmorphisches Design<br/>Live-Updates via WebSocket"]
        GRAPH["🕸️ Interaktiver Wissensgraph<br/>Kraftgerichtete Visualisierung<br/>Klick auf Knoten → Dateianalyse"]
        UPLOAD["📎 Datei-Upload-Zone<br/>Drag & Drop · Multi-Format"]
    end

    subgraph BACKEND["⚙️ FastAPI-Autonome Engine (Port 8000)"]
        direction TB
        PARSER["📄 Dokumenten-Parser<br/>PDF · DOCX · XLSX · CSV<br/>JSON · TXT · PPTX · MD"]
        NLP["🧠 NLP-Prozessor<br/>Absichtserkennung · Unscharfer Titelabgleich<br/>Semantischer Relevanzwächter"]
        RAG["🔍 RAG-Pipeline<br/>Hybrid: Vektor + Schlüsselwortsuche<br/>Kontextfenster-Gedächtnis"]
        SYNTH["✍️ Synthese-Engine<br/>Strukturierte Antwortgenerierung<br/>Zitatformatierung"]
        DLP["🛡️ DLP-Scanner<br/>SSN · Kreditkarten-Blockierung<br/>RBAC-Filter"]
    end

    subgraph DATENBANKEN["💾 Datenbankschicht"]
        QDRANT["🔷 Qdrant<br/>Vektordatenbank<br/>1024-dim Einbettungen<br/>Semantische Suche"]
        NEO4J["🕸️ Neo4j<br/>Wissensgraph<br/>Konzepte · Entitäten<br/>Beziehungen"]
        POSTGRES["🐘 PostgreSQL<br/>Dokument-Metadaten<br/>Inhaltsspeicher<br/>Benutzerrollen"]
        REDIS["⚡ Redis<br/>Anfrage-Cache<br/>WebSocket-Broadcast<br/>Sitzungsspeicher"]
    end

    subgraph LLM["🤖 Lokale LLM-Schicht"]
        OLLAMA["🦙 Ollama-Server<br/>Qwen2.5 · Llama 3<br/>Mistral · Phi-3"]
        EMBED["📐 Einbettungs-Engine<br/>1024-dim Vektoren<br/>Lokale Generierung"]
    end

    UI --> BACKEND
    GRAPH --> BACKEND
    UPLOAD --> BACKEND
    PARSER --> QDRANT
    PARSER --> POSTGRES
    NLP --> RAG
    RAG --> QDRANT
    RAG --> POSTGRES
    RAG --> SYNTH
    SYNTH --> LLM
    BACKEND --> NEO4J
    BACKEND --> REDIS
```
</details>

---

## 🔍 Abfrage- und RAG-Antwortfluss

> Vollständiger neuro-semantischer Workflow, unscharfe Token-Auflösung, Absichts-Klassifizierung und RAG-Synthesepfade.
> **Hinweis:** Für IDEs oder Nur-Text-Reader klicken Sie unten, um die Mermaid-Darstellung anzuzeigen.

<details>
<summary>💻 Mermaid-Diagrammcode anzeigen</summary>

```mermaid
flowchart TD
    A([Benutzeranfrage]) --> B{Slash-Befehl?}
    B -- Ja --> C["/connect /help /status"]
    B -- Nein --> D{Vorschlag-Chip?}
    D -- "Dokumente zusammenfassen" --> E[Alle Docs aus PG laden\nEchte Zusammenfassungen]
    D -- Nein --> F[Redis-Cache-Suche]
    F -- Treffer --> Z([Formatierte Antwort])
    F -- Fehler --> G[NLP: Absicht erkennen]
    G --> H["Absichtstypen:\n• zusammenfassen\n• analysieren\n• vergleichen\n• lokalisieren\n• extrahieren"]
    H --> I[Unscharfer Titelabgleich\nJaccard + Bigramme]
    I -- Treffer --> J[Vollständigen Inhalt laden\naus PostgreSQL]
    I -- Kein Treffer --> K[Vektorsuche\nQdrant semantisch]
    J & K --> L[NLP-Relevanzwächter\nÜberlappung ≥ 6%]
    L -- Relevant --> M[Synthese-Engine\nLokales LLM / Prozedural]
    L -- Nicht relevant --> N(["⚠️ Information nicht gefunden\nin indizierten Dokumenten"])
    M --> O[DLP-Scan]
    O --> Z

    style A fill:#6C5CE7,color:#fff
    style Z fill:#00B894,color:#fff
    style N fill:#E17055,color:#fff
```
</details>

---

## 📐 Schichtenaufbau

| Schicht | Technologie | Zweck |
|:--------|:-----------|:------|
| **🖥️ Chat-Oberfläche** | Next.js 14 + Glassmorphisches CSS | Chat-Konsole, Datei-Upload, Wissensgraph |
| **⚙️ API-Backend** | FastAPI + Python 3.10+ | Dokumenteneinspeisung, RAG-Pipeline, NLP, RBAC, DLP |
| **🧠 NLP-Engine** | Benutzerdefiniertes Python-NLP | Absichtserkennung, unscharfer Titelabgleich |
| **🔷 Vektor-DB** | Qdrant | 1024-dim semantische Fragmentspeicherung |
| **🕸️ Graph-DB** | Neo4j | Konzeptbeziehungen, Wissensmapping |
| **🐘 Relationale DB** | PostgreSQL | Datei-Metadaten, vollständiger Inhalt, Rollen |
| **⚡ Cache** | Redis | Anfrage-Caching, WebSocket-Broadcast |
| **🤖 Lokales LLM** | Ollama / vLLM | Private Einbettungen + RAG-Antwortsynthese |
| **🔌 IDE-Brücke** | MCP-Protokoll | Cursor IDE & Claude Desktop Direktzugriff |

---

## ✨ Hauptfunktionen

### 🔒 Sicherheit & Datenschutz
- **100% On-Premise** — Keine Daten verlassen jemals dein Gerät oder Netzwerk
- **DLP-Scanner** — Blockiert automatisch SSNs und Kreditkartennummern in KI-Antworten
- **RBAC** — Rollenbasierte Zugriffskontrolle pro Dokument und Benutzergruppe
- **Offline-Betrieb** — Funktioniert vollständig ohne Internet nach der Einrichtung

### 🧠 Fortgeschrittene KI-Engine
- **Absichtserkennung** — Erkennt 7 Typen: `zusammenfassen`, `analysieren`, `vergleichen`, `lokalisieren`, `extrahieren`, `tabelle`, `allgemein`
- **Unscharfer Titelabgleich** — Findet das richtige Dokument auch bei Tippfehlern oder Teilnamen
- **Relevanzwächter** — Liefert niemals ein falsches Dokument
- **Kontextuelles Gedächtnis** — Gleitendes Fenster der letzten 5 Gesprächsrunden

### 📄 Unterstützte Dateiformate
- **PDF** — Vollständige Textextraktion pro Seite
- **DOCX** — Direkter XML-Absatz-Parser
- **XLSX / XLS / CSV** — Mehrblattes Zellenresolver, numerische Statistiken
- **PPTX** — Folie-für-Folie XML-Gliederungsrekonstruktion
- **JSON / TXT / MD** — Native Parser mit vollständiger Indizierung

---

## ⚡ Schnellstart

### Voraussetzungen

| Anforderung | Version |
|:-----------|:--------|
| Python | 3.10+ |
| Node.js | 18+ |
| Docker & Docker Compose | Neueste |
| Ollama | Neueste |

### Schritt 1 — Klonen & Konfigurieren

```bash
git clone https://github.com/deine-org/localbrain.git
cd localbrain
cp .env.example .env
```

### Schritt 2 — Datenbanken starten (Docker)

```bash
docker-compose up -d
```

### Schritt 3 — Lokales LLM starten (Ollama)

```bash
$env:OLLAMA_ORIGINS="*"; ollama serve       # Windows
OLLAMA_ORIGINS="*" ollama serve             # macOS/Linux
ollama pull qwen2.5:7b-instruct-q4_K_M
```

### Schritt 4 — Backend starten

```bash
python -m venv venv && .\\venv\\Scripts\\Activate.ps1
pip install -r core_api/requirements.txt
python -m scripts.init_dbs
uvicorn core_api.main:app --port 8000 --reload
```

### Schritt 5 — Frontend starten

```bash
cd frontend && npm install && npm run dev
```

Öffne [http://localhost:3000](http://localhost:3000)

---

## 📁 Projektstruktur

```
localbrain/
├── core_api/                    # FastAPI-Backend
│   ├── main.py                  # API-Routen: Upload, Abfrage, Graph
│   ├── synthesis.py             # NLP-Engine + RAG-Synthese + DLP-Wächter
│   ├── ingestion.py             # Dokumenten-Parser + Einbettungs-Pipeline
│   ├── databases.py             # Qdrant, Neo4j, PostgreSQL, Redis-Adapter
│   └── mcp_server.py            # MCP-Protokoll-Server
├── frontend/                    # Next.js 14 Chat-Oberfläche
├── assets/
│   ├── localbrain_screenshot.png  # UI-Screenshot (oben gezeigt)
│   └── localbrain_demo.mp4        # Bildschirmaufzeichnung Demo
├── scripts/                     # DB-Initialisierungsskripte
├── workers/                     # Hintergrundverarbeitungs-Worker
├── docker-compose.yml           # Datenbank-Stack-Definition
└── .env.example                 # Konfigurationsvorlage
```

---

## 📄 Lizenz

Veröffentlicht unter der **[Apache Lizenz 2.0](http://www.apache.org/licenses/LICENSE-2.0)**.

---

<div align="center">

Gebaut für Teams, die **Datenschutz ernst nehmen**.

*Alles lokal. Keine Cloud. 100% dein.*

⭐ **Gib dem Repo einen Stern**, wenn Local Brain deinem Team hilft!

</div>
