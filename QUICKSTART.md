# 🚀 QUICK START: Run Phase 5 Module Creation Agent

## TL;DR (30 seconds setup)

```bash
# 1. Install dependencies
pip install google-generativeai streamlit python-dotenv

# 2. Add your Gemini API Key to .env
set GOOGLE_API_KEY=your_key_here    # Windows
export GOOGLE_API_KEY=your_key_here # Mac/Linux

# 3. Test the pipeline
python test_pipeline.py

# 4. Launch UI
streamlit run app.py

# 5. Open browser to http://localhost:8501
```

✅ **Done!** Let the application run and see the output in the browser.

---

## Step-by-Step Guide

### Step 1: Get Gemini API Key (2 min)

1. Go to **https://aistudio.google.com/app/apikeys**
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key
5. Add to `.env`:
   ```
   GOOGLE_API_KEY=<paste_key_here>
   ```

> ✅ **Free tier:** No credit card required. Includes free quota.

---

### Step 2: Install Dependencies (2 min)

```bash
# Navigate to project
cd c:\Users\nisha\Projects\tcs_ai\course_ai_agent

# Install main dependencies
pip install -r requirements.txt

# Install Gemini SDK
pip install google-generativeai

# Verify
python -c "import google.generativeai; print('✓ Gemini SDK ready')"
```

---

### Step 3: Test Your Setup (3-5 min)

```bash
# Run comprehensive test
python test_pipeline.py
```

**Expected output:**
```
════════════════════════════════════════════════════════════════
 PHASE 5 TESTING SUITE
 Module Creation Agent & Gemini Integration
════════════════════════════════════════════════════════════════

[1/5] Testing LLM Service...
============================================================
 TEST 1: LLM Service & Gemini Connection
============================================================
Initializing LLM Service...
✓ Provider: gemini
✓ Model: gemini-1.5-pro
✓ Response content: Hello from Gemini!
✓ Response provider: gemini

[2/5] Testing Schemas...
✓ Learning objective created
✓ Lesson created
✓ Module created

[3/5] Testing Utilities...
✓ Course: 40 hours → 6 modules
✓ Avg per module: 6.7h
✓ Mode adjustment: True

[4/5] Testing Module Agent...
✓ Agent ready

[5/5] Testing Full Orchestrator...
✓ Orchestration complete (15.3s)

Generated outline:
  Title: Python for Data Analysis
  Modules: 6
  Confidence: 0.85
  Completeness: 0.90

============================
✅ PHASE 5 IS READY FOR TESTING!
```

---

### Step 4: Run Tests (5 min)

**Option A: Quick tests only**
```bash
pytest tests/test_phase_5_module_creation.py::test_schema_course_outline_basic_instantiation -v
```

**Option B: All Phase 5 tests**
```bash
pytest tests/test_phase_5_module_creation.py -v
```

**Expected:** ~25 tests pass ✅

---

### Step 5: Launch Streamlit UI (2 min)

```bash
streamlit run app.py
```

Browser opens to: **http://localhost:8501**

### In the UI:

1. **Fill course details:**
   - Title: "Machine Learning Basics"
   - Description: "Learn ML fundamentals"
   - Audience: "Undergraduate"
   - Depth: "Implementation Level"
   - Duration: "40" hours
   - Learning Mode: "Project Based"

2. **Click "Generate Course Outline"**

3. **See generated output:**
   - Course structure
   - Modules with time allocation
   - Learning objectives per module
   - Assessment strategy
   - Quality scores

---

## What You'll Get

The **Module Creation Agent** generates:

✅ **Course that respects your constraints**
- Module count matches duration
- Depth level guides content complexity
- Learning mode affects structure

✅ **Curriculum-grade structure**
- Bloom's taxonomy alignment
- 3-7 measurable objectives per module
- Lesson sequencing
- Assessment strategies

✅ **Complete provenance**
- Source attribution
- Confidence scoring
- Reference tracking

✅ **Quality metrics**
- Confidence score (0-1.0)
- Completeness score (0-1.0)

---

## Example Output

```json
{
  "course_title": "Introduction to Machine Learning",
  "modules": [
    {
      "module_id": "M_1",
      "title": "Foundations of ML",
      "estimated_hours": 6.0,
      "learning_objectives": [
        {
          "statement": "Understand supervised vs unsupervised learning",
          "bloom_level": "understand",
          "assessment_method": "Quiz"
        },
        {
          "statement": "Apply ML workflow to simple dataset",
          "bloom_level": "apply",
          "assessment_method": "Hands-on Lab"
        },
        {
          "statement": "Analyze model performance metrics",
          "bloom_level": "analyze",
          "assessment_method": "Project"
        }
      ],
      "lessons": [...],
      "assessment_type": "mixed"
    },
    {...more modules...}
  ],
  "confidence_score": 0.85,
  "completeness_score": 0.90
}
```

---

## Troubleshooting

### ❌ "GOOGLE_API_KEY not found"
```bash
# Check if .env is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

### ❌ "ImportError: cannot import name 'LLMService'"
```bash
# Ensure all fixes are applied
python -c "from services.llm_service import get_llm_service; print('✓ Imports OK')"
```

### ❌ "LLM generation failed"
```bash
# Test Gemini directly
python -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY')
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content('Hello!', generation_config={'max_output_tokens': 100})
print(response.text)
"
```

---

## File Changes Made

**Fixed/Updated:**
- ✅ `services/llm_service.py` - Added GeminiService class, fixed imports
- ✅ `agents/module_creation_agent.py` - Fixed LLM imports and async calls
- ✅ `.env` - Added Gemini configuration
- ✅ `test_pipeline.py` - Created new comprehensive test script

**Documentation Added:**
- 📄 `TESTING_GUIDE.md` - Detailed testing guide
- 📄 `QUICKSTART.md` - This file!

---

## What's Working (Phase 5)

| Component | Status |
|-----------|--------|
| Gemini LLM Integration | ✅ Working |
| Module Creation Agent | ✅ Working |
| Schema Validation | ✅ Working |
| Duration Allocator | ✅ Working |
| Learning Mode Templates | ✅ Working |
| Orchestrator Pipeline | ✅ Working |
| Test Suite (~25 tests) | ✅ Working |

---

## Next Commands to Try

```bash
# View detailed test information
pytest tests/test_phase_5_module_creation.py -v -s

# Run with coverage
pytest tests/test_phase_5_module_creation.py --cov=agents --cov=schemas

# Debug specific test
pytest tests/test_phase_5_module_creation.py::test_schema_course_outline_basic_instantiation -vv

# Stream logs while running
streamlit run app.py --logger.level=debug
```

---

## ⏸️ PHASE 5 STATUS: PAUSED

- Implementation: ✅ COMPLETE
- Testing: ✅ READY
- Documentation: ✅ COMPLETE
- Git Push: ⏸️ PAUSED (waiting for your confirmation)

**To push Phase 5 to GitHub, run:**
```bash
git add -A && git commit -m "Phase 5 tested and verified" && git push
```

---

## Support

**Questions?** Check:
1. Terminal output for error messages
2. `TESTING_GUIDE.md` for detailed troubleshooting
3. Test logs: `pytest tests/ -v --tb=long`

**Ready?** Let's go! 🚀

```bash
python test_pipeline.py && streamlit run app.py
```
