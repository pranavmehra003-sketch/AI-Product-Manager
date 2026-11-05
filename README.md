# 🤖 AI Product Manager — Multi-Agent Product Intelligence System

A comprehensive multi-agent AI system that automates the full product management lifecycle: from raw customer feedback to sprint-ready plans, PRDs, and a quarterly roadmap.

## 🏗️ Architecture

```
Streamlit UI
     │
     ▼
Orchestrator Agent
     │
 ┌───┼───┐
 ▼   ▼   ▼         ← Runs in parallel
Feedback  Competitor  Analytics
 Agent      Agent      Agent
     │
     ▼
Prioritization Agent
     ↓
[👥 Human PM Approval]
     ↓
PRD Writer Agent
     ↓
Sprint Planner Agent
     ↓
Roadmap Agent (on-demand)
```

## 🤖 7 AI Agents

| Agent | Role |
|---|---|
| **Feedback Agent** | Analyzes customer feedback → issues, features, sentiment |
| **Competitor Agent** | Web search + LLM → competitive intelligence |
| **Analytics Agent** | Product metrics → trends, risks, opportunities |
| **Prioritization Agent** | Weighted scoring formula → ranked roadmap |
| **PRD Writer Agent** | RAG-enhanced → 14-section PRDs |
| **Sprint Planner Agent** | PRD + capacity → sprint tasks |
| **Roadmap Agent** | Prioritized features → Now/Next/Later quarterly roadmap |

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit (premium dark theme) |
| AI | Google Gemini 2.0 Flash / OpenAI GPT-4o-mini |
| Agents | Python with concurrent.futures (parallel) |
| Database | SQLite (long-term memory) |
| Vector DB | ChromaDB (RAG) |
| Search | DuckDuckGo (free competitor research) |

## ⚡ Quick Start

### 1. Clone & Install

```bash
cd "d:\AI Product Manager"
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
copy .env.example .env
# Edit .env and add your API key:
# GOOGLE_API_KEY=your_gemini_key_here   (recommended)
# or
# OPENAI_API_KEY=sk-...
```

### 3. Run

```bash
python run.py
# OR directly:
streamlit run ui/app.py
```

Open **https://sprint-craft.streamlit.app**

## 📁 Project Structure

```
ai-product-manager/
├── agents/
│   ├── orchestrator.py         # Workflow controller
│   ├── feedback_agent.py       # Customer feedback analysis
│   ├── competitor_agent.py     # Competitor research
│   ├── analytics_agent.py      # Product metrics analysis
│   ├── prioritization_agent.py # Feature scoring & ranking
│   ├── prd_agent.py            # PRD generation (RAG-enhanced)
│   ├── sprint_agent.py         # Sprint planning
│   └── roadmap_agent.py        # Now/Next/Later roadmap generator ✨
├── tools/
│   ├── openai_tool.py          # Multi-provider LLM wrapper (Gemini + OpenAI)
│   ├── search_tool.py          # DuckDuckGo search
│   ├── database_tool.py        # SQLite operations
│   ├── file_tool.py            # CSV/JSON parsing
│   ├── export_tool.py          # Markdown/CSV export ✨
│   └── error_handler.py        # Retry & error logging
├── memory/
│   ├── short_term.py           # Session context store
│   └── long_term.py            # SQLite persistent memory
├── rag/
│   ├── embeddings.py           # Text chunking
│   ├── vector_store.py         # ChromaDB wrapper
│   └── retriever.py            # RAG interface
├── models/
│   └── schemas.py              # Pydantic data models
├── ui/
│   ├── app.py                  # Streamlit application
│   ├── components.py           # Reusable UI components
│   └── styles.css              # Dark theme CSS
├── data/
│   ├── sample_feedback.csv     # 200 feedback records
│   └── sample_analytics.json  # 8 feature metrics
├── docs/
│   └── previous_prds/          # RAG knowledge base
├── .env.example
├── requirements.txt
└── run.py
```

## 🎯 Priority Scoring Formula

```
Priority Score = 
  Customer Impact    × 0.30
  Business Value     × 0.25
  Strategic Alignment × 0.20
  Urgency            × 0.15
  Feasibility        × 0.10
```

| Score | Priority | Meaning |
|---|---|---|
| ≥ 8.0 | **P0** 🔴 | Critical — build this sprint |
| 6.5–7.9 | **P1** 🟠 | High — build next sprint |
| 5.0–6.4 | **P2** 🟡 | Medium — plan for later |
| < 5.0 | **P3** ⚫ | Low — nice to have |

## 💬 Demo Scenario

1. **Upload** 200 customer feedback records (or use sample data)
2. **Analyze**: 3 agents run in parallel (feedback + competitors + analytics)
3. **Prioritize**: AI ranks features with weighted scoring
4. **Approve**: PM reviews and approves features (human-in-the-loop)
5. **PRD**: AI generates full 14-section PRDs with RAG context
6. **Sprint**: AI creates task-level sprint plan with story points
7. **Roadmap**: Generate Now/Next/Later quarterly roadmap ✨

## 🔑 Requirements

- Python 3.10+
- Google Gemini API key (recommended) or OpenAI API key
- Internet connection (for DuckDuckGo competitor search)

## 📊 Key Features

- ✅ 7 specialized AI agents with structured JSON outputs
- ✅ Parallel agent execution (3x faster analysis)
- ✅ Human-in-the-loop approval checkpoint
- ✅ RAG-enhanced PRD generation
- ✅ SQLite long-term memory (remembers past decisions)
- ✅ ChromaDB vector store for product knowledge
- ✅ Weighted multi-factor feature scoring
- ✅ Sprint board visualization
- ✅ Now/Next/Later quarterly roadmap generation ✨
- ✅ Download PRDs as JSON **or Markdown** ✨
- ✅ Download Sprint Plans as JSON **or Markdown** ✨
- ✅ Download Feature Priorities as **CSV** ✨
- ✅ Error logging and retry logic
- ✅ Premium dark-themed Streamlit UI
- ✅ Google Gemini 2.0 Flash support (default) ✨
