# Quick Start Guide

## Prerequisites Check

### 1. Python
```bash
python --version  # Should be 3.9+
```

### 2. PostgreSQL
```bash
psql --version
```

### 3. Ollama
```bash
ollama --version
```

If not installed:
- Download from: https://ollama.ai
- Pull Llama 3: `ollama pull llama3`
- Start: `ollama serve`

## Installation (5 minutes)

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env with your database credentials

# 3. Initialize database
python -c "from database.models import init_database; init_database()"

# 4. Create directories
python -c "from python.utils.helpers import ensure_directories; ensure_directories()"
```

## Run Your First Pipeline

### Phase 1: Candidate Sourcing

```bash
python -m python.sourcing.main
```

**What it does:**
1. Parses a sample job posting
2. Generates 100 mock candidates
3. AI determines optimal ranking weights
4. Scores and ranks all candidates
5. Shortlists top 10
6. Saves to database
7. Generates report

**Expected output:**
```
🚀 STARTING PHASE 1: CANDIDATE SOURCING PIPELINE
📝 Processing job posting: Senior Python Developer
🔍 Sourcing 100 candidates...
🤖 AI autonomously determining ranking weights...
📊 Ranking 100 candidates...
✓ Shortlisted top 10 candidates
💾 Saving candidates to database...
✓ PHASE 1 PIPELINE COMPLETED SUCCESSFULLY

Top 5 Candidates:
  1. Alice Johnson - Score: 94.23
  2. Bob Martinez - Score: 91.87
  ...
```

### Phase 3: Interview Questions

```bash
python -m python.questions.question_generator
```

**What it does:**
1. Takes job requirements
2. AI determines question distribution
3. Generates 10 customized questions
4. Includes expected answers and evaluation criteria

### Phase 5: Evaluation

```bash
python -m python.evaluation.recommendation_engine
```

**What it does:**
1. Analyzes interview feedback
2. AI makes holistic hiring decision
3. Provides confidence score and justification
4. Suggests next steps

## Testing Components

### Test LLM Connection
```bash
python python/utils/llm_client.py
```

Should output: "✓ Ollama connection successful!"

### Test Job Parser
```bash
python python/sourcing/job_parser.py
```

### Test Candidate Generator
```bash
python python/sourcing/candidate_generator.py
```

### Test Scoring System
```bash
python python/sourcing/candidate_scorer.py
```

## Using n8n Workflows

### Setup n8n
```bash
# Install (one-time)
npm install -g n8n

# Start
n8n
```

Navigate to: http://localhost:5678

### Import Workflows
1. Click "Workflows" → "Import from File"
2. Import from `n8n_workflows/` directory:
   - `phase1_candidate_sourcing.json`
   - `phase3_interview_questions.json`
   - `phase5_evaluation.json`

### Trigger Workflows

**Phase 1 - Candidate Sourcing:**
```bash
curl -X POST http://localhost:5678/webhook/job-posting \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We need an experienced Python developer...",
    "required_skills": ["Python", "Django", "PostgreSQL"],
    "experience_level": "senior",
    "location": "Remote"
  }'
```

**Phase 3 - Generate Questions:**
```bash
curl -X POST http://localhost:5678/webhook/generate-questions \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "candidate_id": 5,
    "question_count": 10
  }'
```

**Phase 5 - Submit Feedback:**
```bash
curl -X POST http://localhost:5678/webhook/submit-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "candidate_id": 5,
    "interviewer_email": "interviewer@company.com",
    "technical_skills_rating": 9,
    "communication_skills_rating": 8,
    "culture_fit_rating": 9,
    "problem_solving_rating": 8,
    "strengths": "Excellent Python skills, great problem solver",
    "concerns": "Limited distributed systems experience",
    "qualitative_comments": "Very strong candidate overall"
  }'
```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Start Ollama
ollama serve

# In another terminal, verify:
ollama list
# Should show llama3
```

### "Database connection failed"
```bash
# Check PostgreSQL is running
pg_ctl status

# Create database if needed
createdb hr_recruitment

# Test connection
psql hr_recruitment
```

### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Performance Issues
- **Ollama slow**: Llama 3 requires decent hardware (8GB+ RAM recommended)
- **Use smaller model**: `ollama pull llama3:8b` (8 billion parameter version)
- **Disable AI features**: Set `use_ai_weights=False` in code

## Next Steps

1. **Customize for your use case:**
   - Edit `python/sourcing/job_parser.py` for your job requirements
   - Modify ranking weights in `candidate_scorer.py`
   - Adjust question templates

2. **Add real integrations:**
   - LinkedIn API for real candidate sourcing
   - Google Calendar API for scheduling
   - Email service (SendGrid, etc.)

3. **Enhance AI capabilities:**
   - Fine-tune prompts in `llm_client.py`
   - Add more evaluation criteria
   - Implement bias detection

## Support

- Check `logs/system.log` for detailed execution logs
- Review `reports/` directory for generated reports
- See `data/` directory for intermediate outputs

**Happy Recruiting! 🚀**
