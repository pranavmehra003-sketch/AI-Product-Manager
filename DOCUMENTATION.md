# 📘 SprintCraft (AI Product Manager) — Complete Project Documentation

---

## 👨‍💻 Project Creator & Maintainer
- **Creator / Developer:** **Pranav Mehra**
- **GitHub:** [@pranavmehra003-sketch](https://github.com/pranavmehra003-sketch)
- **Email:** [pranavmehra003@gmail.com](mailto:pranavmehra003@gmail.com)
- **GitHub Repository:** [https://github.com/pranavmehra003-sketch/AI-Product-Manager](https://github.com/pranavmehra003-sketch/AI-Product-Manager)
- **Live Cloud Deployment:** [https://sprint-craft.streamlit.app](https://sprint-craft.streamlit.app)

---

## 🎯 1. Project Overview (Yeh Project Kya Hai?)

**SprintCraft (AI Product Manager)** ek autonomous **Multi-Agent Artificial Intelligence System** hai jo poore Product Management lifecycle ko automate karta hai.

Traditional product teams mein customer feedback collect karne, competitors ki tracking karne, metrics analyze karne, roadmap prioritize karne, PRD (Product Requirements Document) likhne aur sprint tasks divide karne mein hafto lagte hain.

Yeh system **7 specialized AI agents** aur ek **Human-in-the-Loop checkpoint** ke through is poore workflow ko minutes mein streamline kar deta hai:

```
[Raw Customer Feedback + Competitor Info + Analytics Data]
                          │
                          ▼
            ┌───────────────────────────┐
            │   Orchestrator Agent      │
            └─────────────┬─────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼   (Parallel Execution)
 ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
 │Feedback Agent│  │Competitor Agt│  │Analytics Agt │
 └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
        └─────────────────┼─────────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   Prioritization Agent    │ (Weighted 5-Factor Scoring)
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ 🧑‍💼 Human PM Checkpoint    │ (Review, adjust, approve features)
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │     PRD Writer Agent      │ (RAG + 14-Section Spec)
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   Sprint Planner Agent    │ (Story Points, Teams, DoD)
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │      Roadmap Agent        │ (Now / Next / Later Quarterly View)
            └───────────────────────────┘
```

---

## 🛠️ 2. Technology Stack (Kya Tech Stack Use Hua Hai?)

### A. Frontend & User Interface
- **Framework:** [Streamlit 1.35+](https://streamlit.io/)
- **Styling:** Custom Glassmorphism CSS (`ui/styles.css`), dark mode aesthetic, WCAG AA compliant contrast ratios.
- **Data Visualizations:** [Plotly Express & Plotly Graph Objects](https://plotly.com/python/) (Interactive Radar/Spider charts, Horizontal Priority Bar charts, Analytics Scatter/Bubble plots, Gauge meters).
- **Tabular Data:** Streamlit interactive DataFrames + custom HTML/CSS cards.

### B. Artificial Intelligence & LLMs
- **Primary AI Provider:** **Google Gemini 2.0 Flash** via `google-generativeai >= 0.8.0` (high throughput, low latency, structured JSON parsing).
- **Secondary / Fallback AI Provider:** **OpenAI GPT-4o-mini** via `openai >= 1.30.0`.
- **Dynamic Provider Switching:** Auto-detects configured API key (`GOOGLE_API_KEY` or `OPENAI_API_KEY`) and routes requests automatically without server restarts.
- **Resilience & Fallback:** `tenacity` retry logic + built-in deterministic simulation module (`tools/simulation_fallback.py`) that keeps the UI functioning even during offline periods or API quota exhaustion.

### C. Agent Orchestration & Concurrency
- **Concurrency:** Python standard library `concurrent.futures.ThreadPoolExecutor` for parallel 3x analysis speedup.
- **Data Contracts & Validation:** [Pydantic v2](https://docs.pydantic.dev/) (`models/schemas.py`) ensuring strict JSON schemas for every agent's input and output.

### D. RAG (Retrieval-Augmented Generation) & Vector DB
- **Vector Database:** [ChromaDB](https://www.trychroma.com/) (`chromadb >= 0.5.0`) stored persistently in `data/chroma_db/`.
- **Embeddings:** Text chunking & similarity search to retrieve past PRDs and internal product standards to enrich PRD authoring.

### E. Memory & Persistent Storage
- **Short-Term Memory:** In-memory session context cache (`memory/short_term.py`).
- **Long-Term Memory:** Embedded SQLite3 database (`data/product_manager.db` via `memory/long_term.py`) storing past sessions, error logs, PM decisions, and saved PRDs.

### F. Tools & Web Search
- **Live Search:** [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) (`duckduckgo-search >= 6.1.0`) for real-time competitive intelligence without paid search API subscriptions.
- **File Parsing & Exports:** CSV and JSON data ingestion + multi-format export tool (Markdown, CSV, JSON).

### G. Deployment & Hosting
- **Platform:** Streamlit Community Cloud
- **Production URL:** [https://sprint-craft.streamlit.app](https://sprint-craft.streamlit.app)
- **Configuration:** Custom `.streamlit/config.toml` enforcing headless cloud mode, XSRF protection, and elevated 50MB upload limits.

---

## 🤖 3. Deep Dive: 7 Specialized AI Agents

### 1. Feedback Analysis Agent (`agents/feedback_agent.py`)
- **Input:** Raw customer feedback records (CSV upload or sample data).
- **Function:** Clusters recurring themes, isolates critical bugs vs. feature requests, classifies sentiment, and calculates mention frequencies.
- **Output:** Categorized issues (Impact: Critical/High/Med/Low), feature requests, and sentiment breakdown.

### 2. Competitor Intelligence Agent (`agents/competitor_agent.py`)
- **Input:** Product domain and competitor names.
- **Function:** Queries DuckDuckGo for live web data, evaluates competitor feature sets, strengths, weaknesses, and pricing tiers.
- **Output:** Competitor profiles, comparative feature matrix, and unserved market gaps.

### 3. Product Analytics Agent (`agents/analytics_agent.py`)
- **Input:** Feature usage metrics (JSON format).
- **Function:** Evaluates DAU/MAU, session lengths, retention impact, churn correlation, and error rates.
- **Output:** Identification of high-growth features and high-risk features (e.g., high usage with high error rate).

### 4. Prioritization Agent (`agents/prioritization_agent.py`)
- **Input:** Synthesis of Feedback + Competitor + Analytics data + Business Goals + Team Capacity.
- **Function:** Applies an algorithmic multi-factor weighted scoring formula:
  $$\text{Priority Score} = (\text{Customer Impact} \times 0.30) + (\text{Business Value} \times 0.25) + (\text{Strategic Alignment} \times 0.20) + (\text{Urgency} \times 0.15) + (\text{Feasibility} \times 0.10)$$
- **Tiers:**
  - **P0 (Critical, Score ≥ 8.0):** Immediate sprint build.
  - **P1 (High, Score 6.5 – 7.9):** Next sprint build.
  - **P2 (Medium, Score 5.0 – 6.4):** Planned roadmap.
  - **P3 (Low, Score < 5.0):** Backlog / Nice-to-have.

### 5. PRD Writer Agent (`agents/prd_agent.py`)
- **Input:** PM-approved features + ChromaDB vector RAG context.
- **Function:** Generates production-ready 14-section Product Requirements Documents.
- **Includes:** Problem statement, target user personas, Gherkin-style User Stories (`Given / When / Then`), Functional (FR) & Non-Functional (NFR) requirements, Success metrics, Risks & Mitigations, and Technical architecture notes.

### 6. Sprint Planner Agent (`agents/sprint_agent.py`)
- **Input:** PRDs, approved features, team capacity (Story Points), and team size.
- **Function:** Decomposes features into discrete tasks across Backend, Frontend, Design, QA, and DevOps teams.
- **Includes:** Story point estimation (Fibonacci), dependency chains, Definition of Done (DoD), and capacity utilization meters.

### 7. Strategic Roadmap Agent (`agents/roadmap_agent.py`)
- **Input:** Prioritized feature backlog and business objectives.
- **Function:** Synthesizes an executive **Now / Next / Later** quarterly roadmap.
- **Includes:** Unifying themes per phase, expected business impacts, and measurable target KPIs.

---

## 👥 4. Human-in-the-Loop (PM Governance)

SprintCraft strictly avoids hallucinated autonomy by placing the **Product Manager in control**:
- AI recommends feature rankings with evidence-backed justification.
- The PM reviews the ranked list, overrides priorities if needed, selects approved items, and initiates PRD generation.
- All approval decisions are logged to SQLite for long-term auditability.

---

## 📁 5. Directory Structure

```
AI-Product-Manager/
├── .streamlit/
│   └── config.toml             # Streamlit Cloud deployment configuration
├── agents/
│   ├── orchestrator.py         # Master workflow controller & parallel executor
│   ├── feedback_agent.py       # Customer feedback analysis agent
│   ├── competitor_agent.py     # Competitor research via DuckDuckGo & LLM
│   ├── analytics_agent.py      # Product usage and metrics analyzer
│   ├── prioritization_agent.py # Weighted feature scoring & ranking
│   ├── prd_agent.py            # 14-section PRD writer (RAG-enhanced)
│   ├── sprint_agent.py         # Agile sprint planner & task breakdown
│   └── roadmap_agent.py        # Now/Next/Later strategic quarterly roadmap
├── tools/
│   ├── openai_tool.py          # Dual LLM engine (Google Gemini 2.0 & OpenAI)
│   ├── search_tool.py          # Free DuckDuckGo search integration
│   ├── database_tool.py        # SQLite helper methods
│   ├── file_tool.py            # CSV/JSON parser & validator
│   ├── export_tool.py          # Markdown, CSV, and JSON export utilities
│   ├── error_handler.py        # Error logging & retry handler
│   └── simulation_fallback.py  # Zero-downtime offline simulation engine
├── memory/
│   ├── short_term.py           # In-memory session state management
│   └── long_term.py            # SQLite persistent memory (PRDs, sessions, history)
├── models/
│   └── schemas.py              # Pydantic v2 schemas for all agent payloads
├── rag/
│   ├── embeddings.py           # Text chunking & document vectorization
│   ├── vector_store.py         # ChromaDB client & collection management
│   └── retriever.py            # Similarity search interface for PRDs
├── ui/
│   ├── app.py                  # Main Streamlit application and page router
│   ├── components.py           # Reusable UI widgets, charts, and status badges
│   ├── legal.py                # GDPR/Privacy hub and compliance dialogs
│   └── styles.css              # Cyber-glassmorphism dark UI theme
├── data/
│   ├── sample_feedback.csv     # 200 real-world customer feedback entries
│   ├── sample_analytics.json   # Sample feature usage and retention dataset
│   ├── product_manager.db      # SQLite persistent storage
│   └── chroma_db/              # ChromaDB vector index storage
├── docs/
│   └── previous_prds/          # Seed knowledge base for RAG PRD agent
├── .env.example                # Sample environment variables
├── requirements.txt            # Python package dependencies
├── run.py                      # Local launch script
├── HOW_TO_USE.md               # User quick-start guide
├── DOCUMENTATION.md            # Comprehensive project documentation
└── README.md                   # Public repository documentation
```

---

## ⚡ 6. How to Run Locally

```bash
# 1. Clone repository
git clone https://github.com/pranavmehra003-sketch/AI-Product-Manager.git
cd AI-Product-Manager

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
copy .env.example .env
# Set GOOGLE_API_KEY=your_key in .env

# 4. Launch Application
python run.py
```

---

## 📄 7. License & Credits

- **Developer:** **Pranav Mehra** ([pranavmehra003@gmail.com](mailto:pranavmehra003@gmail.com))
- **GitHub:** [@pranavmehra003-sketch](https://github.com/pranavmehra003-sketch)
- **App URL:** [https://sprint-craft.streamlit.app](https://sprint-craft.streamlit.app)
- **License:** Open Source under the MIT License.
