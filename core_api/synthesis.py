import os
import re
import math
import httpx
from typing import List, Dict, Any, Optional
from .logger import get_logger

logger = get_logger("synthesis")


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase, strip punctuation/underscores/dashes, collapse whitespace."""
    text = text.lower()
    text = re.sub(r'[_\-\.]+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _ngrams(tokens: List[str], n: int) -> List[str]:
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


# ---------------------------------------------------------------------------
# NLPProcessor
# ---------------------------------------------------------------------------

class NLPProcessor:
    """
    Advanced NLP analyzer:
    - Semantic intent detection (summarize, compare, locate, list, analyse…)
    - Fuzzy document title matching via token overlap + n-gram similarity
    - Relevance scoring between query ↔ retrieved chunks
    - Negation, format-hint, and conversational detection
    """

    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "at",
        "by", "for", "with", "about", "against", "between", "into", "through",
        "during", "before", "after", "above", "below", "to", "from", "up", "down",
        "in", "out", "on", "off", "over", "under", "again", "further", "once",
        "here", "there", "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such", "own", "same", "so", "than", "too", "very",
        "can", "will", "just", "should", "now", "is", "was", "were", "are",
        "am", "be", "been", "being", "have", "has", "had", "doing", "do", "does",
        "did", "of", "me", "my", "its", "it", "this", "that", "these", "those",
        "i", "you", "he", "she", "we", "they", "what", "which", "who", "how",
        "where", "why", "please", "could", "would", "tell", "give", "show",
        "let", "know", "need", "want", "make",
    }

    # Intent taxonomy ─ ordered from most-specific to least
    INTENT_PATTERNS = {
        "summarize": re.compile(
            r'\b(summar(?:ize|ise|y|ze)|summerze|overview|brief|recap|tldr|gist|synopsis|abstract|digest)\b',
            re.I),
        "analyse": re.compile(
            r'\b(analys[ei]s|analyz[ei]|audit|breakdown|deep.?dive|examine|inspect|review|evaluate)\b',
            re.I),
        "compare": re.compile(
            r'\b(compar[ei]|vs\.?|versus|differ(?:ence)?|contrast|between)\b', re.I),
        "locate": re.compile(
            r'\b(where|locat(?:e|ion)|stored|path|find|directory|folder)\b', re.I),
        "list": re.compile(
            r'\b(list|enumerate|show\s+all|all\s+files|index(?:ed)?|all\s+doc)\b', re.I),
        "download": re.compile(
            r'\b(download|fetch|export|save|get\s+file|retrieve\s+file)\b', re.I),
        "table": re.compile(
            r'\b(table|tabular|spreadsheet|grid|rows?\s+and\s+columns?|matrix)\b', re.I),
        "extract": re.compile(
            r'\b(extract|pull\s+out|get\s+data|find\s+(?:in|from)|what\s+(?:is|are|does))\b',
            re.I),
        "general": re.compile(r'.*', re.I),  # catch-all
    }

    SYNONYMS = {
        "document": {"doc", "file", "report", "paper", "record", "sheet",
                     "pdf", "docx", "xlsx", "csv", "txt", "pptx", "md"},
        "show":     {"display", "render", "give", "list", "present", "view", "print"},
        "download": {"fetch", "get", "retrieve", "obtain", "export", "save"},
        "table":    {"tabular", "grid", "matrix", "rows", "columns"},
        "list":     {"bullets", "bulletpoints", "points", "enumerate"},
    }

    # ---------------------------------------------------------------------------
    @staticmethod
    def tokenize(text: str) -> List[str]:
        return re.findall(r'\b\w{2,}\b', text.lower())

    @classmethod
    def clean_tokens(cls, tokens: List[str]) -> List[str]:
        return [t for t in tokens if t not in cls.STOPWORDS]

    # ---------------------------------------------------------------------------
    # Intent
    # ---------------------------------------------------------------------------
    @classmethod
    def detect_intent(cls, query: str) -> str:
        for intent, pattern in cls.INTENT_PATTERNS.items():
            if pattern.search(query):
                return intent
        return "general"

    # ---------------------------------------------------------------------------
    # Negation
    # ---------------------------------------------------------------------------
    @classmethod
    def analyze_negation(cls, text: str) -> bool:
        markers = {"not", "no", "never", "without", "none", "neither",
                   "nor", "cannot", "can't", "won't", "don't", "didn't", "isn't"}
        return any(m in cls.tokenize(text) for m in markers)

    # ---------------------------------------------------------------------------
    # Fuzzy document-title matching
    # ---------------------------------------------------------------------------
    @classmethod
    def match_document_title(
        cls,
        query: str,
        doc_titles: List[str],
        threshold: float = 0.30,
    ) -> Optional[str]:
        """
        Returns the best-matching document title for a query, or None.

        Scoring (weighted union):
          • Exact substring (norm query contains norm title-no-ext) → 1.0
          • Token Jaccard overlap between query tokens and title tokens
          • Bigram / trigram overlap bonus
        Only returns a match when score ≥ threshold AND the match is meaningfully
        better than the second-best candidate (gap ≥ 0.15) to avoid ambiguous picks.
        """
        if not doc_titles:
            return None

        norm_q = _normalize(query)
        q_tokens = set(cls.clean_tokens(cls.tokenize(norm_q)))

        scored = []
        for title in doc_titles:
            norm_t = _normalize(title)
            # Remove file extension for matching
            norm_t_ne = re.sub(r'\.\w{2,5}$', '', norm_t).strip()
            t_tokens = set(cls.tokenize(norm_t_ne))
            t_tokens_clean = set(cls.clean_tokens(list(t_tokens)))

            score = 0.0

            # 1. Exact containment bonus (very strong signal)
            if norm_t_ne and norm_t_ne in norm_q:
                score += 1.0
            elif norm_t_ne and norm_q in norm_t_ne:
                score += 0.7

            # 2. Jaccard token similarity
            if q_tokens and t_tokens_clean:
                inter = q_tokens & t_tokens_clean
                union = q_tokens | t_tokens_clean
                jaccard = len(inter) / len(union) if union else 0.0
                score += jaccard * 0.8

            # 3. n-gram overlap (bigrams)
            q_bg = set(_ngrams(cls.clean_tokens(cls.tokenize(norm_q)), 2))
            t_bg = set(_ngrams(cls.clean_tokens(list(t_tokens)), 2))
            if q_bg and t_bg:
                bg_score = len(q_bg & t_bg) / max(len(q_bg), 1)
                score += bg_score * 0.4

            # 4. Bonus if individual title words appear literally in query
            for tok in t_tokens_clean:
                if len(tok) >= 4 and tok in norm_q:
                    score += 0.15

            scored.append((score, title))

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_title = scored[0]
        second_score = scored[1][0] if len(scored) > 1 else 0.0

        logger.info(
            f"[NLP] Doc-title match: best='{best_title}' ({best_score:.3f}), "
            f"second=({second_score:.3f})"
        )

        if best_score < threshold:
            return None
        # Require a meaningful gap only when the best score is not very high
        if best_score < 0.70 and (best_score - second_score) < 0.10:
            logger.info("[NLP] Ambiguous title match — not committing to one document.")
            return None

        return best_title

    # ---------------------------------------------------------------------------
    # Chunk relevance
    # ---------------------------------------------------------------------------
    @classmethod
    def calculate_similarity_score(cls, query: str, context: str) -> float:
        q_tokens = set(cls.clean_tokens(cls.tokenize(query)))
        c_tokens = set(cls.clean_tokens(cls.tokenize(context)))
        if not q_tokens:
            return 1.0
        inter = q_tokens & c_tokens
        bonus = 0.0
        for qt in q_tokens - c_tokens:
            for key, syns in cls.SYNONYMS.items():
                if qt in syns or qt == key:
                    if any(s in c_tokens for s in syns):
                        bonus += 0.5
                        break
        return (len(inter) + bonus) / len(q_tokens)

    @classmethod
    def check_context_relevance(
        cls, query: str, chunks: List[Dict[str, Any]], threshold: float = 0.08
    ) -> bool:
        if not chunks:
            return False
        full_ctx = " ".join(c.get("content", "") for c in chunks)
        score = cls.calculate_similarity_score(query, full_ctx)
        neg = cls.analyze_negation(query)
        logger.info(
            f"[NLP] Relevance score={score:.4f}, negation={neg}, threshold={threshold}"
        )
        return score >= threshold

    # ---------------------------------------------------------------------------
    # Conversational check
    # ---------------------------------------------------------------------------
    @classmethod
    def is_conversational_or_friendly(cls, query: str) -> bool:
        q = query.lower().strip()
        greetings = {
            "hello", "hi", "hey", "hola", "greetings",
            "good morning", "good afternoon", "good evening",
            "how are you", "who are you", "what is your name",
            "what are you", "help", "/help", "thank you", "thanks",
        }
        if q in greetings or any(q.startswith(g) for g in greetings if len(g) > 3):
            return True
        tokens = cls.tokenize(query)
        if len(tokens) <= 3:
            doc_kw = {
                "document", "file", "xlsx", "pdf", "docx", "csv", "txt",
                "data", "upload", "audit", "plan", "spec", "report",
            }
            if not any(t in doc_kw for t in tokens):
                return True
        return False

    # ---------------------------------------------------------------------------
    # Download detection
    # ---------------------------------------------------------------------------
    @classmethod
    def detect_download_request(
        cls, query: str, available_docs: List[str] = None
    ) -> List[str]:
        q_tokens = cls.tokenize(query)
        dl_syns = cls.SYNONYMS["download"] | cls.SYNONYMS["show"] | {"download", "show"}
        is_dl = any(t in q_tokens for t in dl_syns)
        doc_intent = any(t in q_tokens for t in cls.SYNONYMS["document"])
        if not (is_dl or doc_intent):
            return []
        matched = []
        if available_docs:
            for doc in available_docs:
                dc = _normalize(doc)
                parts = [p for p in dc.split() if len(p) > 2]
                if dc in _normalize(query) or any(p in q_tokens for p in parts):
                    matched.append(doc)
        return matched

    # ---------------------------------------------------------------------------
    # Markdown helpers
    # ---------------------------------------------------------------------------
    @staticmethod
    def construct_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
        if not headers or not rows:
            return ""
        col_w = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_w):
                    col_w[i] = max(col_w[i], len(str(cell)))
        header_line = "| " + " | ".join(h.ljust(col_w[i]) for i, h in enumerate(headers)) + " |"
        sep_line    = "| " + " | ".join("-" * col_w[i] for i in range(len(headers)))       + " |"
        row_lines   = [
            "| " + " | ".join(str(c).ljust(col_w[i]) for i, c in enumerate(row)) + " |"
            for row in rows
        ]
        return "\n".join([header_line, sep_line] + row_lines)


# ---------------------------------------------------------------------------
# SynthesisEngine
# ---------------------------------------------------------------------------

class SynthesisEngine:
    """
    Secure, on-premise synthesis engine.

    Priority order:
      1. Slash-command intercepts (handled in main.py before reaching here)
      2. Attempt local LLM (Ollama / vLLM OpenAI-compatible API)
      3. Rich procedural fallback grounded strictly in the retrieved chunks
    """

    def __init__(self):
        self.llm_url   = os.getenv("VLLM_API_URL",      "http://localhost:11434/v1")
        self.llm_model = os.getenv("LOCAL_MODEL_NAME",  "qwen2.5:3b-instruct")

    # -----------------------------------------------------------------------
    async def synthesize(
        self,
        query: str,
        top_chunks: List[Dict[str, Any]],
        history: List[Dict[str, str]] = None,
        available_doc_titles: List[str] = None,
    ) -> str:
        """
        Synthesize a grounded answer.

        Parameters
        ----------
        query              : Raw user query string
        top_chunks         : Ranked list of retrieved context dicts
                             (keys: content, title, uploaded_at)
        history            : Sliding window of {query, answer} pairs
        available_doc_titles : All document titles from the database
                               (used for fuzzy-match fallback)
        """
        available_docs = available_doc_titles or []
        if not available_docs and os.path.exists("uploaded_docs"):
            available_docs = os.listdir("uploaded_docs")

        # ── 1. Download / view document link request ──────────────────────
        matched_dl = NLPProcessor.detect_download_request(query, available_docs)
        if matched_dl:
            links = "\n".join(
                f"- **[{d}](http://127.0.0.1:8000/documents/{d})**" for d in matched_dl
            )
            return (
                "I found the following document(s) matching your request. "
                "You can view or download them directly:\n\n"
                f"{links}\n\n"
                "Let me know if you'd like me to extract specific data or summarise the content!"
            )

        # ── 2. Relevance guard (only for document-focused queries) ─────────
        intent = NLPProcessor.detect_intent(query)
        is_conv = NLPProcessor.is_conversational_or_friendly(query)

        if not is_conv and intent not in {"list", "locate"}:
            if top_chunks:
                if not NLPProcessor.check_context_relevance(query, top_chunks, threshold=0.06):
                    logger.warning(
                        f"[Synthesis] Low relevance — chunks don't match query '{query}'. "
                        "Returning 'Not Found'."
                    )
                    return (
                        "⚠️ **Information not found in the indexed documents.**\n\n"
                        "The documents I have do not appear to contain an answer to your question. "
                        "Please upload the relevant file or rephrase your query."
                    )
            else:
                doc_kw = {"document", "file", "upload", "ingested", "vault"}
                file_ext = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".json"}
                q_l = query.lower()
                if any(w in q_l for w in doc_kw) and any(e in q_l for e in file_ext):
                    return "⚠️ **Information not found in the indexed documents.**"

        # ── 3. Build LLM system prompt ─────────────────────────────────────
        system_prompt = self._build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]

        # Append conversation history (sliding window)
        if history:
            for turn in history:
                messages.append({"role": "user",      "content": turn.get("query", "")})
                messages.append({"role": "assistant", "content": turn.get("answer", "")})

        # Build user message with grounded context
        if top_chunks:
            ctx_blocks = []
            for c in top_chunks:
                ts = c.get("uploaded_at", "N/A")
                ctx_blocks.append(
                    f"--- Source: {c.get('title', 'Unknown')} (uploaded: {ts}) ---\n"
                    f"{c.get('content', '')}"
                )
            context_str  = "\n\n".join(ctx_blocks)
            user_content = (
                f"Context from indexed documents:\n\n{context_str}\n\n"
                f"User Question: {query}\n\n"
                "Answer (be specific to the documents above, cite the source title and "
                "upload date, use markdown formatting with tables/lists as appropriate):"
            )
        else:
            user_content = query

        messages.append({"role": "user", "content": user_content})

        logger.info(
            f"[Synthesis] Synthesizing answer for '{query}' "
            f"| chunks={len(top_chunks)} | history={len(history or [])}"
        )

        # ── 4. Local LLM attempt ───────────────────────────────────────────
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.llm_url}/chat/completions"
                payload = {
                    "model":       self.llm_model,
                    "messages":    messages,
                    "temperature": 0.2,
                    "max_tokens":  1200,
                }
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data   = resp.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    logger.info("[Synthesis] Answer generated by local LLM.")
                    return answer
                raise ValueError(f"HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"[Synthesis] Local LLM unavailable ({e}). Using procedural fallback.")

        # ── 5. Procedural fallback ─────────────────────────────────────────
        return self._procedural_fallback(query, top_chunks, intent, is_conv)

    # -----------------------------------------------------------------------
    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "You are Local Brain, a private, on-premise AI Knowledge Engine.\n"
            "You behave exactly like a highly capable AI assistant — giving rich, "
            "formatted, structured answers — but you run 100% locally.\n\n"
            "## Context Data Format\n"
            "The context provided to you has been converted into rich Markdown via MarkItDown. "
            "It is highly structured. Use this structure to give deep semantic responses.\n\n"
            "## Response Formatting Rules\n"
            "- Always match your response format to the user's intent:\n"
            "  • Summary request  → executive summary with bullet highlights\n"
            "  • Analysis request → structured sections with tables/lists\n"
            "  • Question         → concise, direct answer with citations\n"
            "  • List request     → clean markdown list or table\n"
            "  • Compare request  → side-by-side table\n"
            "- Use **bold** for key terms, `code` for filenames/paths.\n"
            "- Always cite the source document name and upload timestamp.\n"
            "- Use markdown tables when presenting numerical or comparative data.\n\n"
            "## Grounding Rules\n"
            "- Ground ALL factual statements in the provided Markdown Context.\n"
            "- If the Context does not contain the answer, say:\n"
            "  '⚠️ This information was not found in the indexed documents.'\n"
            "- NEVER hallucinate facts, filenames, or figures not in the Context.\n"
            "- For general questions (greetings, math, code), use your knowledge.\n\n"
            "## Citation & File Links\n"
            "When referencing a document, write:\n"
            "> According to **DocumentName** (uploaded: YYYY-MM-DD HH:MM:SS), …\n"
            "You MUST also append a clickable download link immediately after referencing a file, in this EXACT format:\n"
            "`[Download DocumentName](/documents/DocumentName)`\n"
        )

    # -----------------------------------------------------------------------
    def _procedural_fallback(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        intent: str,
        is_conv: bool,
    ) -> str:
        """
        Rich procedural synthesis that strictly uses text from the retrieved chunks.
        Never invents data — returns 'not found' if chunks are empty or irrelevant.
        """

        # ── Conversational ──────────────────────────────────────────────────
        if is_conv:
            return self._conversational_response(query)

        # ── No chunks ───────────────────────────────────────────────────────
        if not chunks:
            return (
                "⚠️ **Information not found in the indexed documents.**\n\n"
                "I could not find any document content related to your query. "
                "Please upload the relevant file or ask about a different topic."
            )

        doc_title   = chunks[0].get("title", "Document")
        uploaded_at = chunks[0].get("uploaded_at", "N/A")
        full_text   = "\n".join(ch.get("content", "") for ch in chunks)
        clean_title = doc_title.lower()
        q_lower     = query.lower()

        logger.info(
            f"[Synthesis Fallback] intent={intent}, doc='{doc_title}', "
            f"text_len={len(full_text)}"
        )

        # ── Location query ──────────────────────────────────────────────────
        if intent == "locate" or any(
            kw in q_lower for kw in ["where is", "location", "file path", "stored", "find file"]
        ):
            dl = f"[Download `{doc_title}`](http://127.0.0.1:8000/documents/{doc_title})"
            return (
                f"### 📍 Document Location\n\n"
                f"**`{doc_title}`** is indexed and securely stored in the local vault.\n\n"
                f"| Property | Value |\n"
                f"| :--- | :--- |\n"
                f"| **Registry Path** | `uploaded_docs/{doc_title}` |\n"
                f"| **Indexed At** | {uploaded_at} |\n"
                f"| **Access** | On-premise only |\n\n"
                f"📥 {dl}"
            )

        # ── Image/visual ────────────────────────────────────────────────────
        if re.search(r'\.(png|jpe?g|gif|webp|bmp|svg)$', clean_title):
            dl = f"[View `{doc_title}`](http://127.0.0.1:8000/documents/{doc_title})"
            return (
                f"### 🖼️ Visual Asset: `{doc_title}`\n\n"
                f"*Registered at: {uploaded_at}*\n\n"
                f"This is a visual/image asset stored locally at `uploaded_docs/{doc_title}`.\n\n"
                f"📥 {dl}"
            )

        # ── Summarize ───────────────────────────────────────────────────────
        if intent == "summarize":
            return self._synthesize_summary(doc_title, uploaded_at, full_text, query)

        # ── Analyse / deep-dive ─────────────────────────────────────────────
        if intent in {"analyse", "extract"}:
            # Route to file-type specific analyser
            if re.search(r'\.(xlsx|xls|csv)$', clean_title) or _has_tabular_data(full_text):
                return self._analyse_spreadsheet(doc_title, uploaded_at, full_text, query)
            elif clean_title.endswith(".pptx"):
                return self._analyse_presentation(doc_title, uploaded_at, full_text)
            else:
                return self._analyse_text_document(doc_title, uploaded_at, full_text, query)

        # ── Compare ─────────────────────────────────────────────────────────
        if intent == "compare":
            titles = list({c.get("title", "") for c in chunks})
            if len(titles) >= 2:
                return self._compare_documents(chunks)

        # ── Table request ───────────────────────────────────────────────────
        if intent == "table":
            if re.search(r'\.(xlsx|xls|csv)$', clean_title) or _has_tabular_data(full_text):
                return self._analyse_spreadsheet(doc_title, uploaded_at, full_text, query)

        # ── General question — attempt keyword-targeted answer ──────────────
        return self._targeted_answer(query, doc_title, uploaded_at, full_text)

    # -----------------------------------------------------------------------
    # Rich synthesisers
    # -----------------------------------------------------------------------

    def _synthesize_summary(
        self, title: str, uploaded_at: str, full_text: str, query: str
    ) -> str:
        """
        Generates a real executive summary from the document's actual text.
        Extracts key sentences, not made-up ones.
        """
        sentences = _extract_sentences(full_text, min_len=40)
        word_count = len(full_text.split())
        char_count = len(full_text)

        # Pick top sentences by length and position (first + dense middle)
        highlights = sentences[:2] + (sentences[len(sentences)//2: len(sentences)//2 + 2] if len(sentences) > 4 else [])
        highlights = highlights[:5]

        bullet_lines = "\n".join(f"- {s[:200]}{'...' if len(s)>200 else ''}" for s in highlights) or \
                       "- No detailed text could be extracted from this document."

        # Detect domain
        domain = _infer_domain(title, full_text)

        return (
            f"### 📄 Document Summary: `{title}`\n\n"
            f"> According to **{title}** (uploaded: {uploaded_at})\n\n"
            f"**Domain**: {domain}\n"
            f"**Document Size**: ~{word_count:,} words, {char_count:,} characters\n\n"
            f"#### 🔑 Key Points\n\n"
            f"{bullet_lines}\n\n"
            f"#### 📊 Document Statistics\n\n"
            f"| Metric | Value |\n"
            f"| :--- | :--- |\n"
            f"| Total Words | {word_count:,} |\n"
            f"| Total Characters | {char_count:,} |\n"
            f"| Paragraphs Detected | {full_text.count(chr(10))+1} |\n"
            f"| Indexed At | {uploaded_at} |\n\n"
            f"Would you like a deeper analysis, specific data extraction, or a compliance audit?"
        )

    def _analyse_spreadsheet(
        self, title: str, uploaded_at: str, full_text: str, query: str
    ) -> str:
        numbers = [float(n) for n in re.findall(r'\b\d+(?:[,\d]*\d)?(?:\.\d+)?\b', full_text.replace(",", "")) if float(n.replace(",","")) < 1e12]
        total_sum = sum(numbers[:50]) if numbers else 0
        avg_val   = total_sum / len(numbers[:50]) if numbers else 0
        max_val   = max(numbers[:50]) if numbers else 0

        # Extract labeled rows (label, value pairs)
        rows_md = []
        for line in full_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2 and parts[0] and parts[1]:
                label = parts[0][:50]
                value = parts[1][:30]
                extra = parts[2][:30] if len(parts) > 2 else ""
                rows_md.append(f"| **{label}** | `{value}` | {extra} |")
            if len(rows_md) >= 10:
                break

        if not rows_md:
            rows_md = ["| *No structured rows detected* | — | — |"]

        rows_str = "\n".join(rows_md)
        return (
            f"### 📊 Spreadsheet Analysis: `{title}`\n\n"
            f"> According to **{title}** (uploaded: {uploaded_at})\n\n"
            f"#### 📋 Data Rows\n\n"
            f"| Label / Metric | Value | Notes |\n"
            f"| :--- | :--- | :--- |\n"
            f"{rows_str}\n\n"
            f"#### 🔢 Computed Statistics\n\n"
            f"| Statistic | Value |\n"
            f"| :--- | :--- |\n"
            f"| **Sum (first 50 numeric values)** | `{total_sum:,.2f}` |\n"
            f"| **Maximum Value** | `{max_val:,.2f}` |\n"
            f"| **Average Value** | `{avg_val:,.2f}` |\n\n"
            f"Would you like me to filter by a specific category, calculate margins, or export a subset?"
        )

    def _analyse_presentation(self, title: str, uploaded_at: str, full_text: str) -> str:
        slides = []
        current = []
        for line in full_text.split("\n"):
            if ("slide" in line.lower() or "---" in line or len(line.strip()) > 60) and current:
                slides.append(current)
                current = []
            if line.strip():
                current.append(line.strip())
        if current:
            slides.append(current)

        slide_items = []
        for i, sl in enumerate(slides[:6]):
            hdr  = sl[0][:80] if sl else f"Slide {i+1}"
            body = "\n   - ".join(s[:90] for s in sl[1:4]) if len(sl) > 1 else "Content not extracted."
            slide_items.append(f"**🖥️ Slide {i+1}: {hdr}**\n   - {body}")

        slides_str = "\n\n".join(slide_items) if slide_items else "No slides could be parsed."

        return (
            f"### 🖥️ Presentation Analysis: `{title}`\n\n"
            f"> According to **{title}** (uploaded: {uploaded_at})\n\n"
            f"#### 📋 Slide Outline\n\n"
            f"{slides_str}\n\n"
            f"Would you like a specific slide's content or a full transcript?"
        )

    def _analyse_text_document(
        self, title: str, uploaded_at: str, full_text: str, query: str
    ) -> str:
        sentences = _extract_sentences(full_text, min_len=50)
        domain    = _infer_domain(title, full_text)

        # Keyword-targeted highlight: find sentences most relevant to query
        q_tokens  = set(NLPProcessor.clean_tokens(NLPProcessor.tokenize(query)))
        scored_sents = []
        for s in sentences:
            s_tokens = set(NLPProcessor.tokenize(s))
            overlap  = len(q_tokens & s_tokens)
            scored_sents.append((overlap, s))
        scored_sents.sort(key=lambda x: x[0], reverse=True)
        top_sents = [s for _, s in scored_sents[:5]]

        bullet_lines = "\n".join(
            f"- {s[:250]}{'...' if len(s)>250 else ''}" for s in top_sents
        ) or "- No relevant content could be extracted."

        return (
            f"### 📄 Document Analysis: `{title}`\n\n"
            f"> According to **{title}** (uploaded: {uploaded_at})\n\n"
            f"**Domain**: {domain}\n\n"
            f"#### 🔍 Most Relevant Passages (to your query)\n\n"
            f"{bullet_lines}\n\n"
            f"#### 📊 Document Overview\n\n"
            f"| Property | Value |\n"
            f"| :--- | :--- |\n"
            f"| **Total Words** | {len(full_text.split()):,} |\n"
            f"| **Total Characters** | {len(full_text):,} |\n"
            f"| **Domain** | {domain} |\n"
            f"| **Uploaded** | {uploaded_at} |\n\n"
            f"Ask me for a full summary, a compliance check, or to extract specific terms."
        )

    def _targeted_answer(
        self, query: str, title: str, uploaded_at: str, full_text: str
    ) -> str:
        """
        Finds the most relevant passage in the document for a specific question.
        """
        q_tokens  = set(NLPProcessor.clean_tokens(NLPProcessor.tokenize(query)))
        sentences = _extract_sentences(full_text, min_len=20)

        # Score each sentence by token overlap with query
        scored = []
        for s in sentences:
            s_toks = set(NLPProcessor.tokenize(s))
            score  = len(q_tokens & s_toks)
            scored.append((score, s))
        scored.sort(key=lambda x: x[0], reverse=True)

        best_passages = [s for sc, s in scored[:4] if sc > 0]

        if not best_passages:
            return (
                f"⚠️ **Could not find a specific answer in `{title}`.**\n\n"
                f"The document is indexed (uploaded: {uploaded_at}) but does not "
                f"appear to contain the exact information you are looking for.\n\n"
                f"Would you like a full summary or analysis of this document instead?"
            )

        bullet_lines = "\n".join(
            f"- {s[:280]}{'...' if len(s)>280 else ''}" for s in best_passages
        )

        return (
            f"### 🔍 Answer from `{title}`\n\n"
            f"> According to **{title}** (uploaded: {uploaded_at})\n\n"
            f"Here are the most relevant passages from the document:\n\n"
            f"{bullet_lines}\n\n"
            f"For a deeper analysis, ask me to *summarise* or *analyse* this document."
        )

    def _compare_documents(self, chunks: List[Dict[str, Any]]) -> str:
        by_doc: Dict[str, List[str]] = {}
        for c in chunks:
            t = c.get("title", "Unknown")
            by_doc.setdefault(t, []).append(c.get("content", ""))

        titles = list(by_doc.keys())
        rows   = []
        all_texts = {t: " ".join(by_doc[t]) for t in titles}

        props = ["Word Count", "Key Topics (first 5 words)", "Uploaded"]
        for prop in props:
            row = [prop]
            for t in titles[:3]:
                txt = all_texts[t]
                if prop == "Word Count":
                    row.append(str(len(txt.split())))
                elif prop == "Key Topics (first 5 words)":
                    kw = " ".join(
                        NLPProcessor.clean_tokens(NLPProcessor.tokenize(txt))[:5]
                    )
                    row.append(kw[:60])
                else:
                    row.append(chunks[0].get("uploaded_at", "N/A"))
            rows.append(row)

        headers = ["Property"] + [t[:30] for t in titles[:3]]
        table   = NLPProcessor.construct_markdown_table(headers, rows)

        return (
            f"### ⚖️ Document Comparison\n\n"
            f"{table}\n\n"
            f"Ask me for a deeper comparison on a specific aspect."
        )

    # -----------------------------------------------------------------------
    @staticmethod
    def _conversational_response(query: str) -> str:
        q = query.lower().strip()
        if "help" in q or q.startswith("/help"):
            return (
                "👋 **Welcome to Local Brain — Your Private AI Knowledge Engine!**\n\n"
                "Here is what I can do:\n\n"
                "| Command / Question | What I Do |\n"
                "| :--- | :--- |\n"
                "| *Summarize [document name]* | Executive summary of any uploaded file |\n"
                "| *Analyse [document name]* | Deep-dive: tables, stats, key passages |\n"
                "| *Where is [document name]?* | File registry path and download link |\n"
                "| *List all indexed files* | Full table of uploaded documents |\n"
                "| *Compare [doc A] and [doc B]* | Side-by-side property comparison |\n"
                "| *[Any question about your docs]* | Grounded RAG answer with citations |\n\n"
                "**Integrations**: Use `/connect slack`, `/connect gmail`, etc.\n\n"
                "How can I help you today?"
            )
        elif any(p in q for p in ["who are you", "your name", "what are you"]):
            return (
                "🤖 I am **Local Brain**, your private on-premise AI Knowledge Engine.\n\n"
                "I index your documents, map concepts into a knowledge graph, and answer "
                "questions with full citations — 100% locally, zero data leaves your machine.\n\n"
                "Type `/help` for a full feature list, or upload a document to get started!"
            )
        elif "thank" in q:
            return "You're very welcome! Let me know if there's anything else I can help with. 😊"
        else:
            return (
                "Hello! 👋 I'm **Local Brain**, your private AI companion.\n\n"
                "You can ask me questions about your uploaded documents, request summaries, "
                "analyse data files, or type `/help` to see all features."
            )


# ---------------------------------------------------------------------------
# DLP Guard
# ---------------------------------------------------------------------------

class DLPScope:
    """Data Loss Prevention: scans output for sensitive patterns."""

    @staticmethod
    def scan_output(text: str) -> bool:
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
            raise ValueError("DLP Violation: SSN pattern detected in output.")
        if re.search(r'\b(?:\d[ -]*?){13,16}\b', text):
            raise ValueError("DLP Violation: Credit card pattern detected in output.")
        return True


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_sentences(text: str, min_len: int = 30) -> List[str]:
    """Split text into clean sentences above min_len characters."""
    raw = re.split(r'(?<=[.!?])\s+|\n{2,}', text)
    cleaned = []
    for s in raw:
        s = s.strip()
        if len(s) >= min_len:
            cleaned.append(s)
    return cleaned


def _has_tabular_data(text: str) -> bool:
    """Heuristic: does this text look like it came from a spreadsheet?"""
    comma_lines = sum(1 for line in text.split("\n") if line.count(",") >= 2)
    return comma_lines > 3


def _infer_domain(title: str, text: str) -> str:
    title_l = title.lower()
    text_l  = text.lower()
    if any(k in title_l for k in ["ai", "llm", "machine", "neural", "model"]):
        return "Artificial Intelligence & Machine Learning"
    if any(k in title_l for k in ["finance", "financial", "budget", "revenue", "opex"]):
        return "Finance & Budget Management"
    if any(k in title_l for k in ["security", "auth", "keycloak", "vault", "dlp"]):
        return "Security & Access Control"
    if any(k in title_l for k in ["api", "backend", "server", "database", "db"]):
        return "Software Engineering & Infrastructure"
    if any(k in title_l for k in ["emotion", "bridge", "scale"]):
        return "Emotional Analytics & Scaling"
    if any(k in title_l for k in ["team", "hack", "vaidhya"]):
        return "Team Operations & Hackathon"
    if any(k in title_l for k in ["primed", "prime"]):
        return "Primed AI & Product Documentation"
    if any(k in text_l for k in ["grade", "cgpa", "gpa", "marks", "semester"]):
        return "Academic Records & Grading"
    return "General Documentation"
