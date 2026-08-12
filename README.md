# 🤖 AI Product Manager — Multi-Agent Product Intelligence System

A comprehensive multi-agent AI system that automates the full product management lifecycle: from raw customer feedback to sprint-ready plans.

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
```

## 🤖 6 AI Agents

| Agent | Role |
|---|---|
| **Feedback Agent** | Analyzes customer feedback → issues, features, sentiment |
| **Competitor Agent** | Web search + GPT-4o → competitive intelligence |
| **Analytics Agent** | Product metrics → trends, risks, opportunities |
| **Prioritization Agent** | Weighted scoring formula → ranked roadmap |
| **PRD Writer Agent** | RAG-enhanced → 14-section PRDs |
| **Sprint Planner Agent** | PRD + capacity → sprint tasks |

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit (premium dark theme) |
| AI | OpenAI GPT-4o / GPT-4o-mini |
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
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

### 3. Run

```bash
python run.py
# OR directly:
streamlit run ui/app.py
```

Open http://localhost:8501

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
│   └── sprint_agent.py         # Sprint planning
├── tools/
│   ├── openai_tool.py          # GPT-4o wrapper
│   ├── search_tool.py          # DuckDuckGo search
│   ├── database_tool.py        # SQLite operations
│   ├── file_tool.py            # CSV/JSON parsing
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

## 🔑 Requirements

- Python 3.10+
- OpenAI API key (GPT-4o-mini works well and is cost-efficient)
- Internet connection (for DuckDuckGo competitor search)

## 📊 Key Features

- ✅ 6 specialized AI agents with structured JSON outputs
- ✅ Parallel agent execution (3x faster analysis)
- ✅ Human-in-the-loop approval checkpoint
- ✅ RAG-enhanced PRD generation
- ✅ SQLite long-term memory (remembers past decisions)
- ✅ ChromaDB vector store for product knowledge
- ✅ Weighted multi-factor feature scoring
- ✅ Sprint board visualization
- ✅ Download PRDs and sprint plans as JSON
- ✅ Error logging and retry logic
- ✅ Premium dark-themed Streamlit UI
