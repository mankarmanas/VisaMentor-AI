# VisaMentor AI

An AI-powered F1 student visa assistant built with a production-grade RAG (Retrieval Augmented Generation) pipeline. Provides accurate, sourced answers to F1 visa questions using official USCIS, ICE, and SEVP documentation.

---

## What it does

- Answers F1 visa questions (OPT, STEM OPT, CPT, EAD, SEVIS, grace periods)
- Retrieves answers only from official government sources — never hallucinates
- Cites every source with URL
- Blocks out-of-scope questions automatically
- Maintains multi-turn conversation history per session

---

## Architecture

```
User Question
      ↓
Intent Classification (Claude Haiku)
      ↓ visa question         ↓ greeting/out-of-scope
Hybrid Retrieval          Skip retrieval
  Dense (OpenAI)
  + Sparse (BM25)
      ↓
Pinecone Vector DB (dotproduct metric)
      ↓
Cohere Reranker (cross-encoder)
5 chunks → top 3
      ↓
Claude Sonnet — Answer Generation
      ↓
Guardrails — Knowledge Leakage Check
      ↓
Answer + Sources → User
```

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| LLM | Claude Sonnet 4.6 (Anthropic) |
| Intent classifier | Claude Haiku 4.5 |
| Embeddings | OpenAI text-embedding-3-large (3072 dims) |
| Vector DB | Pinecone (dotproduct metric, serverless) |
| Sparse retrieval | BM25 via pinecone-text |
| Reranker | Cohere rerank-english-v3.0 (cross-encoder) |
| API framework | FastAPI |
| Language | Python 3.11+ |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | Next.js 16 (App Router) |
| Styling | Tailwind CSS |
| Markdown rendering | react-markdown + remark-gfm |
| Language | TypeScript |

### Data
| Component | Detail |
|-----------|--------|
| Knowledge base | 8 official pages (USCIS, ICE, SEVP) |
| Total chunks | 95 chunks |
| Chunk size | 800 tokens, 150 overlap |
| Scraper | Custom BeautifulSoup scraper |

---

## RAG Pipeline — Layer by Layer

### Layer 1 — Core RAG
- Web scraper for USCIS, ICE, SEVP official pages
- Document chunker (RecursiveCharacterTextSplitter)
- OpenAI dense embeddings
- Pinecone vector storage and retrieval
- Claude Sonnet answer generation
- FastAPI backend + Next.js chat UI

### Layer 2 — Production Quality
- **Hybrid search** — BM25 sparse + OpenAI dense vectors combined
- **Two-stage retrieval** — Pinecone (top 5) → Cohere reranker (top 3)
- **Intent classification** — routes visa questions vs greetings vs out-of-scope
- **Guardrails** — detects and blocks knowledge leakage
- **Query cleaning** — strips greeting noise before embedding
- **Score filtering** — MIN_SCORE = 1.0 (dotproduct scale)

---

## Key Design Decisions

**Why dotproduct instead of cosine?**
Hybrid search (dense + sparse) requires dotproduct metric in Pinecone. Cosine normalizes vectors and loses the sparse signal.

**Why BM25 + dense vectors?**
Dense search misses exact terms like "I-765" or "8 CFR 214.2". BM25 catches exact keyword matches. Combined score = semantic understanding + keyword precision.

**Why Cohere reranker?**
Cross-encoder reranker reads query and chunk together — much more accurate than bi-encoder similarity scores. Reduces 5 chunks to top 3 most relevant.

**Why guardrails after generation?**
LLMs answer from parametric knowledge even when told not to. Guardrails detect when Claude answers without retrieved context and replaces with a safe refusal.

**Why intent classification?**
Greetings and formatting requests should not trigger expensive retrieval. QueryRewriter classifies intent first — saves cost and improves accuracy.

---

## Project Structure

```
VisaMentor-AI/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── routes/
│   │   │   ├── chat.py          # Chat endpoint + session manager
│   │   │   └── health.py        # Health check
│   │   └── models/
│   │       └── chat.py          # Request/response models
│   ├── rag/
│   │   ├── pipeline.py          # Orchestrates full RAG flow
│   │   ├── retriever.py         # Hybrid search (dense + sparse)
│   │   ├── generator.py         # Claude answer generation
│   │   ├── reranker.py          # Cohere cross-encoder reranker
│   │   ├── query_rewriter.py    # Intent classification
│   │   └── guardrails.py        # Knowledge leakage detection
│   └── ingestion/
│       ├── web_scraper.py       # USCIS/ICE/SEVP scraper
│       ├── chunker.py           # Document chunking
│       ├── embedder.py          # Dense + sparse embeddings
│       └── pinecone_store.py    # Vector upsert
├── scripts/
│   ├── run_ingest.py            # Full ingestion pipeline
│   └── recreate_index.py        # Recreate Pinecone index
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Home page
│   │   └── layout.tsx           # Root layout
│   └── components/
│       └── chat/
│           ├── ChatWindow.tsx   # Main chat interface
│           ├── MessageBubble.tsx # Message rendering + markdown
│           └── ChatInput.tsx    # Input component
└── data/
    └── scraped/                 # Scraped JSON documents
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- API keys: Anthropic, OpenAI, Pinecone, Cohere

### Backend
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .

# add API keys to .env
cp .env.example .env

# ingest documents
python scripts/run_ingest.py

# start backend
uvicorn src.api.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

---

## Environment Variables

```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
COHERE_API_KEY=
```

---

## Roadmap

- [x] Layer 1 — Core RAG pipeline
- [x] Layer 2 — Hybrid search, reranking, guardrails
- [ ] Layer 3 — Firebase auth, PostgreSQL, per-user personalization
- [ ] Layer 4 — LangSmith observability, admin dashboard, deployment

---

## Author

Manas Mahendra Mankar
