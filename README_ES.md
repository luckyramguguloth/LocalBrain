<div align="center">
<p align="center">
  <img src="assets/synapsecore_logo.png" alt="Logo" width="80" height="80" />
</p>
<h1 align="center">Local Brain</h1>

### Plataforma de IA Empresarial · On-Premise · 100% Privada

[![Licencia: Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](https://nextjs.org)
[![Ollama](https://img.shields.io/badge/Ollama-LLM%20Local-FF6B35)](https://ollama.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Base%20Vectorial-6C5CE7)](https://qdrant.tech)
[![Neo4j](https://img.shields.io/badge/Neo4j-Grafo%20de%20Conocimiento-008CC1?logo=neo4j)](https://neo4j.com)

**Sube tus documentos. Pregunta cualquier cosa. Obtén respuestas precisas y citadas — completamente offline.**

*Sin nube. Sin suscripciones. Tus datos nunca abandonan tu servidor.*

---

[🇺🇸 English](README.md) · 🇪🇸 **Español** · [🇩🇪 Deutsch](README_DE.md) · [🇯🇵 日本語](README_JA.md)

</div>

---

## 🖥️ Vista Previa en Vivo

> Local Brain ejecutándose localmente — cero nube, 100% privado.

![Local Brain — Captura de Pantalla de la Interfaz](assets/localbrain_screenshot.png)

---

## 🚀 ¿Qué es Local Brain?

Local Brain es una **plataforma de IA privada y autohospedada** que convierte los documentos de tu organización en una base de conocimiento inteligente y consultable, impulsada completamente por un **LLM local que se ejecuta en tu propio hardware**.

Sube archivos — PDFs, documentos Word, hojas Excel, CSVs, Markdown — y el sistema los analiza, trocea, indexa y hace consultables a través de una interfaz de chat moderna. La IA usa **NLP semántico avanzado** para entender la intención del usuario y **nunca llama a ninguna API externa**.

> **Perfecto para equipos que manejan datos sensibles** y no pueden usar servicios de IA en la nube.

---

## 🏗️ Arquitectura del Sistema

> Mapa de arquitectura SVG vectorial nítido. Completamente escalable, responsivo y compatible offline.
> **Nota:** Para entornos IDE o lectores de texto plano, haz clic abajo para ver la representación Mermaid.

<details>
<summary>💻 Ver código de diagrama Mermaid</summary>

```mermaid
graph TB
    subgraph USUARIO["👤 Capa de Interfaz de Usuario"]
        UI["🖥️ Chat UI Next.js 14<br/>Diseño Glassmorphic<br/>Actualizaciones en Tiempo Real"]
        GRAPH["🕸️ Grafo de Conocimiento Interactivo<br/>Visualización por Fuerza<br/>Clic en Nodo → Análisis de Archivo"]
        UPLOAD["📎 Zona de Subida<br/>Arrastrar y Soltar · Multi-Formato"]
    end

    subgraph BACKEND["⚙️ Motor Autónomo FastAPI (Puerto 8000)"]
        direction TB
        PARSER["📄 Parser de Documentos<br/>PDF · DOCX · XLSX · CSV<br/>JSON · TXT · PPTX · MD"]
        NLP["🧠 Procesador NLP<br/>Detección de Intención · Coincidencia Difusa<br/>Guardia de Relevancia Semántica"]
        RAG["🔍 Pipeline RAG<br/>Búsqueda Híbrida: Vector + Palabras Clave<br/>Memoria de Ventana Contextual"]
        SYNTH["✍️ Motor de Síntesis<br/>Generación de Respuestas Estructuradas<br/>Formato de Citas"]
        DLP["🛡️ Escáner DLP<br/>Bloqueo SSN · Tarjetas de Crédito<br/>Filtro RBAC"]
    end

    subgraph BBDD["💾 Capa de Bases de Datos"]
        QDRANT["🔷 Qdrant<br/>Base Vectorial<br/>Embeddings 1024-dim<br/>Búsqueda Semántica"]
        NEO4J["🕸️ Neo4j<br/>Grafo de Conocimiento<br/>Conceptos · Entidades<br/>Relaciones"]
        POSTGRES["🐘 PostgreSQL<br/>Metadatos de Documentos<br/>Almacenamiento de Contenido<br/>Roles de Usuario"]
        REDIS["⚡ Redis<br/>Caché de Consultas<br/>WebSocket Broadcast<br/>Sesiones"]
    end

    subgraph LLM["🤖 Capa LLM Local"]
        OLLAMA["🦙 Servidor Ollama<br/>Qwen2.5 · Llama 3<br/>Mistral · Phi-3"]
        EMBED["📐 Motor de Embeddings<br/>Vectores 1024-dim<br/>Generación Local"]
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

## 🔍 Flujo de Consulta RAG

> Flujo de trabajo neuro-semántico completo, resolución difusa de tokens, clasificación de intención y vías de síntesis RAG.
> **Nota:** Para entornos IDE o lectores de texto plano, haz clic abajo para ver la representación Mermaid.

<details>
<summary>💻 Ver código de diagrama Mermaid</summary>

```mermaid
flowchart TD
    A([Consulta del Usuario]) --> B{¿Comando Slash?}
    B -- Sí --> C["/connect /help /status"]
    B -- No --> D{¿Chip de Sugerencia?}
    D -- "Resumir docs" --> E[Obtener todos los docs\nGenerar resúmenes reales]
    D -- No --> F[Buscar en Caché Redis]
    F -- Acierto --> Z([Respuesta Formateada])
    F -- Fallo --> G[NLP: Detectar Intención]
    G --> H["Tipos de Intención:\n• resumir · analizar\n• comparar · localizar\n• extraer · tabla"]
    H --> I[Coincidencia Difusa de Título\nJaccard + Bigramas + Exacto]
    I -- Coincidencia --> J[Cargar contenido completo\ndesde PostgreSQL]
    I -- Sin coincidencia --> K[Búsqueda Vectorial\nQdrant semántico]
    J & K --> L[Guardia de Relevancia NLP\nSolapamiento ≥ 6%]
    L -- Relevante --> M[Motor de Síntesis\nLLM Local / Procedural]
    L -- No relevante --> N(["⚠️ Información no encontrada\nen los documentos indexados"])
    M --> O[Escaneo DLP]
    O --> Z

    style A fill:#6C5CE7,color:#fff
    style Z fill:#00B894,color:#fff
    style N fill:#E17055,color:#fff
```
</details>

---

## 📐 Desglose por Capas

| Capa | Tecnología | Propósito |
|:-----|:-----------|:---------|
| **🖥️ Interfaz Chat** | Next.js 14 + CSS Glassmorphic | Consola de chat, subida de archivos, visualización del grafo |
| **⚙️ Backend API** | FastAPI + Python 3.10+ | Ingesta, pipeline RAG, procesamiento NLP, RBAC, DLP |
| **🧠 Motor NLP** | MarkItDown + NLP personalizado | Normalización Markdown, detección de intención, coincidencia difusa |
| **🔷 BD Vectorial** | Qdrant | Almacenamiento semántico 1024-dim, búsqueda sub-200ms |
| **🕸️ BD de Grafos** | Neo4j | Relaciones conceptuales GraphRAG, mapeo de conocimiento |
| **🐘 BD Relacional** | PostgreSQL | Metadatos de archivos, contenido completo, roles |
| **⚡ Caché** | Redis | Caché de consultas, WebSocket broadcast |
| **🤖 LLM Local** | Ollama / vLLM | Embeddings privados + síntesis RAG (offline) |
| **🔌 IDE** | Protocolo MCP | Acceso desde Cursor IDE y Claude Desktop |

---

## ✨ Características Principales

### 🔒 Seguridad y Privacidad
- **100% On-Premise** — Cero datos salen de tu máquina o red
- **Escáner DLP** — Bloquea SSNs y números de tarjetas de crédito en respuestas IA
- **RBAC** — Control de acceso basado en roles por documento y usuario
- **Operación Offline** — Funciona completamente sin internet una vez configurado

### 🧠 Motor de IA Avanzado
- **GraphRAG y Extracción (Graphify)** — Mapeo semántico profundo de `conceptos`, `entidades` y `relaciones` en Neo4j.
- **Detección de Intención** — Reconoce 7 tipos: `resumir`, `analizar`, `comparar`, `localizar`, `extraer`, `tabla`, `general`
- **Coincidencia Difusa de Títulos** — Encuentra el documento correcto incluso con nombres parciales o errores tipográficos
- **Guardia de Relevancia** — Nunca devuelve un documento equivocado
- **Memoria Contextual** — Ventana deslizante de últimas 5 conversaciones

### 📄 Formatos Soportados
- **PDF** — Extracción de texto completo por página
- **DOCX** — Parser XML de párrafos (cero dependencias externas)
- **XLSX / XLS / CSV** — Resolvedor de celdas multi-hoja, estadísticas numéricas
- **PPTX** — Reconstrucción de esquema diapositiva por diapositiva
- **JSON / TXT / MD** — Parsers nativos con indexación completa

---

## ⚡ Inicio Rápido

### Requisitos Previos

| Requisito | Versión |
|:---------|:--------|
| Python | 3.10+ |
| Node.js | 18+ |
| Docker & Docker Compose | Última |
| Ollama | Última |

### Paso 1 — Clonar y Configurar

```bash
git clone https://github.com/tu-org/localbrain.git
cd localbrain
cp .env.example .env
```

### Paso 2 — Iniciar Bases de Datos (Docker)

```bash
docker-compose up -d
```

### Paso 3 — Iniciar el LLM Local (Ollama)

```bash
$env:OLLAMA_ORIGINS="*"; ollama serve       # Windows
OLLAMA_ORIGINS="*" ollama serve             # macOS/Linux
ollama pull qwen2.5:7b-instruct-q4_K_M
```

### Paso 4 — Iniciar el Backend

```bash
python -m venv venv && .\\venv\\Scripts\\Activate.ps1
pip install -r core_api/requirements.txt
python -m scripts.init_dbs
uvicorn core_api.main:app --port 8000 --reload
```

### Paso 5 — Iniciar el Frontend

```bash
cd frontend && npm install && npm run dev
```

Abre [http://localhost:3000](http://localhost:3000)

---

## 📁 Estructura del Proyecto

```
localbrain/
├── core_api/                    # Backend FastAPI
│   ├── main.py                  # Rutas API: subida, consulta, grafo
│   ├── synthesis.py             # Motor NLP + síntesis RAG + guardia DLP
│   ├── ingestion.py             # Parsers de documentos + embeddings
│   ├── databases.py             # Adaptadores Qdrant, Neo4j, PostgreSQL, Redis
│   └── mcp_server.py            # Servidor Protocolo MCP
├── frontend/                    # Interfaz Next.js 14
├── assets/
│   ├── localbrain_screenshot.png  # Captura de pantalla (arriba)
│   └── localbrain_demo.mp4        # Grabación de demostración
├── scripts/                     # Scripts de inicialización de BD
├── workers/                     # Workers de integración
├── docker-compose.yml           # Stack completo de bases de datos
└── .env.example                 # Plantilla de configuración
```

---

## 📄 Licencia

Publicado bajo la **[Licencia Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)**.

---

<div align="center">

Construido para equipos que se toman la **privacidad de datos en serio**.

*Todo local. Cero nube. 100% tuyo.*

⭐ **¡Dale una estrella al repo** si Local Brain ayuda a tu equipo!

</div>
