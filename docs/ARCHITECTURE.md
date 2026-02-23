"""
Architecture Overview

This document describes the high-level architecture and design decisions.
See PHASED_IMPLEMENTATION_PLAN.md for step-by-step implementation.

==============================================================================
🏗️ COMPONENT MODEL
==============================================================================

Frontend Layer
├── Streamlit UI
│   ├── Input form (user preferences)
│   ├── Preview pane (generated outline)
│   ├── Edit panel (modify sections)
│   ├── Chat widget (Query Agent Q&A)
│   └── Export buttons (Markdown, PDF, JSON)
└── Session Manager (in-memory state)

Agent Layer (Asynchronous)
├── Orchestrator Agent (coordinator)
│   ├── Routes requests to agents
│   ├── Manages session context
│   ├── Implements retry logic (Validator feedback)
│   └── Aggregates results
├── Retrieval Agent (RAG)
│   ├── Connects to ChromaDB
│   ├── Autonomously formulates queries
│   ├── Returns relevant doc chunks with metadata
│   └── Supports metadata filtering
├── Web Search Agent
│   ├── Multi-tool strategy (Tavily → DuckDuckGo → SerpAPI)
│   ├── Ranks results by relevance
│   └── Returns with confidence scores
├── Module Creation Agent (core synthesis)
│   ├── Respects all constraints (duration, depth, audience, mode)
│   ├── Maps objectives to Bloom's taxonomy
│   ├── Applies backward design principles
│   ├── Generates assessments aligned to objectives
│   └── Tracks provenance (which input → which output)
├── Validator Agent (quality gate)
│   ├── Scores outline using rubric (0-100)
│   ├── Provides targeted feedback
│   ├── Signals accept/reject + regeneration needs
│   └── (Triggers retry loop in Orchestrator)
└── Query Agent (interactive)
    ├── Answers follow-up questions
    ├── Shows provenance for responses
    ├── Can trigger module regeneration
    └── Maintains session context

Storage & External Services
├── ChromaDB Vector Store
│   ├── Curriculum documents (embeddings)
│   ├── Metadata index
│   └── Similarity search API
├── Web Search APIs
│   ├── Tavily (primary)
│   ├── DuckDuckGo (fallback)
│   └── SerpAPI (fallback)
├── LLM APIs (abstracted via LangChain)
│   ├── OpenAI (GPT-4)
│   ├── Anthropic (Claude)
│   └── Local models (optional)
└── Session Storage
    ├── In-memory (default)
    └── Temp file store for PDFs

==============================================================================
🔄 DATA FLOW (Generate Outline)
==============================================================================

1. USER SUBMITS FORM
   ┌─────────────────────────────────────────────┐
   │ UserInputSchema                             │
   │ - title, description, audience, depth       │
   │ - learning_mode, duration, optional PDF     │
   └──────────────────────────────────────────────┘
                        ↓
2. SESSION CREATED
   ┌─────────────────────────────────────────────┐
   │ OrchestratorContext                         │
   │ - session_id (UUID)                         │
   │ - user_input                                │
   │ - pdf_path (temp)                           │
   │ - (empty intermediate results)              │
   └──────────────────────────────────────────────┘
                        ↓
3. PARALLEL AGENT DISPATCH
   ┌─────────────────────────────────────────────┐
   │ Orchestrator.run()                          │
   │                                             │
   │ Parallel:                                   │
   │ ├─ RetrievalAgent.run(topic + filters)     │
   │ └─ WebSearchAgent.run(topic + depth)       │
   │                                             │
   │ When both complete:                         │
   │ └─ ModuleCreationAgent.run(all inputs)     │
   └──────────────────────────────────────────────┘
                        ↓
4. SYNTHESIS
   ┌─────────────────────────────────────────────┐
   │ Module Creation Agent processes             │
   │ - User input + constraints                  │
   │ - Retrieved doc chunks                      │
   │ - Web search results                        │
   │ - PDF content (if uploaded)                 │
   │                                             │
   │ Generates CourseOutlineSchema               │
   │ - Modules (count scales with duration)      │
   │ - Learning objectives (Bloom-mapped)        │
   │ - Lessons + assessments                     │
   │ - Provenance citations                      │
   └──────────────────────────────────────────────┘
                        ↓
5. VALIDATION LOOP (PHASE 6+)
   ┌─────────────────────────────────────────────┐
   │ ValidatorAgent.run(outline)                 │
   │                                             │
   │ Score: 0-100                                │
   │ - Coverage (0-25)                           │
   │ - Audience alignment (0-20)                 │
   │ - Depth/accuracy (0-20)                     │
   │ - Assessability (0-15)                      │
   │ - Practicality (0-10)                       │
   │ - Originality (0-10)                        │
   │                                             │
   │ If score < 75:                              │
   │   ├─ Feedback + targeted edits              │
   │   ├─ Orchestrator retries Module Agent      │
   │   └─ Loop until score >= 75 OR max attempts │
   │ Else:                                       │
   │   └─ Accept and return                      │
   └──────────────────────────────────────────────┘
                        ↓
6. RETURN TO FRONTEND
   ┌─────────────────────────────────────────────┐
   │ {                                           │
   │   "outline": CourseOutlineSchema,           │
   │   "validator_score": 88,                    │
   │   "regeneration_attempts": 2                │
   │ }                                           │
   │                                             │
   │ UI displays:                                │
   │ - Preview pane                              │
   │ - Editable sections                         │
   │ - Export buttons                            │
   │ - Chat widget for follow-ups                │
   └──────────────────────────────────────────────┘

==============================================================================
🔄 AGENT INTERACTION: Query Agent
==============================================================================

EDUCATOR QUESTION
     ↓
Query Agent receives:
  - question (string)
  - session context (user_input, retrieved_docs, web_results, outline)
     ↓
Query Agent:
  1. Understand question type (why, which resources, can you change)
  2. Retrieve relevant context
  3. Formulate answer with sources
  4. Assess confidence
  5. Optional: suggest module for regeneration
     ↓
Return QueryAgentResponse:
  - answer (natural language)
  - sources (no hallucinations)
  - confidence (0-1)
  - can_regenerate_module (if applicable)
     ↓
DISPLAY TO EDUCATOR

==============================================================================
📊 CONSTRAINTS & RESPECTS
==============================================================================

Duration Constraint
- USER: "I want a 40-hour course"
- MODULE CREATION AGENT respects this:
  ├─ Scales module count (e.g., 40 hrs → 5-6 modules)
  ├─ Allocates time per module
  ├─ Generates lessons to fit allocation
  └─ Validates: sum(module_hours) == 40

Depth Requirement
             CONCEPTUAL       APPLIED          IMPLEMENTATION        RESEARCH
             ──────────       ──────           ────────────          ────────
Examples:    Overview         Scenarios        Code labs              Papers
Activities:  Lectures         Case studies     Projects               Literature
Assessment:  Quiz             Report           Working code           Novel findings

Audience Level
             HIGH SCHOOL      UNDERGRAD        POSTGRAD              PROFESSIONAL
             ─────────────    ──────────       ──────────            ────────────
Vocab:       Simple           Technical        Advanced              Domain-specific
Math:        Algebra          Calculus         Proofs                ETC
Pace:        Slower           Moderate         Fast                   Deep-dive

Learning Mode
             SYNCHRONOUS      ASYNCHRONOUS     HYBRID
             ───────────      ────────────     ──────
Interaction: Live discussion  Self-paced       Both
Assessment:  Exams, group     Quizzes, essays  Mixed
Delivery:    Zoom, lectures   Videos, reading  Async + sync meetings

All constraints enforced by Module Creation Agent.
Validator checks compliance.

==============================================================================
🧪 OBSERVABILITY & MONITORING
==============================================================================

Agent Metrics (Per Request)
├─ agent_name (string)
├─ duration_ms (float)
├─ input_tokens (int)
├─ output_tokens (int)
├─ success (bool)
└─ error (optional)

Quality Metrics (Aggregated)
├─ validator_score (distribution)
├─ regeneration_frequency (%)
├─ educator_feedback_rating (1-5)
└─ error_rate (%)

Session Metrics
├─ total_latency_ms
├─ agents_called (list)
├─ regeneration_attempts
└─ export_format (json | markdown | pdf)

Logging (PII-Filtered)
├─ Pseudonymized session ID
├─ Agent execution trace
├─ Validator feedback
├─ Error stack trace
└─ (NO educator names, student data, or PDF content)

Dashboard Views (PHASE 9)
├─ Average validator score over time
├─ Regeneration frequency by depth/audience
├─ Error rate trends
├─ Agent latency distribution
└─ Educator satisfaction

==============================================================================
🔒 SECURITY & PRIVACY
==============================================================================

Session PDFs
✓ Stored in encrypted temp directory
✓ Auto-deleted when session ends
✓ Never indexed into persistent vector DB
✓ Explicit opt-in for any persistence

Logs & Telemetry
✓ PII filtering (no names, no student data)
✓ Pseudonymized by session ID
✓ Retention policy: 30 days by default
✓ Audit trail of decisions

API Access
- (TBD: Authentication & RBAC when API goes public)

---

Approved March 2025
"""