<div align="center">

# 🧠 Local Brain

### Enterprise-Grade · On-Premise · 100% Private AI Knowledge Engine

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](https://nextjs.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-FF6B35)](https://ollama.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-6C5CE7)](https://qdrant.tech)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-008CC1?logo=neo4j)](https://neo4j.com)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis)](https://redis.io)

**Upload your documents. Ask anything. Get precise, cited answers — fully offline.**

*No cloud. No subscriptions. No data ever leaves your machine.*

---

🇺🇸 **English** · [🇪🇸 Español](README_ES.md) · [🇩🇪 Deutsch](README_DE.md) · [🇯🇵 日本語](README_JA.md)

</div>

---

## 🖥️ Live Preview

> Local Brain running locally — zero cloud, 100% private.

![Local Brain — Chat Interface Screenshot](assets/localbrain_screenshot.png)

---

## 🚀 What is Local Brain?

Local Brain is a **private, self-hosted AI platform** that transforms your organization's documents into a searchable, intelligent knowledge base powered entirely by a **local LLM running on your own hardware**.

Upload files — PDFs, Word docs, Excel sheets, CSVs, Markdown, images — and the system automatically parses, chunks, embeds, and indexes them. The AI answers questions with **exact citations and upload timestamps**, uses **semantic NLP** to understand intent precisely, and **never calls any external API**.

> **Perfect for teams that handle sensitive data** and cannot use cloud AI services.

---

## 🏗️ System Architecture

> Interactive, vector-crisp SVG architectural map. Fully scalable, responsive, and offline-compatible.
> **Note:** For IDE or raw text fallbacks, click below to view the Mermaid representation.

<details>
<summary>💻 View Mermaid Class Diagram Code</summary>

```mermaid
graph TB
    subgraph USER["👤 User Interface Layer"]
        UI["🖥️ Next.js 14 Chat UI<br/>Glassmorphic Design<br/>WebSocket Live Updates"]
        GRAPH["🕸️ Interactive Knowledge Graph<br/>Force-Directed Visualization<br/>Node Click → File Analysis"]
        UPLOAD["📎 File Upload Zone<br/>Drag & Drop • Multi-Format"]
    end

    subgraph BACKEND["⚙️ FastAPI Autonomic Engine (Port 8000)"]
        direction TB
        PARSER["📄 Document Parser<br/>PDF · DOCX · XLSX · CSV<br/>JSON · TXT · PPTX · MD"]
        NLP["🧠 NLP Processor<br/>Intent Detection · Fuzzy Title Match<br/>Semantic Relevance Guard"]
        RAG["🔍 RAG Pipeline<br/>Hybrid Vector + Keyword Search<br/>Context Window Memory"]
        SYNTH["✍️ Synthesis Engine<br/>Structured Response Generation<br/>Citation Formatting"]
        DLP["🛡️ DLP Scanner<br/>SSN · Credit Card Blocking<br/>RBAC Filter"]
    end

    subgraph DATABASES["💾 Database Layer"]
        QDRANT["🔷 Qdrant<br/>Vector Store<br/>1024-dim Embeddings<br/>Semantic Search"]
        NEO4J["🕸️ Neo4j<br/>Knowledge Graph<br/>Concepts · Entities<br/>Relationships"]
        POSTGRES["🐘 PostgreSQL<br/>Document Metadata<br/>Content Storage<br/>User Roles"]
        REDIS["⚡ Redis<br/>Query Cache<br/>WebSocket Broadcast<br/>Session Store"]
    end

    subgraph LLM["🤖 Local LLM Layer"]
        OLLAMA["🦙 Ollama Server<br/>Qwen2.5 · Llama 3<br/>Mistral · Phi-3"]
        VLLM["⚡ vLLM Server<br/>GPU-Accelerated<br/>High Throughput"]
        EMBED["📐 Embeddings Engine<br/>1024-dim Vectors<br/>Local Generation"]
    end

    subgraph MCP["🔌 IDE Integration"]
        MCPSERVER["MCP Protocol Server<br/>Cursor IDE · Claude Desktop"]
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
    SYNTH --> DLP
    SYNTH --> LLM
    BACKEND --> NEO4J
    BACKEND --> REDIS
    MCPSERVER --> BACKEND
    LLM --> EMBED
```
</details>

---

## 🔍 Query & RAG Response Flow

> Full neural-semantic workflow, fuzzy token resolution, intent classification, and RAG retrieval pathways.
> **Note:** For IDE or raw text fallbacks, click below to view the Mermaid representation.

<details>
<summary>💻 View Mermaid Flowchart Code</summary>

```mermaid
flowchart TD
    A([User Query]) --> B{Slash Command?}
    B -- Yes --> C["/connect /help /status"]
    C --> D([Command Response])
    B -- No --> E{Suggestion Chip?}
    E -- "Summarize docs" --> F[Fetch all docs from PG\nGenerate real summaries]
    E -- "List indexed" --> G[Table of all docs + sizes]
    E -- "Show connections" --> H[Neo4j graph relationships]
    F & G & H --> Z([Formatted Response])
    E -- No --> I[Redis Cache Lookup]
    I -- Hit --> Z
    I -- Miss --> J[NLP: Detect Intent]
    J --> K["Intent Types:\n• summarize\n• analyse\n• compare\n• locate\n• extract\n• table\n• general"]
    K --> L[Fuzzy Title Match\nNLPProcessor.match_document_title]
    L -- Match found --> M[Load full doc content\nfrom PostgreSQL directly]
    L -- No match --> N[Vector Similarity Search\nQdrant semantic search]
    N -- Score ≥ 0.40 --> O[Relevant chunks]
    N -- Score < 0.40 --> P[Keyword Fallback Search\nContent-specific terms only]
    M & O & P --> Q[NLP Relevance Guard\nCheck overlap ≥ 6%]
    Q -- Relevant --> R[Synthesis Engine\nLocal LLM / Procedural]
    Q -- Not relevant --> S(["⚠️ Information not found\nin indexed documents"])
    R --> T[DLP Scan\nBlock SSN/CC]
    T --> U[Save to Redis Cache]
    U --> Z

    style A fill:#6C5CE7,color:#fff
    style Z fill:#00B894,color:#fff
    style S fill:#E17055,color:#fff
    style D fill:#0984E3,color:#fff
```
</details>

---

## 📐 Layer Breakdown

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **🖥️ Chat UI** | Next.js 14 + Glassmorphic CSS | Chat console, file upload, knowledge graph visualization |
| **⚙️ API Backend** | FastAPI + Python 3.10+ | Document ingestion, RAG pipeline, NLP processing, RBAC, DLP |
| **🧠 NLP Engine** | MarkItDown + Custom NLP | Markdown normalization, intent detection, fuzzy title matching |
| **🔷 Vector DB** | Qdrant | 1024-dim semantic chunk storage, sub-200ms similarity search |
| **🕸️ Graph DB** | Neo4j | GraphRAG concept relationships, entity synapses, knowledge mapping |
| **🐘 Relational DB** | PostgreSQL | File metadata, full content, permissions, user roles |
| **⚡ Cache** | Redis | Query caching, WebSocket broadcast, session state |
| **🤖 Local LLM** | Ollama / vLLM | Private embeddings + RAG answer synthesis (fully offline) |
| **🔌 IDE Bridge** | MCP Protocol | Cursor IDE & Claude Desktop direct knowledge access |

---

## ✨ Features

### 🔒 Security & Privacy First
- **100% On-Premise** — Zero data leaves your machine or network, ever
- **DLP Scanner** — Automatically blocks SSNs and credit card numbers from AI responses
- **RBAC** — Role-based access control per document and user group
- **Offline Operation** — Works entirely without internet once set up

### 🧠 Advanced AI Knowledge Engine

#### Semantic NLP Understanding
- **Intent Detection** — Recognizes 7 intent types: `summarize`, `analyse`, `compare`, `locate`, `extract`, `table`, `general`
- **Fuzzy Document Title Matching** — Uses token Jaccard similarity + bigram overlap + exact containment scoring. Asking *"summarize the ai document"* correctly finds `Document.pdf` even with typos or partial names
- **Relevance Guard** — Returns `⚠️ Information not found` when retrieved chunks don't semantically match the query — never serves a wrong document
- **Contextual Memory** — Sliding window of last 5 conversation turns for coherent multi-turn dialogue

#### GraphRAG & Knowledge Extraction
- **Graphify Techniques** — Deep semantic mapping of extracted `concepts`, `entities`, and `relationships` directly into a Neo4j knowledge graph.
- **Pre-computed Relationships** — Provides the local LLM with blazingly fast context retrieval and profound conceptual memory.

#### Deep File Analysis (powered by Microsoft MarkItDown)
- **Unified Async Markdown Parsing** — Converts PDF, DOCX, XLSX, CSV, PPTX, JSON, TXT into clean Markdown natively using high-speed non-blocking syncio threads.
- **Optimized for LLMs** — By standardizing all file types into Markdown, vector embeddings and LLM context comprehension are drastically improved.
- **Images** — Registry path + download link generation

#### Response Intelligence
- **Format-Aware Synthesis** — Tables for numeric data, bullet summaries for text docs, slide outlines for presentations
- **Citation Required & Dynamic Links** — Every answer cites exact document name + upload timestamp, and dynamically generates a robust, case-insensitive download link.
- **Targeted Passage Finder** — Scores every sentence by query-token overlap to surface the most relevant passages
- **Comparison Mode** — Side-by-side markdown tables for multi-document queries

### 💬 Chat Interface
- **Glassmorphic UI** — Dynamic gradients, frosted glass panels, micro-animations
- **Live Log Stream** — Real-time ingestion events via WebSocket
- **Suggestion Chips** — Clickable quick actions (Summarize, List, Show Graph, Analyse)
- **Slash Commands** — `/connect slack <webhook>`, `/connect gmail <token>`, `/help`
- **Download Links** — Direct file download links rendered as clickable markdown

---

## ⚡ Quick Start

### Prerequisites

| Requirement | Version | Purpose |
|:-----------|:--------|:--------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| Docker & Docker Compose | Latest | Database stack |
| Ollama | Latest | Local LLM server |

### Step 1 — Clone & Configure

```bash
git clone https://github.com/your-org/localbrain.git
cd localbrain
cp .env.example .env
# Edit .env with your database passwords and model settings
```

### Step 2 — Start Databases (Docker)

```bash
docker-compose up -d
# Starts: Qdrant (6333), Neo4j (7474/7687), PostgreSQL (5432), Redis (6379)
```

### Step 3 — Start the Local LLM (Ollama)

```bash
# Windows (PowerShell)
$env:OLLAMA_ORIGINS="*"; ollama serve

# macOS / Linux
OLLAMA_ORIGINS="*" ollama serve
```

```bash
# Pull a recommended model (in a new terminal)
ollama pull qwen2.5:7b-instruct-q4_K_M
# Or a lighter model for lower-spec machines:
ollama pull qwen2.5:3b-instruct
```

Then set in `.env`:
```properties
VLLM_API_URL=http://localhost:11434/v1
LOCAL_MODEL_NAME=qwen2.5:7b-instruct-q4_K_M
```

### Step 4 — Start the Backend

```bash
python -m venv venv

# Windows:
.\\venv\\Scripts\\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r core_api/requirements.txt
python -m scripts.init_dbs          # Run once — seeds DB schemas
uvicorn core_api.main:app --port 8000 --reload
```

### Step 5 — Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 🔌 GPU-Accelerated vLLM (Optional)

For high-throughput deployments with NVIDIA GPUs:

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --port 8001
```

Update `.env`:
```properties
VLLM_API_URL=http://localhost:8001/v1
LOCAL_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
```

---

## 🖥️ MCP — IDE Integration

Connect Local Brain to **Cursor IDE** or **Claude Desktop** and query your knowledge base from inside your code editor.

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "LocalBrain": {
      "command": "python",
      "args": ["C:/path/to/localbrain/core_api/mcp_server.py"]
    }
  }
}
```

### MCP Tool Reference

| Tool | Description |
|:-----|:-----------|
| `search_wiki` | Semantic search across all indexed documents |
| `get_index` | Lists all document titles, types, and metadata |
| `get_page` | Reads a specific document with its graph relationships |
| `get_overview` | System health: doc count, chunk count, DB status |
| `index_document` | Ingests a new file from a local path into the knowledge base |

---

## 💬 Slash Commands Reference

| Command | Example | What it does |
|:--------|:--------|:------------|
| `/help` | `/help` | Shows all features and usage guide |
| `/connect slack` | `/connect slack https://hooks.slack.com/...` | Mounts Slack webhook integration |
| `/connect notion` | `/connect notion <token> <db_id>` | Connects Notion database |
| `/connect gmail` | `/connect gmail <api_token>` | Mounts Gmail inbox reader |
| `/connect jira` | `/connect jira <url> <token> <project>` | Connects Jira tracker |
| `/connect gdrive` | `/connect gdrive <folder_id>` | Mounts Google Drive folder |

---

## 📁 Project Structure

```
localbrain/
├── core_api/                    # FastAPI backend
│   ├── main.py                  # API routes, upload, query, graph endpoints
│   ├── synthesis.py             # NLP engine + RAG synthesis + DLP guard
│   ├── ingestion.py             # Document parsers + embedding pipeline
│   ├── databases.py             # Qdrant, Neo4j, PostgreSQL, Redis adapters
│   ├── mcp_server.py            # Model Context Protocol server
│   ├── logger.py                # Structured logging
│   ├── config.py                # Environment configuration
│   └── requirements.txt         # Python dependencies
├── frontend/                    # Next.js 14 chat UI
│   └── src/
│       └── app/
│           ├── page.tsx         # Main chat interface
│           ├── globals.css      # Glassmorphic design system
│           └── components/      # Reusable UI components
├── assets/
│   ├── localbrain_screenshot.png  # UI screenshot (shown above)
│   └── localbrain_demo.mp4        # Screen recording demo
├── scripts/                     # DB initialization & seed scripts
├── workers/                     # Background ingestion workers
├── security/                    # DLP rules & auth modules
├── uploaded_docs/               # Persistent document storage
├── temp_uploads/                # Temporary upload staging
├── docker-compose.yml           # Full database stack definition
├── .env.example                 # Configuration template
└── README.md                    # This file
```
## 🧪 Supported File Formats

| Format | Extension | Analysis Type |
|:-------|:----------|:-------------|
| PDF | `.pdf` | Full text, page-by-page extraction |
| Word | `.docx` | Paragraph XML parser |
| Excel | `.xlsx`, `.xls` | Multi-sheet cell resolver + statistics |
| CSV | `.csv` | Row/column structured text |
| PowerPoint | `.pptx` | Slide-by-slide outline |
| JSON | `.json` | Formatted structure display |
| Text | `.txt`, `.md`, `.markdown` | Raw text with chunking |
| Images | `.png`, `.jpg`, `.jpeg` | Registry + download link |

---

## 📄 License

Released under the **[Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)**.

---

<div align="center">

Built for teams that take **data privacy seriously**.

*All Local. Zero cloud. 100% yours.*

⭐ **Star this repo** if Local Brain helps your team stay private!

</div>
