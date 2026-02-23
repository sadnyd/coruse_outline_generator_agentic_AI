"""
📋 COMPREHENSIVE PHASED IMPLEMENTATION PLAN

Course AI Agent: From Bare Bones to Full Agentic System

==============================================================================
🟢 PHASE 0 — Project Skeleton & Contracts (Foundation)
==============================================================================

🎯 GOAL
Create nothing intelligent yet — only structure, interfaces, and contracts.
Ensure future agents plug in cleanly without architectural rot.

DELIVERABLES
✓ Structured directory layout
✓ Pydantic schema contracts (input, output, intermediate)
✓ Agent base classes with run() signatures
✓ Test scaffolding (no tests pass yet)
✓ Stub agent implementations

RESPONSIBILITIES (Who Owns What)
- Project Lead: Directory structure, schema ownership
- Backend Lead: Agent base classes, interface design
- QA Lead: Test scaffolding design

KEY FILES
- schemas/user_input.py - UserInputSchema contract
- schemas/course_outline.py - CourseOutlineSchema + LearningObjective contract
- schemas/agent_outputs.py - Per-agent output contracts
- agents/base.py - BaseAgent + agent responsibilities
- tests/ - All test skeletons with docstrings

EXIT CONDITION
✓ All imports work
✓ Agents can be instantiated
✓ Schemas validate correctly
✓ No runtime errors

TESTING
- test_schemas.py: Schema validation (Pydantic, required fields)
- test_project_boot.py: Import checks, directory existence

DURATION ESTIMATE: 1-2 days (one engineer)

---

🟢 PHASE 1 — Streamlit UI + Session Management
==============================================================================

🎯 GOAL
Build the full frontend input experience.
Establish session-aware request context (no AI yet).

DELIVERABLES
✓ Streamlit UI with all input fields
✓ Session management (in-memory store)
✓ PDF upload → temp storage lifecycle
✓ Form validation on submit
✓ Input capture in structured schema

RESPONSIBILITIES
- Frontend Lead: Streamlit UI, form layout, UX
- Backend Lead: Session manager, temp file handling
- DevOps: Temp directory configuration (cleanup)

KEY FILES
- app.py - Streamlit entry point
- utils/session.py - SessionManager class
- tests/test_phase_1_ui.py - UI + session tests

AGENT STUBS NEEDED
- Session storage only (no agent invocation yet)

SESSION CONTEXT (Established Now)
```
{
  "session_id": "uuid",
  "user_input": UserInputSchema,
  "pdf_path": "/tmp/session_123.pdf",
  "intermediate_results": {},
  "conversation_history": []
}
```

EXIT CONDITION
✓ Form submits with valid input
✓ Form rejects incomplete input
✓ PDF uploaded to temp directory
✓ Session persists across requests
✓ Reset button clears all data
✓ temp files cleaned up after session

TESTING
- test_phase_1_ui.py: Form capture, validation, session lifecycle

DURATION ESTIMATE: 3-4 days

---

🟢 PHASE 2 — Orchestrator (Single-Pass, Non-Agentic)
==============================================================================

🎯 GOAL
Create end-to-end vetical slice: input → orchestrator → module creation → output.
Still non-agentic (no loops, retries, or validation yet).

DELIVERABLES
✓ Orchestrator accepts UserInputSchema
✓ Orchestrator calls Module Creation Agent (stubbed, returns mock outline)
✓ Module Creation Agent respects constraints (duration, depth, audience)
✓ Orchestrator returns valid CourseOutlineSchema
✓ UI displays generated outline

RESPONSIBILITIES
- Backend Lead: Orchestrator logic, agent dispatch
- Module Creation Owner: Initialization of core agent
- DevOps: LLM config (which model, API keys)

KEY FILES
- agents/orchestrator.py - CourseOrchestratorAgent implementation
- agents/module_creation_agent.py - Initial version (stateless generator)
- app.py - UI + orchestrator integration

AGENT IMPLEMENTATIONS
- ModuleCreationAgent: Mock/template-based outline generator
- All others: Still stubs

ORCHESTRATOR LOGIC (Simplified)
```
1. Receive UserInputSchema from UI
2. Validate constraints
3. Call ModuleCreationAgent(user_input + empty retrieval + empty web results)
4. Return CourseOutlineSchema to UI
```

EXIT CONDITION
✓ Full pipeline works: UI → Orchestrator → Module Agent → UI
✓ Outline respects duration constraint
✓ Outline respects depth and audience
✓ Output conforms to CourseOutlineSchema
✓ No external API calls yet (LLM mocked or simple template)

TESTING
- test_phase_2_orchestrator.py: Constraint checks, schema compliance

DURATION ESTIMATE: 4-5 days

---

🟢 PHASE 3 — Retrieval Agent & ChromaDB (Private Knowledge)
==============================================================================

🎯 GOAL
Add institutional knowledge retrieval (RAG).
Independent from other agents — can be tested in isolation.

DELIVERABLES
✓ ChromaDB initialized with sample curricula
✓ Document chunking & embedding pipeline
✓ Similarity search with metadata filtering
✓ Retrieval Agent calls vector DB autonomously
✓ Orchestrator calls Retrieval Agent in parallel

RESPONSIBILITIES
- RAG/ML Lead: ChromaDB setup, chunking strategy, QA of retrieval
- Backend Lead: Retrieval Agent implementation
- Data Lead: Sample curriculum ingestion

KEY FILES
- vectorstore/chroma_client.py - ChromaDB connector
- vectorstore/embeddings.py - Embedding provider (LangChain wrapper)
- agents/retrieval_agent.py - Autonomous retrieval logic
- data/sample_curricula/ - Sample docs for testing

DATA INGESTION
- Load sample curriculum PDFs (2-5 public syllabi)
- Chunk into ~500-token segments
- Embed using LangChain embeddings (OpenAI / Anthropic / local)
- Store in ChromaDB with metadata (institution, degree, year, tags)

RETRIEVAL AGENT AUTONOMY
Receives user_input → formulates query (topic + audience + depth) → searches DB

EXIT CONDITION
✓ ChromaDB has 5+ sample curricula (10K+ chunks)
✓ Similarity search returns relevant chunks
✓ Metadata filters work (institution, degree, year)
✓ Retrieval Agent is autonomous (no orchestrator instruction on what to search)
✓ Output conforms to RetrievalAgentOutput schema
✓ Orchestrator calls Retrieval Agent in parallel with Module Creation

TESTING
- test_phase_3_retrieval.py: Search accuracy, metadata filters, autonomy

DURATION ESTIMATE: 5-6 days

---

🟢 PHASE 4 — Web Search Agent (Public Knowledge)
==============================================================================

🎯 GOAL
Add external knowledge via web search (isolated).
Fallback strategy ensures resilience.

DELIVERABLES
✓ LangChain tool wrappers for Tavily, DuckDuckGo, SerpAPI
✓ Web Search Agent formulates queries autonomously
✓ Fallback logic when primary tool underperforms
✓ Results ranked by confidence
✓ Orchestrator calls Web Search Agent in parallel
✓ No hallucinated URLs

RESPONSIBILITIES
- Tool Integration Lead: LangChain tool setup
- Backend Lead: Web Search Agent, fallback logic
- QA Lead: URL validation, hallucination checks

KEY FILES
- tools/web_tools.py - Web search tool wrappers
- agents/web_search_agent.py - Autonomous query construction + fallback

TOOL STRATEGY
1. Try Tavily (most reliable for academia-oriented results)
2. Fallback to DuckDuckGo (privacy, no API key)
3. Fallback to SerpAPI (if configured)
4. Threshold: accept if top-3 results have relevance score > 0.6

EXIT CONDITION
✓ All three tools can be invoked
✓ Fallback triggers when primary results poor
✓ URLs in output are not hallucinated (spot-check)
✓ Confidence scores > 0.5
✓ Web Search Agent autonomous (formulates query from user_input)
✓ Orchestrator calls in parallel with Retrieval Agent

TESTING
- test_phase_4_web_search.py: Tool invocation, fallback, hallucination checks

DURATION ESTIMATE: 4-5 days

---

🟢 PHASE 5 — Module Creation Agent (Core Synthesis)
==============================================================================

🎯 GOAL
Implement the brain of the system.
Consumes all inputs (user choice + retrieved docs + web results + PDF).
Generates structured, constraint-respecting course outline.

DELIVERABLES
✓ Full Module Creation Agent implementation
✓ Prompt templates (Bloom-aware, backward design)
✓ Constraint enforcement (duration, depth, audience, learning_mode)
✓ Objective generation (measurable Bloom verbs)
✓ Assessment alignment
✓ Lesson breakdown with activities & resources
✓ Provenance tracking (which input influenced which module)
✓ Multiple candidate generation (optional: Theory-Oriented vs Project-Based)

RESPONSIBILITIES
- Curriculum/Instructional Designer Lead: Prompt templates, heuristics
- Backend Lead: Agent orchestration, constraint logic
- Content Lead: Validation of pedagogical soundness

KEY FILES
- agents/module_creation_agent.py - Full implementation
- prompts/module_creator.txt - Prompt template
- utils/scoring.py - Constraint validation helpers

INPUTS TO AGENT
```
{
  "user_input": UserInputSchema,
  "retrieved_docs": [RetrievedChunk],
  "web_results": [WebSearchResult],
  "pdf_content": Optional[str]
}
```

AGENT RESPONSIBILITIES
1. Parse inputs and extract key themes
2. Generate module structure
   - Count: scales with duration (e.g., 40 hrs → 5-6 modules)
   - Flow: follows pedagogical progression (simple → complex)
3. For each module, generate:
   - Title & synopsis
   - 3-7 learning objectives (Bloom-mapped, measurable)
   - Lesson breakdown (lessons, activities, timings)
   - Assessment (aligned to objectives)
   - Resources (with provenance)
4. Respect constraints:
   - Total hours = duration_hours
   - Learning_mode affects structure (async = more self-study, sync = more discussion)
   - Depth requirement affects content level (Conceptual = overview; Implementation = hands-on)
   - Audience level affects language/prerequisites
5. Track provenance (web result → module mapping, retrieved doc → lesson mapping)

OPTIONAL: GENERATE CANDIDATES
If time permits, generate 2-3 variants:
- Theory-Oriented (more lectures, fewer labs)
- Project-Based (fewer lectures, capstone project)
- Industry-Focused (real-world case studies)
Let validator rank them (PHASE 6).

EXIT CONDITION
✓ Objectives use proper Bloom verbs (Explain, Implement, Analyze, etc.)
✓ All objectives marked with Bloom level
✓ Module count scales with duration
✓ Learning mode affects structure (verifiable)
✓ Depth requirement affects content
✓ Audience level affects language
✓ Total hours sum matches requested duration
✓ Each module has 3-7 objectives
✓ Each objective has aligned assessment
✓ Provenance tracked for all resources
✓ Output is valid CourseOutlineSchema

TESTING
- test_phase_5_module_creation.py: Constraint checks, Bloom mapping, alignment

DURATION ESTIMATE: 8-10 days

---

🟢 PHASE 6 — Validator Agent (Quality Gate + Loop)
==============================================================================

🎯 GOAL
Introduce self-correction & agentic behavior (CRITICAL PHASE).
This is what turns a "prompt-based app" into an "agent system."

DELIVERABLES
✓ Rubric-based scoring (0-100)
✓ Scoring breakdown by category
✓ Targeted feedback generation
✓ Accept/Reject decision (threshold 75)
✓ Regeneration signal + Max retries
✓ Orchestrator retry loop

RESPONSIBILITIES
- Rubric Design Lead: Scoring criteria, calibration
- Backend Lead: Validator Agent, retry loop logic
- QA Lead: Score calibration on golden set of outlines

KEY FILES
- agents/validator_agent.py - Validator implementation
- utils/scoring.py - Rubric scoring logic
- agents/orchestrator.py - Retry loop integration

VALIDATOR RUBRIC (Total 100 points, Threshold 75)
```
Coverage & Coherence (0-25):
  - Are all expected topics represented?
  - Is the flow logical (prerequisites → building blocks → synthesis)?
  - Check: no orphan modules, no circular prerequisites

Audience Alignment (0-20):
  - Does depth match audience level?
  - Is language appropriate?
  - Check: undergrad outline != postgrad outline for same topic

Depth & Technical Accuracy (0-20):
  - Are concepts technically correct?
  - Is depth appropriate?
  - Check: Implementation-level has code examples; Conceptual doesn't

Assessability (0-15):
  - Are learning objectives measurable?
  - Are assessments aligned to objectives (1:1 mapping)?
  - Check: each objective has ≥1 assessment

Practicality / Feasibility (0-10):
  - Is pacing realistic?
  - Total hours vs content depth compatible?
  - Check: 40-hr course doesn't have 200 hrs of required reading

Originality & Duplication (0-10):
  - Is the structure unique (adds value vs copy)?
  - No plagiarism / hallucinated sources?
  - Check: web URLs are real (spot check)
```

VALIDATOR FEEDBACK FORMAT
```
{
  "score": 78,
  "rubric_breakdown": {
    "coverage": 22,
    "audience_alignment": 18,
    "depth_accuracy": 19,
    "assessability": 12,
    "practicality": 8,
    "originality": -1 // failed plagiarism check
  },
  "accept": true,  // score >= 75
  "feedback": [
    "Module 2 needs implementation examples (score: 12/15 on Technical Accuracy)",
    "Add assessment for LO 2.3 (Implement X) — currently unmeasured"
  ],
  "targeted_edits": {
    "module_2": "Add 2-3 hands-on labs with code examples",
    "assess_lo_2_3": "Add mini-project or coding exercise"
  },
  "regenerate_modules": null  // only set if accept=false
}
```

ORCHESTRATOR RETRY LOOP
```
DO:
  outline = ModuleCreationAgent.run(input)
  feedback = ValidatorAgent.run(outline)
  if feedback.score >= 75:
    ACCEPT and return
  else:
    // Regenerate with targeted feedback
    input.targeted_feedback = feedback.targeted_edits
    iteration_count++
WHILE score < 75 AND iteration_count < 3
IF iteration_count >= 3:
  LOG warning, return best-scored outline anyway
```

EXIT CONDITION
✓ Validator scores outlines consistently (gold-set calibration)
✓ Low-quality outlines score < 75
✓ High-quality outlines score >= 90
✓ Feedback is targeted and actionable
✓ Regeneration loop works (max 3 retries)
✓ Loop terminates after max retries
✓ UI shows acceptance/rejection reason

TESTING
- test_phase_6_validator.py: Scoring consistency, feedback quality, loop termination

DURATION ESTIMATE: 6-7 days

---

🟢 PHASE 7 — Query Agent (Interactive Explanations)
==============================================================================

🎯 GOAL
Enable educators to ask follow-ups, explore reasoning, and request targeted changes.
Session-aware conversational interface.

DELIVERABLES
✓ Query Agent answers common follow-ups
✓ Provenance-attached responses
✓ Session context awareness
✓ Confidence scoring
✓ Optional regeneration signal (single module)

RESPONSIBILITIES
- Conversation Lead: Query design, context management
- Backend Lead: Query Agent, context retrieval
- Frontend Lead: Chat UI in Streamlit

KEY FILES
- agents/query_agent.py - Query Agent implementation
- app.py - Chat interface integration

SAMPLE QUERIES (And Expected Behavior)
```
"Why is Module 2 included?"
  → Answer: "Module 2 (X) is included because your learning mode is 'Hybrid'
     and depth is 'Implementation'. The module prepares students for the capstone."
  Sources: [{'from': 'user_input.depth_requirement', ...}]
  Confidence: 0.9

"Can you simplify Module 3?"
  → Answer: "I can regenerate Module 3 with fewer prerequisites and simpler activities."
  can_regenerate_module: "M_3"

"What resources influenced the assessment strategy?"
  → Answer: "Assessment strategy is based on:
     1. Web source: https://... (Bloom's assessment best practices)
     2. Retrieved doc: XYZ Institution's rubric"
  Sources: [{'from': 'web', 'url': '...', 'confidence': 0.85}, ...]
  Confidence: 0.7
```

CONTEXT ACCESS
Query Agent has read-only access to:
- user_input (original request)
- retrieved_docs (from RAG)
- web_results (from web search)
- generated_outline (current)
- conversation_history (session)

EXIT CONDITION
✓ Queries are answered with context
✓ Sources are correctly cited (no hallucinations)
✓ Confidence scores reflect uncertainty
✓ Module regeneration can be triggered
✓ Session context preserved across queries

TESTING
- test_phase_7_query.py: Provenance accuracy, confidence calibration

DURATION ESTIMATE: 4-5 days

---

🟢 PHASE 8 — Streamlit UX Polish & Exports
==============================================================================

🎯 GOAL
Make the system educator-friendly and production-quality.

DELIVERABLES
✓ Editable outline sections (educator can tweak)
✓ Regenerate single-module button
✓ Multi-format exports (Markdown, PDF, JSON)
✓ Download links
✓ Feedback widget (optional: rate outline, comment)
✓ Preview pane
✓ Progress indicator during generation
✓ Error messages (graceful degradation)

RESPONSIBILITIES
- Frontend Lead: Full Streamlit UX
- Backend Lead: Export logic, error handling
- DevOps: Temp file cleanup, concurrency

KEY FILES
- app.py - Full UX implementation
- utils/session.py - Export helpers

EXPORT FORMATS
```
JSON: Full CourseOutlineSchema (can be re-imported)
Markdown: Readable format (for sharing, editing in Word/Notion)
PDF: Professional format (for printing, distribution)
```

EXIT CONDITION
✓ Educators can edit sections
✓ Regenerate button works
✓ All export formats work
✓ Exported files are valid (spot-check)
✓ Feedback reaches logging system
✓ Session cleans up after export

TESTING
- test_phase_8_ux.py: Export integrity, editing, buttons

DURATION ESTIMATE: 5-6 days

---

🟢 PHASE 9 — Observability, Monitoring & Metrics
==============================================================================

🎯 GOAL
Make the system production-ready: trackable, debuggable, improvable.

DELIVERABLES
✓ Structured logging (no PII)
✓ Agent latency tracking
✓ Validator score trends
✓ Regeneration frequency metrics
✓ Model token usage tracking
✓ Error rate monitoring
✓ Metrics dashboard (optional: simple Streamlit view)
✓ Audit trail (decisions, feedback, versions)

RESPONSIBILITIES
- DevOps / SRE Lead: Logging infrastructure, metrics export
- Backend Lead: Instrumentation across agents
- QA Lead: PII filtering, audit completeness

KEY FILES
- utils/logging.py - AudioLogger implementation
- app.py - Metrics dashboard

METRICS COLLECTED
```
Agent-level:
  - Name, duration_ms, input_tokens, output_tokens, success, error

Request-level:
  - session_id, user_input.audience_level, user_input.depth, 
    attempt_count, final_score, accepted, total_duration_ms

Quality-level:
  - validator_scores (trend), regeneration_frequency, 
    educator_feedback_rating (if submitted)

Error-level:
  - error_type, agent_name, timestamp, session_id
```

PII FILTERING
- No educator names
- No student data
- No PDF content
- No course titles if they contain sensitive info

DASHBOARD (Simple Streamlit View)
```
- Average validator score over time
- Regeneration frequency
- Error rate
- Agent latency distribution
- Educator satisfaction (if collected)
```

EXIT CONDITION
✓ All agents instrumented
✓ No PII in logs
✓ Metrics queryable
✓ Audit trail complete
✓ Dashboard functional

TESTING
- test_phase_9_observability.py: Logging accuracy, PII filtering, cleanup

DURATION ESTIMATE: 4-5 days

==============================================================================
🔷 SPRINT MAPPING (Example 4-week sprints)
==============================================================================

SPRINT 1 (Week 1-2):
  ✓ PHASE 0 (Foundation)
  ✓ PHASE 1 (UI + Session)
  ✓ PHASE 2 (Orchestrator v1)

SPRINT 2 (Week 3-4):
  ✓ PHASE 3 (Retrieval + ChromaDB)
  ✓ PHASE 4 (Web Search)

SPRINT 3 (Week 5-6):
  ✓ PHASE 5 (Module Creation Agent)

SPRINT 4 (Week 7-8):
  ✓ PHASE 6 (Validator + Loop)
  ✓ PHASE 7 (Query Agent)

SPRINT 5 (Week 9-10):
  ✓ PHASE 8 (UX Polish)
  ✓ PHASE 9 (Observability)

SPRINT 6+ (Week 11+):
  ✓ Integration testing
  ✓ Stage deployment
  ✓ Educator pilot
  ✓ Production deployment

==============================================================================
🔷 KEY GUARDRAILS
==============================================================================

1. EACH PHASE ADDS ONE CAPABILITY (No scope creep)
2. AGENTS ARE STATELESS & REPRODUCIBLE (no side effects outside session)
3. TESTS VALIDATE BOTH FUNCTIONALITY & CONSTRAINTS
4. PHASE N DOES NOT DEPEND ON PHASE N+1 IMPLEMENTATION
   (Phase 5 works even if Phase 6 validator is stubbed)
5. NO PII IN LOGS OR EXPORTS
6. SESSION DATA IS EPHEMERAL (auto-delete on completion)
7. EVERY EXTERNAL CALL (LLM, Web, DB) HAS TIMEOUT + RETRY LOGIC
8. VALIDATOR FEEDBACK IS EXPLAINABLE (educator can understand why)
9. ALL AGENT OUTPUTS CONFORM TO SCHEMA (no unvalidated outputs)
10. UNIT TESTS > INTEGRATION TESTS > E2E TESTS (pyramid)

==============================================================================
🔷 SUCCESS CRITERIA (Overall)
==============================================================================

Beta-Ready:
✓ End-to-end flow works (input → outline → output)
✓ Validator + retry loop works (agentic behavior)
✓ Tests pass (>80% code coverage)
✓ Educator can export in 3 formats
✓ No PII leaks

Pilot-Ready:
✓ 5+ educators use system with satisfaction > 4/5
✓ Outlines accepted on first try >= 60% of the time
✓ No unrecovered agent errors
✓ Metrics dashboard is correct

Production-Ready:
✓ <5 minute latency (p95) from input to outline
✓ 99% uptime SLA
✓ Zero PII incidents
✓ Educator feedback loop established
✓ Cost optimization done (model choice, caching)

==============================================================================
"""