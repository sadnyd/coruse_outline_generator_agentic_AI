"""
Services Documentation

## Overview

The `services` package provides abstraction layers for external dependencies:
- **LLM Service**: Abstract interface for LLM providers (OpenAI, Anthropic, etc.)
- **Database Service**: Abstract interface for database providers (PostgreSQL, MongoDB, etc.)

This allows you to swap providers without modifying agent code.

---

## LLM Service

### Supported Providers
- OpenAI (GPT-3.5, GPT-4, GPT-4 Turbo)
- Anthropic Claude (Claude 2, Claude 3 Opus/Sonnet)
- Azure OpenAI (enterprise)
- Ollama (local)
- Gemini (Google)
- Groq
- Cohere

### Usage

**Basic Usage:**
```python
from services import get_llm_service

llm = get_llm_service()
response = await llm.generate(
    prompt="Explain machine learning",
    system_prompt="You are an expert educator."
)
print(response.content)
```

**Custom Configuration:**
```python
from services import LLMFactory, LLMConfig, LLMProvider

config = LLMConfig(
    provider=LLMProvider.ANTHROPIC,
    model="claude-3-opus-20240229",
    temperature=0.7,
    max_tokens=2000,
    api_key="sk-ant-..."
)

llm = LLMFactory.create_service(config)
response = await llm.generate("Your prompt here")
```

**Environment Variables:**
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000
LLM_API_KEY=sk-...
LLM_API_BASE=https://api.openai.com/v1
LLM_TIMEOUT=30
```

**Streaming Responses:**
```python
llm = get_llm_service()
async for chunk in llm.generate_streaming("Your prompt"):
    print(chunk, end="", flush=True)
```

**Token Estimation:**
```python
llm = get_llm_service()
tokens = llm.estimate_tokens("Your text here")
print(f"Estimated tokens: {tokens}")
```

---

## Database Service

### Supported Providers
- PostgreSQL (primary)
- MongoDB
- SQLite
- MySQL
- DynamoDB (AWS)
- Firestore (Google Cloud)
- Supabase (PostgreSQL wrapper)

### Usage

**Basic Usage:**
```python
from services import get_db_service

db = get_db_service()

# Save course
course_id = await db.save_course(
    user_id="user123",
    course_data={"title": "ML 101", "modules": [...]},
    session_id="sess456"
)

# Retrieve course
course = await db.get_course(course_id)

# List user courses
courses = await db.list_user_courses("user123")

# Delete course
await db.delete_course(course_id)
```

**Session Management:**
```python
db = get_db_service()

# Save session
await db.save_session(
    session_id="sess123",
    user_id="user456",
    session_data={"input": {...}, "status": "in_progress"}
)

# Retrieve session
session = await db.get_session("sess123")

# Delete session
await db.delete_session("sess123")
```

**User Management:**
```python
db = get_db_service()

# Create user
await db.create_user(
    user_id="user123",
    email="educator@example.com",
    profile={"role": "educator", "institution": "MIT"}
)

# Get user
user = await db.get_user("user123")

# Update user
await db.update_user(
    "user123",
    {"last_active": "2024-02-21", "preferences": {...}}
)
```

**Activity Logging:**
```python
db = get_db_service()

# Log activity
await db.log_activity(
    user_id="user123",
    action="course_generated",
    metadata={"course_id": "c456", "duration_hours": 40}
)

# Retrieve activity logs
logs = await db.get_activity_logs("user123", limit=50)
```

**Custom Configuration:**
```python
from services import DatabaseFactory, DatabaseConfig, DatabaseProvider

config = DatabaseConfig(
    provider=DatabaseProvider.POSTGRESQL,
    host="db.example.com",
    port=5432,
    username="courseai",
    password="secure_password",
    database="course_ai_prod",
    pool_size=20
)

db = DatabaseFactory.create_database(config)
await db.connect()
```

**Environment Variables:**
```bash
DB_PROVIDER=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=courseai
DB_PASSWORD=secure_password
DB_NAME=course_ai
DB_POOL_SIZE=10
DB_TIMEOUT=30
```

**Connection Management:**
```python
db = get_db_service()

# Connect
await db.connect()

# Health check
is_healthy = await db.health_check()
if is_healthy:
    print("Database is healthy")

# Disconnect
await db.disconnect()
```

**For Testing (Mock Database):**
```python
from services import set_db_service, MockDatabase, DatabaseConfig, DatabaseProvider

config = DatabaseConfig(
    provider=DatabaseProvider.SQLITE,  # Uses MockDatabase
)
mock_db = MockDatabase(config)
set_db_service(mock_db)
```

---

## Integration with Agents

### Example: CourseOrchestratorAgent

```python
from services import get_llm_service, get_db_service

class CourseOrchestratorAgent:
    def __init__(self):
        self.llm = get_llm_service()
        self.db = get_db_service()
    
    async def run(self, user_input):
        # Use LLM for content generation
        response = await self.llm.generate(f"Create course for: {user_input}")
        
        # Save to database
        course_id = await self.db.save_course(
            user_id=user_input.user_id,
            course_data={"content": response.content},
            session_id=user_input.session_id
        )
        
        return {"course_id": course_id, "content": response.content}
```

---

## Swapping Providers

**To change LLM provider from OpenAI to Anthropic:**

1. Update `.env`:
```bash
# Before
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_API_KEY=sk-...

# After
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
LLM_API_KEY=sk-ant-...
```

2. No code changes needed! The factory handles it.

**To change database from PostgreSQL to mock (testing):**

```python
from services import reset_llm_service, DatabaseProvider, DatabaseConfig, MockDatabase

# For testing
config = DatabaseConfig(provider=DatabaseProvider.SQLITE)
test_db = MockDatabase(config)
set_db_service(test_db)

# For production
reset_db_service()  # Reloads from env
```

---

## Adding New Providers

**To add a new LLM provider:**

```python
from services.llm_service import BaseLLMService, LLMFactory, LLMProvider

class MyLLMService(BaseLLMService):
    async def generate(self, prompt, system_prompt=None, **kwargs):
        # Implementation
        pass
    
    async def generate_streaming(self, prompt, system_prompt=None, **kwargs):
        # Implementation
        pass
    
    def estimate_tokens(self, text):
        # Implementation
        pass

# Register
LLMFactory.register_provider(LLMProvider.MY_PROVIDER, MyLLMService)
```

**To add a new database provider:**

```python
from services.db_service import BaseDatabase, DatabaseFactory, DatabaseProvider

class MyDatabase(BaseDatabase):
    async def connect(self):
        pass
    
    async def save_course(self, user_id, course_data, session_id):
        pass
    
    # ... implement all abstract methods
    pass

# Register
DatabaseFactory.register_provider(DatabaseProvider.MYDATABASE, MyDatabase)
```

---

## Best Practices

### LLM Service
- ✅ Use `get_llm_service()` for global instance
- ✅ Call `estimate_tokens()` before generating to avoid overages
- ✅ Set reasonable `max_tokens` to control costs
- ✅ Use `generate_streaming()` for long content (better UX)
- ❌ Don't hardcode provider names in agents
- ❌ Don't store API keys in code (use env vars)

### Database Service
- ✅ Always call `await db.connect()` before using
- ✅ Call `await db.health_check()` before critical ops
- ✅ Use transactions for multi-step operations
- ✅ Call `await db.disconnect()` on shutdown
- ✅ Use connection pooling for high concurrency
- ❌ Don't hardcode connection strings
- ❌ Don't store passwords in code (use env vars)

### Testing
- ✅ Use `MockDatabase` for unit tests
- ✅ Use `set_llm_service()` and `set_db_service()` to inject mocks
- ✅ Call `reset_llm_service()` and `reset_db_service()` in teardown
- ✅ Mock external API calls to avoid costs

---

## Migration Paths

### From Direct API Calls to Service Layer

**Before:**
```python
import openai

class Agent:
    async def run(self, prompt):
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
```

**After:**
```python
from services import get_llm_service

class Agent:
    async def run(self, prompt):
        llm = get_llm_service()
        response = await llm.generate(prompt)
        return response.content
```

### From Direct DB Calls to Service Layer

**Before:**
```python
import psycopg2

def save_course(user_id, course_data):
    conn = psycopg2.connect("host=localhost dbname=courseai")
    cur = conn.cursor()
    cur.execute("INSERT INTO courses VALUES ...")
    conn.commit()
```

**After:**
```python
from services import get_db_service

async def save_course(user_id, course_data):
    db = get_db_service()
    return await db.save_course(user_id, course_data, "sess_123")
```

---

## Troubleshooting

**LLM Service Issues:**

| Issue | Solution |
|-------|----------|
| "openai package required" | `pip install openai` |
| API key not found | Check `LLM_API_KEY` env var |
| Rate limit exceeded | Add retry logic, reduce request frequency |
| Timeout | Increase `LLM_TIMEOUT` env var |

**Database Service Issues:**

| Issue | Solution |
|-------|----------|
| "asyncpg required" | `pip install asyncpg` |
| Connection refused | Check host/port, db is running |
| Auth failed | Verify credentials in env vars |
| Pool exhausted | Increase `DB_POOL_SIZE` or reduce connections |

---

## Performance Tips

1. **LLM**: Cache responses for identical prompts
2. **LLM**: Use streaming for long responses
3. **LLM**: Estimate tokens before generation
4. **DB**: Use connection pooling (already configured)
5. **DB**: Batch inserts when possible
6. **DB**: Add indexes on frequently queried fields

---

## Security Considerations

- Store secrets in `.env` (never in code)
- Use HTTPS/TLS for all external connections
- Validate all inputs before passing to LLM/DB
- Implement rate limiting on sensitive operations
- Log security events (authentication, authorization)
- Rotate API keys regularly
- Use least-privilege DB credentials

---

Last Updated: February 21, 2026
Status: Production-ready abstraction layers
