<div align="center">

# 🧠 Local Brain

### エンタープライズAIプラットフォーム · オンプレミス · 100%プライベート

[![ライセンス: Apache 2.0](https://img.shields.io/badge/ライセンス-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](https://nextjs.org)
[![Ollama](https://img.shields.io/badge/Ollama-ローカルLLM-FF6B35)](https://ollama.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-ベクターDB-6C5CE7)](https://qdrant.tech)
[![Neo4j](https://img.shields.io/badge/Neo4j-知識グラフ-008CC1?logo=neo4j)](https://neo4j.com)

**ドキュメントをアップロードし、何でも質問する。完全オフラインで、正確な引用付きの回答を取得。**

*クラウド不要。サブスクリプション不要。データがデバイスを離れることは一切ありません。*

---

[🇺🇸 English](README.md) · [🇪🇸 Español](README_ES.md) · [🇩🇪 Deutsch](README_DE.md) · 🇯🇵 **日本語**

</div>

---

## 🖥️ ライブプレビュー

> Local Brain がローカルで動作中 — クラウドなし、100%プライベート。

![Local Brain — チャットインターフェーススクリーンショット](assets/localbrain_screenshot.png)

---

## 🎬 デモ録画

> Local Brain の動作をご覧ください: ドキュメントのアップロード、質問、知識グラフの探索。

https://github.com/user-attachments/assets/localbrain_demo.mp4

> **注意:** ブラウザで動画が再生されない場合は、[こちらからダウンロード](assets/localbrain_demo.mp4)してください。

---

## 🚀 Local Brain とは？

Local Brain は、**プライベートでセルフホストのAIプラットフォーム**です。組織のドキュメントを、**自前のハードウェア上で動作するローカルLLM**によって完全に駆動された、検索可能でインテリジェントな知識ベースに変換します。

PDF、Wordドキュメント、Excelシート、CSV、Markdownなどのファイルをアップロードすると、システムが自動的に解析・チャンク分割・インデックス化します。AIは**高度なセマンティックNLP**でユーザーの意図を正確に理解し、**外部APIを一切呼び出しません**。

> **機密データを扱うチームに最適です** — クラウドAIサービスが使えない組織のために。

---

## 🏗️ システムアーキテクチャ

> ベクターで鮮明なインタラクティブSVGシステムアーキテクチャマップ。完全にスケーラブル、レスポンシブ、かつオフライン対応。
> **注意:** IDEやプレーンテキストリーダーをご使用の場合は、以下をクリックして Mermaid 表記を展開してください。

![システムアーキテクチャ](assets/system_architecture.svg)

<details>
<summary>💻 Mermaid クラス図コードを表示</summary>

```mermaid
graph TB
    subgraph ユーザー["👤 ユーザーインターフェース層"]
        UI["🖥️ Next.js 14 チャットUI<br/>グラスモーフィックデザイン<br/>WebSocketリアルタイム更新"]
        GRAPH["🕸️ インタラクティブ知識グラフ<br/>力指向ビジュアライゼーション<br/>ノードクリック → ファイル分析"]
        UPLOAD["📎 ファイルアップロードゾーン<br/>ドラッグ&ドロップ · マルチフォーマット"]
    end

    subgraph バックエンド["⚙️ FastAPI自律エンジン (ポート8000)"]
        direction TB
        PARSER["📄 ドキュメントパーサー<br/>PDF · DOCX · XLSX · CSV<br/>JSON · TXT · PPTX · MD"]
        NLP["🧠 NLPプロセッサー<br/>意図検出 · ファジータイトルマッチ<br/>セマンティック関連性ガード"]
        RAG["🔍 RAGパイプライン<br/>ハイブリッド検索: ベクトル + キーワード<br/>コンテキストウィンドウメモリ"]
        SYNTH["✍️ 合成エンジン<br/>構造化レスポンス生成<br/>引用フォーマット"]
        DLP["🛡️ DLPスキャナー<br/>SSN · クレジットカードブロック<br/>RBACフィルター"]
    end

    subgraph データベース["💾 データベース層"]
        QDRANT["🔷 Qdrant<br/>ベクターストア<br/>1024次元埋め込み<br/>セマンティック検索"]
        NEO4J["🕸️ Neo4j<br/>知識グラフ<br/>概念 · エンティティ<br/>関係"]
        POSTGRES["🐘 PostgreSQL<br/>ドキュメントメタデータ<br/>コンテンツストレージ<br/>ユーザーロール"]
        REDIS["⚡ Redis<br/>クエリキャッシュ<br/>WebSocketブロードキャスト<br/>Session Store"]
    end

    subgraph LLM["🤖 ローカルLLM層"]
        OLLAMA["🦙 Ollamaサーバー<br/>Qwen2.5 · Llama 3<br/>Mistral · Phi-3"]
        EMBED["📐 埋め込みエンジン<br/>1024次元ベクトル<br/>ローカル生成"]
    end

    UI --> バックエンド
    GRAPH --> バックエンド
    UPLOAD --> バックエンド
    PARSER --> QDRANT
    PARSER --> POSTGRES
    NLP --> RAG
    RAG --> QDRANT
    RAG --> POSTGRES
    RAG --> SYNTH
    SYNTH --> LLM
    バックエンド --> NEO4J
    バックエンド --> REDIS
```
</details>

---

## 🔍 クエリとRAGレスポンスフロー

> 完全なニューラル・セマンティック・ワークフロー、ファジートークン解決、意図分類、および RAG 合成パス。
> **注意:** IDEやプレーンテキストリーダーをご使用の場合は、以下をクリックして Mermaid 表記を展開してください。

![クエリとRAGレスポンスフロー](assets/query_rag_flow.svg)

<details>
<summary>💻 Mermaid フローチャートコードを表示</summary>

```mermaid
flowchart TD
    A([ユーザークエリ]) --> B{スラッシュコマンド?}
    B -- はい --> C["/connect /help /status"]
    B -- いいえ --> D{提案チップ?}
    D -- "ドキュメント要約" --> E[全ドキュメント取得
リアルな要約生成]
    D -- いいえ --> F[Redisキャッシュ検索]
    F -- ヒット --> Z([フォーマット済みレスポンス])
    F -- ミス --> G[NLP: 意図検出]
    G --> H["意図タイプ:
• 要約 · 分析
• 比較 · 場所
• 抽出 · テーブル"]
    H --> I[ファジータイトルマッチ
Jaccard + バイグラム]
    I -- 一致 --> J[PostgreSQLから
全コンテンツ直接ロード]
    I -- 不一致 --> K[ベクトル検索
Qdrantセマンティック]
    J & K --> L[NLP関連性ガード
オーバーラップ ≥ 6%]
    L -- 関連あり --> M[合成エンジン
ローカルLLM / プロシージャル]
    L -- 関連なし --> N(["⚠️ インデックス済みドキュメントに
情報が見つかりません"])
    M --> O[DLPスキャン]
    O --> Z

    style A fill:#6C5CE7,color:#fff
    style Z fill:#00B894,color:#fff
    style N fill:#E17055,color:#fff
```
</details>

---

## 📐 レイヤー構成

| レイヤー | 技術 | 目的 |
|:--------|:----|:----|
| **🖥️ チャットUI** | Next.js 14 + グラスモーフィックCSS | チャットコンソール、ファイルアップロード、知識グラフ可視化 |
| **⚙️ APIバックエンド** | FastAPI + Python 3.10+ | 取り込み、RAGパイプライン、NLP処理、RBAC、DLP |
| **🧠 NLPエンジン** | MarkItDown + カスタムNLP | Markdown正規化、意図検出、ファジータイトルマッチ |
| **🔷 ベクターDB** | Qdrant | 1024次元セマンティックチャンク、200ms以下の検索 |
| **🕸️ グラフDB** | Neo4j | GraphRAG概念関係、エンティティシナプス、知識マッピング |
| **🐘 リレーショナルDB** | PostgreSQL | ファイルメタデータ、全コンテンツ、権限、ロール |
| **⚡ キャッシュ** | Redis | クエリキャッシング、WebSocketブロードキャスト |
| **🤖 ローカルLLM** | Ollama / vLLM | プライベート埋め込み + RAG回答合成（完全オフライン） |
| **🔌 IDEブリッジ** | MCPプロトコル | Cursor IDE & Claude Desktopから直接アクセス |

---

## ✨ 主要機能

### 🔒 セキュリティとプライバシー
- **100%オンプレミス** — データがデバイスやネットワークを離れることは絶対にない
- **DLPスキャナー** — AIレスポンスからSSNとクレジットカード番号を自動ブロック
- **RBAC** — ドキュメントとユーザーグループごとのロールベースアクセス制御
- **オフライン動作** — セットアップ後はインターネットなしで完全に動作

### 🧠 高度なAI知識エンジン
- **意図検出** — 7タイプを認識: `要約`, `分析`, `比較`, `場所確認`, `抽出`, `テーブル`, `一般`
- **ファジータイトルマッチング** — 部分的な名前やタイプミスでも正しいドキュメントを検索
- **関連性ガード** — 間違ったドキュメントを提供することはない
- **コンテキストメモリ** — 最後の5回の会話のスライディングウィンドウ

### 📄 対応ファイル形式

| 形式 | 拡張子 | 分析タイプ |
|:-----|:------|:---------|
| PDF | `.pdf` | ページごとの全文抽出 |
| Word | `.docx` | パラグラフXMLパーサー |
| Excel | `.xlsx`, `.xls` | マルチシートセルリゾルバー + 統計 |
| CSV | `.csv` | 行/列の構造化テキスト |
| PowerPoint | `.pptx` | スライドごとのアウトライン |
| JSON | `.json` | フォーマット済み構造表示 |
| テキスト | `.txt`, `.md` | チャンク付き生テキスト |
| 画像 | `.png`, `.jpg` | レジストリ + ダウンロードリンク |

---

## ⚡ クイックスタート

### 前提条件

| 要件 | バージョン |
|:----|:---------|
| Python | 3.10+ |
| Node.js | 18+ |
| Docker & Docker Compose | 最新 |
| Ollama | 最新 |

### ステップ 1 — クローンと設定

```bash
git clone https://github.com/your-org/localbrain.git
cd localbrain
cp .env.example .env
```

### ステップ 2 — データベース起動（Docker）

```bash
docker-compose up -d
```

### ステップ 3 — ローカルLLM起動（Ollama）

```bash
$env:OLLAMA_ORIGINS="*"; ollama serve       # Windows
OLLAMA_ORIGINS="*" ollama serve             # macOS/Linux
ollama pull qwen2.5:7b-instruct-q4_K_M
```

### ステップ 4 — バックエンド起動

```bash
python -m venv venv && .\\venv\\Scripts\\Activate.ps1
pip install -r core_api/requirements.txt
python -m scripts.init_dbs
uvicorn core_api.main:app --port 8000 --reload
```

### ステップ 5 — フロントエンド起動

```bash
cd frontend && npm install && npm run dev
```

[http://localhost:3000](http://localhost:3000) を開く

---

## 📁 プロジェクト構造

```
localbrain/
├── core_api/                    # FastAPIバックエンド
│   ├── main.py                  # APIルート: アップロード、クエリ、グラフ
│   ├── synthesis.py             # NLPエンジン + RAG合成 + DLPガード
│   ├── ingestion.py             # ドキュメントパーサー + 埋め込みパイプライン
│   ├── databases.py             # Qdrant, Neo4j, PostgreSQL, Redisアダプター
│   └── mcp_server.py            # MCPプロトコルサーバー
├── frontend/                    # Next.js 14 チャットUI
├── assets/
│   ├── localbrain_screenshot.png  # UIスクリーンショット（上記参照）
│   └── localbrain_demo.mp4        # スクリーン録画デモ
├── scripts/                     # DB初期化スクリプト
├── workers/                     # バックグラウンド取り込みワーカー
├── docker-compose.yml           # データベーススタック定義
└── .env.example                 # 設定テンプレート
```

---

## 📄 ライセンス

**[Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)** の下でリリース。

---

<div align="center">

**データプライバシーを真剣に考えるチーム**のために作られました。

*すべてローカル。クラウドなし。100%あなたのもの。*

⭐ Local Brain があなたのチームのプライバシー保護に役立てば、**スターをお願いします！**

</div>
