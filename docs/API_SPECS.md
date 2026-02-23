"""
API Specification (PHASE 2+)

This document describes the REST API contracts for the Course AI Agent.
Implemented incrementally across phases.

==============================================================================
🔹 ENDPOINTS
==============================================================================

BASE_URL: http://localhost:8000/api

---

POST /outline
█████ Generate a course outline

Request:
  Content-Type: application/json
  {
    "course_title": "Introduction to Machine Learning",
    "course_description": "A comprehensive introduction...",
    "audience_level": "undergraduate",  # high_school | undergraduate | postgraduate | professional
    "audience_category": "cs_major",    # cs_major | non_cs_domain | industry_professional | self_learner
    "learning_mode": "hybrid",          # synchronous | asynchronous | hybrid
    "depth_requirement": "implementation",  # conceptual | applied | implementation | research
    "duration_hours": 40,
    "pdf_path": null,
    "custom_constraints": null
  }

Response: 200 OK
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "accepted",  # accepted | rejected | pending
    "outline": {
      "course_title": "...",
      "course_summary": "...",
      "audience_level": "undergraduate",
      "modules": [...],
      ...
    },
    "validator_score": 88,
    "regeneration_attempts": 2,
    "timestamp": "2025-02-21T10:30:00Z"
  }

Response: 400 Bad Request
  {
    "error": "Invalid audience_level: must be one of [...]",
    "field": "audience_level"
  }

---

POST /outline/{session_id}/query
█████ Ask a follow-up question about an outline

Request:
  Content-Type: application/json
  {
    "question": "Why is Module 2 included?"
  }

Response: 200 OK
  {
    "question": "Why is Module 2 included?",
    "answer": "Module 2 (Classification) is included because your learning mode is 'Hybrid' and depth is 'Implementation'. It prepares students for modules 3-4.",
    "sources": [
      {
        "type": "user_input",
        "field": "depth_requirement",
        "value": "implementation"
      },
      {
        "type": "web",
        "url": "https://...",
        "title": "Machine Learning Best Practices",
        "confidence": 0.85
      }
    ],
    "confidence": 0.92,
    "can_regenerate_module": null
  }

---

POST /outline/{session_id}/regenerate
█████ Regenerate a specific module

Request:
  Content-Type: application/json
  {
    "module_id": "M_2",
    "feedback": "Make this more hands-on with more code examples"
  }

Response: 200 OK
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "module_id": "M_2",
    "new_module": { ... },
    "validator_score": 82,
    "timestamp": "2025-02-21T10:35:00Z"
  }

---

GET /outline/{session_id}/export
█████ Export outline in different formats

Query Parameters:
  ?format=markdown | json | pdf

Response: 200 OK (Content-Type: varies)
  - format=markdown: text/markdown (plain text)
  - format=json: application/json (CourseOutlineSchema)
  - format=pdf: application/pdf (binary PDF)

---

POST /outline/{session_id}/feedback
█████ Submit educator feedback

Request:
  Content-Type: application/json
  {
    "rating": 4,  # 1-5
    "comment": "Great structure! Module 3 needs simpler prerequisites.",
    "modules_edited": ["M_3", "M_5"]
  }

Response: 200 OK
  {
    "status": "recorded",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-02-21T10:40:00Z"
  }

==============================================================================
🔹 ERROR RESPONSES
==============================================================================

400 Bad Request
  {
    "error": "Invalid input",
    "details": {
      "field": "duration_hours",
      "message": "Must be between 1 and 500"
    }
  }

404 Not Found
  {
    "error": "Session not found",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }

429 Too Many Requests
  {
    "error": "Rate limit exceeded",
    "retry_after_seconds": 60
  }

500 Internal Server Error
  {
    "error": "Agent failure",
    "agent": "module_creation_agent",
    "details": "LLM API timeout"
  }

==============================================================================
🔹 ASYNC EXAMPLE (Optional Polling)
==============================================================================

POST /outline (response: 202 Accepted, include Location header)
  Headers:
    Location: /api/outline/{session_id}

GET /outline/{session_id} (poll for status)
  Response: 200 OK
    {
      "status": "processing",  # processing | accepted | rejected
      "progress": 0.6,
      "current_stage": "validator",
      "timestamp": "2025-02-21T10:32:00Z"
    }

When status changes to "accepted":
  GET /outline/{session_id}
    {
      "status": "accepted",
      "outline": { ... }
    }

---

Approved March 2025
"""