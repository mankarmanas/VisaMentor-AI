# VisaMentor AI

An AI-powered F-1 visa assistant for international students studying in the United States. VisaMentor AI answers questions about OPT, CPT, STEM OPT, work authorization, tax obligations, H-1B transition, and more — grounded strictly in official government sources.

🔗 **Live Demo:** https://visamentorai.vercel.app

---

## Features

- **RAG Pipeline** — Retrieval-Augmented Generation with Pinecone hybrid search (dense + sparse BM25)
- **Cohere Reranker** — Re-orders retrieved chunks by actual relevance before generation
- **Claude Sonnet 4.6** — Generates grounded answers strictly from retrieved context
- **Knowledge Leakage Prevention** — Multi-layer guardrails prevent the LLM from using pretrained knowledge
- **Personalized Answers** — Student profile (university, program, dates) used to calculate OPT/CPT deadlines
- **Date Engine** — Calculates CPT eligibility, OPT application window, STEM OPT dates from program dates
- **STEM Mismatch Detection** — Warns students if their program qualifies for STEM OPT but they marked it otherwise
- **Conversation History** — Full multi-turn chat with session persistence
- **Firebase Authentication** — Google Sign-In
- **LangSmith Observability** — Full pipeline tracing with token usage and latency per step
- **GitHub Actions CI** — Automated testing on every push

---

## Tech Stack

### Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| LLM | Claude Sonnet 4.6 (Anthropic) |
| Query Classification | Claude Haiku 4.5 |
| Embeddings | OpenAI text-embedding-3-large |
| Vector Database | Pinecone (hybrid search) |
| Sparse Search | BM25 (pinecone-text) |
| Reranker | Cohere rerank-english-v3.0 |
| Database | PostgreSQL (Render) |
| ORM | SQLAlchemy |
| Observability | LangSmith |
| Package Manager | uv |

### Frontend
| Component | Technology |
|---|---|
| Framework | Next.js 15 |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Authentication | Firebase (Google Sign-In) |
| Deployment | Vercel |

### Data Pipeline
| Component | Technology |
|---|---|
| Web Scraper | httpx + BeautifulSoup + curl-cffi |
| Chunker | Custom text chunker |
| Embedder | OpenAI + Pinecone ingestion |
| Sources | USCIS, SEVP, ICE, IRS, State Dept |

---

## RAG Pipeline Architecture

```
User Question
      ↓
Query Rewriter (Claude Haiku)
  → Classifies intent (visa_question / greeting / formatting / out_of_scope)
  → Cleans query
      ↓
Retriever (Pinecone Hybrid Search)
  → Dense vector search (OpenAI embeddings)
  → Sparse BM25 search
  → Combined hybrid score
      ↓
Reranker (Cohere)
  → Re-orders chunks by relevance
  → Quality gate: blocks low-confidence results
      ↓
Generator (Claude Sonnet 4.6)
  → Strict RAG mode — answers only from retrieved context
  → Personalized with student profile and calculated dates
      ↓
Guardrails
  → Blocks answers that use pretrained knowledge
  → Ensures refusal when context is insufficient
      ↓
Response + Sources
```

---

## Knowledge Leakage Prevention

VisaMentor AI uses a 3-layer system to prevent the LLM from answering from pretrained knowledge:

1. **Reranker Quality Gate** — Blocks retrieval if best rerank score < 0.35
2. **Hardened System Prompt** — Strict RAG mode instructions, no inline citations
3. **Guardrails** — Post-generation check that validates answer against chunk count

---

## Data Sources

All answers are grounded in official US government sources:

- **USCIS** — OPT, STEM OPT, CPT, I-765, H-1B, E-Verify, policy manual
- **SEVP / Study in the States** — F-1 employment, CPT, SEVIS, student forms
- **ICE** — Practical training
- **IRS** — Tax obligations for F-1 students and scholars
- **State Department** — F-1 visa information

---

## Project Structure

```
VisaMentor-AI/
├── src/
│   ├── api/              # FastAPI routes and middleware
│   ├── db/               # SQLAlchemy models, CRUD, database connection
│   ├── ingestion/        # Web scraper, chunker, embedder, Pinecone store
│   └── rag/              # Pipeline, retriever, reranker, generator, guardrails
├── frontend/             # Next.js 15 app
│   ├── app/              # Pages (login, main chat)
│   ├── components/       # Chat window, sidebar, profile, settings
│   └── lib/              # API client, Firebase auth
├── tests/                # pytest test suite
├── data/
│   ├── scraped/          # Raw scraped JSON files
│   └── bm25_encoder.json # Trained BM25 encoder
├── .github/workflows/    # GitHub Actions CI
└── pyproject.toml        # Python dependencies (uv)
```

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- uv package manager
- Pinecone account
- OpenAI API key
- Anthropic API key
- Cohere API key
- Firebase project
- PostgreSQL database

### Backend

```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Fill in your API keys

# Run ingestion pipeline (scrape + embed + push to Pinecone)
uv run python -m src.ingestion.web_scraper
uv run python scripts/run_ingest.py

# Start backend
uv run uvicorn src.api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

### Backend (.env)
```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
COHERE_API_KEY=
DATABASE_URL=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=VisaMentor-AI
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
```

---

## Deployment

- **Backend** — Render Web Service (Virginia US East)
- **Database** — Render PostgreSQL (Virginia US East)
- **Frontend** — Vercel
- **Observability** — LangSmith

---

## CI/CD

GitHub Actions runs on every push to `main` and `dev`:

- **Backend CI** — runs pytest test suite
- **Frontend CI** — TypeScript type check, ESLint, Next.js build

---

## License

MIT
