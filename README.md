"""
Main README for the Course AI Agent project.
"""

# Course AI Agent

📚 AI-powered course outline generator using agentic LLM architecture.

**Status:** ✅ Phase 5 Complete | Module Creation Agent (Core Intelligence Layer) with multi-layer prompts and provenance tracking

---

## What is This?

A system that generates comprehensive, constraint-respecting course outlines by:

1. **Accepting educator input** (title, description, audience level, depth, duration, optional PDF)
2. **Coordinating multiple AI agents** (Retrieval, Web Search, Module Creation, Validator, Query)
3. **Synthesizing intelligent outlines** aligned to Bloom's taxonomy and backward design principles
4. **Validating quality** with rubric-based scoring and automated feedback loops
5. **Enabling refinement** through interactive follow-ups and targeted regeneration

---

## Architecture (High-Level)

```
Frontend (Streamlit)
       ↓
Orchestrator Agent (coordinator)
       ├─→ Step 4: Retrieval Agent (ChromaDB) - internal knowledge
       ├─→ Step 5: Web Search Agent (Tavily/DuckDuckGo/SerpAPI) - external knowledge ⭐ NEW
       ├─→ Step 6: Module Creation Agent - uses both sources
       ├─→ Validator Agent - quality gate
       └─→ Query Agent - interactive explanations
       ↓
Frontend Results & Editable Outline
```

**Phase 4 Integration:** WebSearchAgent added as non-blocking Step 5 with intelligent fallback chain

---

## Quick Start

### Prerequisites

- Python 3.10+
- Streamlit
- LangChain
- ChromaDB
- OpenAI API key (or alternative LLM)

### Setup

```bash
cd course_ai_agent
pip install -r requirements.txt

# Run tests
pytest tests/

# Run app
streamlit run app.py
```

---

## Project Structure

```
course_ai_agent/
├── app.py                      # Streamlit entry point
├── agents/
│   ├── base.py                # Agent contracts & base classes
│   ├── orchestrator.py         # Main coordinator (Step 1-6)
│   ├── retrieval_agent.py      # RAG (ChromaDB) - Step 4
│   ├── web_search_agent.py     # Web search (Tavily/DuckDuckGo/SerpAPI) - Step 5 ⭐ NEW
│   ├── module_creation_agent.py # Core synthesis engine - Step 6
│   ├── validator_agent.py      # Quality scoring & feedback
│   └── query_agent.py          # Interactive explanations
├── schemas/
│   ├── user_input.py           # UserInputSchema
│   ├── execution_context.py    # ExecutionContext (carries all sources)
│   ├── web_search_agent_output.py # WebSearchAgentOutput ⭐ NEW
│   ├── retrieval_agent_output.py # RetrievalAgentOutput
│   ├── course_outline.py       # CourseOutlineSchema
│   └── vector_document.py      # VectorDocument
├── tools/
│   ├── web_search_tools.py     # Multi-tool orchestration (Tavily/DuckDuckGo/SerpAPI) ⭐ NEW
│   ├── curriculum_ingestion.py # ChromaDB ingestion ⭐ UPDATED
│   └── pdf_loader.py           # PDF extraction
├── services/
│   ├── llm_service.py          # LLM abstraction layer (Claude/GPT/Ollama)
│   ├── embedding_service.py    # Embedding provider
│   ├── vector_store.py         # Vector store management
│   └── db_service.py           # Database service
├── utils/
│   ├── session.py              # Session management
│   ├── scoring.py              # Validator rubric logic
│   └── logging.py              # Observability
├── prompts/
│   ├── orchestrator.txt        # Orchestrator prompt
│   └── web_search_agent.txt    # Web search anti-hallucination prompt ⭐ NEW
├── tests/                      # Comprehensive test suite (by phase)
├── data/
│   ├── sample_curricula/       # Synthetic test docs
│   └── sample_user_uploads/    # Ephemeral session test files
├── docs/
│   ├── PHASED_IMPLEMENTATION_PLAN.md  # Phase planning
│   ├── architecture.md         # Architecture details
│   └── API_SPECS.md            # API contracts
├── PHASE_4_MASTER_INDEX.md     # Phase 4 documentation navigation ⭐
├── PHASE_4_ARCHITECTURE.md     # Phase 4 system design
├── PHASE_4_CODE_EXAMPLES.md    # Phase 4 runnable examples
├── PHASE_4_TESTING_RUNBOOK.md  # Phase 4 test guide
├── PHASE_4_QUICK_START.md      # Phase 4 quick reference
├── PHASE_4_COMPLETION_SUMMARY.md # Phase 4 delivery report
└── README.md                   # This file
```

---

## Phased Implementation (9 Phases)

We implement incrementally, adding one capability per phase. Each phase is testable and deployable independently.

| Phase | Goal | Duration | Status |
|-------|------|----------|--------|
| 0 | Project skeleton & contracts | 1-2d | ✅ Complete |
| 1 | Streamlit UI + session mgmt | 3-4d | ✅ Complete |
| 2 | Orchestrator (single-pass) | 4-5d | ✅ Complete |
| 3 | Retrieval Agent + ChromaDB | 5-6d | ✅ Complete |
| 4 | Web Search Agent | 4-5d | ✅ Complete |
| 5 | Module Creation Agent (Core Intelligence) | 8-10d | ✅ **COMPLETE** ⭐ NEW |
| 6 | Validator Agent (agentic loop) | 6-7d | 🟡 Planning |
| 7 | Query Agent (interactive) | 4-5d | 🟡 Planning |
| 8 | UX polish & exports | 5-6d | 🟡 Planning |
| 9 | Observability & metrics | 4-5d | 🟡 Planning |

See [PHASED_IMPLEMENTATION_PLAN.md](docs/PHASED_IMPLEMENTATION_PLAN.md) for detailed breakdown.

### Phase 4 (Web Search Agent) - Just Delivered! 🎉

**What was added:**
- Multi-tool search orchestration (Tavily, DuckDuckGo, SerpAPI with intelligent fallback)
- WebSearchAgent with contextual query generation (3 queries per request)
- LLM-powered synthesis with anti-hallucination prompt template
- Complete provenance tracking (tool attribution, URLs, timestamps, confidence scores)
- Non-blocking orchestrator integration (Step 5)
- 30 comprehensive async tests
- 6 detailed documentation guides (~4,300 lines)

**Documentation:**
- 📖 [PHASE_4_MASTER_INDEX.md](PHASE_4_MASTER_INDEX.md) - Start here! Navigation guide
- 🏗️ [PHASE_4_ARCHITECTURE.md](PHASE_4_ARCHITECTURE.md) - System design & decisions
- 💡 [PHASE_4_CODE_EXAMPLES.md](PHASE_4_CODE_EXAMPLES.md) - 6 runnable examples
- 🧪 [PHASE_4_TESTING_RUNBOOK.md](PHASE_4_TESTING_RUNBOOK.md) - Test guide
- ⚡ [PHASE_4_QUICK_START.md](PHASE_4_QUICK_START.md) - Quick reference
- 📋 [PHASE_4_COMPLETION_SUMMARY.md](PHASE_4_COMPLETION_SUMMARY.md) - Delivery report

**Quick Test:**
```bash
pytest tests/test_phase_4_web_search.py -v
# Expected: 30 passed in ~15s ✅
```

---

### Phase 5 (Module Creation Agent - Core Intelligence Layer) - Just Delivered! 🎉

**What was added:**
- **STEP 5.1:** CourseOutlineSchema locked with comprehensive validation (BloomLevel, AssessmentType, SourceType enums, Reference dataclass for provenance)
- **STEP 5.2:** Agent responsibility boundary (pure synthesis, no tool calls, stateless)
- **STEP 5.3:** Multi-layer prompt architecture (system, developer, user, context, constraints layers)
- **STEP 5.4:** Duration & depth allocator utility (pre-LLM logic prevents hallucination)
- **STEP 5.5:** Learning mode templates (theory, project_based, interview_prep, research)
- **STEP 5.6:** PDF integration (contextual guidance without dominating content)
- **STEP 5.7:** Complete provenance tracking (4 source types: web, retrieved, pdf, generated)
- **STEP 5.8:** Orchestrator Step 6 integration (non-blocking, passes through all context)
- **STEP 5.9:** Comprehensive test suite (~25 tests covering all 9 steps)

**Files Added/Updated:**
- ✅ `agents/module_creation_agent.py` (580+ lines) - Full Phase 5 implementation
- ✅ `schemas/course_outline.py` (450+ lines) - Enhanced with Phase 5 schema
- ✅ `utils/duration_allocator.py` (~180 lines) - Pre-LLM duration logic
- ✅ `utils/learning_mode_templates.py` (~280 lines) - Mode-specific structures
- ✅ `tests/test_phase_5_module_creation.py` (~550 lines) - Comprehensive test suite
- ✅ `agents/orchestrator.py` (updated) - Step 6 integration

**Key Features:**
- 🧠 Multi-layer prompts prevent LLM hallucination through explicit constraints
- 📐 Pre-LLM duration allocation ensures module count respects time constraints
- 🔄 Learning mode variations (theory → project-based → interview prep → research)
- 📚 3 Bloom levels per module (remember → understand → apply → analyze → evaluate → create)
- 🔗 Complete source attribution (who authored, what institution, when published)
- 🎯 Confidence & completeness scoring (context richness → outline quality)
- 🛡️ Schema validation (3-12 modules, 3-7 objectives per module, duration alignment)

**Documentation Coming** (Phase 6 will add detailed guides)

**Quick Test:**
```bash
pytest tests/test_phase_5_module_creation.py -v
# Expected: ~25 passed in ~10s ✅
```

---

## Key Contracts & Schemas

### Input: UserInputSchema

```python
{
  "course_title": "Introduction to Machine Learning",
  "course_description": "...",
  "audience_level": "undergraduate",
  "audience_category": "cs_major",
  "learning_mode": "hybrid",
  "depth_requirement": "implementation",
  "duration_hours": 40,
  "pdf_path": "/tmp/session_123.pdf",  # optional
  "custom_constraints": "..."
}
```

### Output: CourseOutlineSchema

```python
{
  "course_title": "...",
  "course_summary": "...",
  "audience_level": "undergraduate",
  "modules": [
    {
      "module_id": "M_1",
      "title": "Foundations",
      "learning_objectives": [
        {
          "statement": "Explain supervised vs unsupervised learning",
          "bloom_level": "understand",
          "assessment_method": "quiz"
        }
      ],
      "lessons": [...]
    }
  ],
  "citations_and_provenance": [...]
}
```

Full schemas: [schemas/](schemas/)

---

## Testing

Tests are organized by phase:

```bash
# Phase 2 - Orchestrator
pytest tests/test_orchestrator.py

# Phase 3 - Retrieval Agent + ChromaDB
pytest tests/test_phase_3_retrieval.py

# Phase 4 - Web Search Agent (NEW)
pytest tests/test_phase_4_web_search.py -v
# Expected: 30 tests, all passing

# Phase 1 - UI + Session
pytest tests/test_phase_1_ui.py

# Run all tests
pytest tests/ -v
# Expected: 75+ tests (Phase 2: 20, Phase 3: 25, Phase 4: 30)
```

**Phase 4 Test Coverage:**
- ✅ Search Tools (8 tests) - Tool initialization, fallback chain, deduplication
- ✅ Output Schema (8 tests) - Schema validation, serialization, confidence
- ✅ Agent Logic (7 tests) - Query generation, synthesis, orchestration
- ✅ Failure Resilience (5 tests) - Error handling, graceful degradation
- ✅ Provenance (4 tests) - Attribution tracking, timestamps, URLs
- ✅ Integration (1 test) - Full end-to-end pipeline

---

## Configuration

Set environment variables:

```bash
# LLM Service (OpenAI, Anthropic, or Ollama)
export OPENAI_API_KEY="sk-..."          # For OpenAI
export ANTHROPIC_API_KEY="sk-ant-..."  # For Claude
export LLM_MODEL="gpt-4-turbo"         # or "claude-3-sonnet", etc.

# Phase 4: Web Search (Optional - all have fallbacks)
export TAVILY_API_KEY="tvly-..."       # Primary (optional, has mock)
export DUCKDUCKGO_ENABLED=true          # Secondary (free, always available)
export SERPAPI_KEY="..."               # Tertiary (optional)

# ChromaDB & Vector Store
export CHROMA_DB_PATH="./chroma_db"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Session Management
export SESSION_TTL_MINUTES=60
export TEMP_DIR="/tmp/course_ai_sessions"

# Validation & Regeneration
export VALIDATOR_THRESHOLD=75
export MAX_REGENERATION_ATTEMPTS=3

# Data
export CURRICULUM_FOLDER="./data/sample_curricula"
```

---

## API Usage (PHASE 2+)

### Generate Course Outline

```bash
curl -X POST http://localhost:8000/api/outline \
  -H "Content-Type: application/json" \
  -d '{
    "course_title": "Intro to ML",
    "course_description": "...",
    "audience_level": "undergraduate",
    "learning_mode": "hybrid",
    "depth_requirement": "implementation",
    "duration_hours": 40
  }'
```

Response:
```json
{
  "session_id": "uuid",
  "status": "accepted",
  "outline": { ... CourseOutlineSchema ... },
  "validator_score": 88,
  "regeneration_attempts": 1
}
```

---

## Data Privacy & Security

✅ **Session PDFs:** Ephemeral (stored in temp, auto-deleted after session)
✅ **Persistent Storage:** Only curriculum metadata + embeddings (no PII)
✅ **Logging:** Pseudonymized (session IDs, no names)
✅ **Exports:** Consent captured, revision history maintained

---

## Contributing

**Current Phase:** Phase 5 (Module Creation Agent - In Progress)

1. Check [PHASED_IMPLEMENTATION_PLAN.md](docs/PHASED_IMPLEMENTATION_PLAN.md) for phase details
2. Review Phase X documentation before implementing
3. Implement phase contracts (see schemas/)
4. Write comprehensive async tests
5. Run tests: `pytest tests/test_phase_X.py -v`
6. Ensure backward compatibility with previous phases
7. Submit PR with documentation

**Phase 4 Integration Pattern (Use for Phase 5+):**
- Add new agent to `agents/`
- Create output schema in `schemas/`
- Add non-blocking try-catch in `orchestrator.py`
- Store results in `ExecutionContext`
- Write 20-30 comprehensive tests
- Document with code examples

---

## Roadmap

### Current (Phase 4 ✅ Complete)
- ✅ Web search integration with multi-tool fallback
- ✅ External knowledge layer
- ✅ Orchestrator Step 5 (non-blocking)

### Near-term (Phase 5-7)
- 🟢 Phase 5: Module Creation Agent (use both internal + external knowledge)
- 🟡 Phase 6: Validator Agent (agentic loop with quality scoring)
- 🟡 Phase 7: Query Agent (interactive follow-ups)

### Medium-term (Phase 8-9)
- 🟡 Phase 8: UX polish & professional exports
- 🟡 Phase 9: Observability & analytics

### Long-term (Post-Phase-9)
- Human-in-the-loop review workflow
- LMS integration (Moodle, Canvas)
- Student capability adaptivity
- Real-time collaborative editing
- Multi-language support
- AI-powered assessment rubric generation

---

## Support

- **Issues?** See `tests/` for expected behavior
- **Questions?** Check [PHASED_IMPLEMENTATION_PLAN.md](docs/PHASED_IMPLEMENTATION_PLAN.md)
- **Design Docs?** See `docs/` folder

---

**Built with:** Streamlit, LangChain, ChromaDB, LLMs (OpenAI/Anthropic)

**License:** [TBD]

**Status:** 🟢 Phase 4 Complete (Phases 0-4 implemented, Phase 5+ in planning)

**Latest Update (Feb 21, 2026):**
- ✅ Phase 4: Web Search Agent complete with 30 tests
- ✅ Multi-tool fallback (Tavily → DuckDuckGo → SerpAPI)
- ✅ Anti-hallucination LLM synthesis
- ✅ Complete provenance tracking
- ✅ Non-breaking orchestrator integration
- ✅ ~1,920 lines of code + ~4,300 lines of documentation
- ✅ All pushed to GitHub (commit: 71e663c)
