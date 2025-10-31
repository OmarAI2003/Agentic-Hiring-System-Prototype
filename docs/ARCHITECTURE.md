# System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTIONS                             │
│  (HR Manager submits job posting, Interviewer provides feedback)    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    n8n WORKFLOW ORCHESTRATION                        │
│                    (Self-hosted, Open Source)                        │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Phase 1    │  │   Phase 3    │  │   Phase 5    │              │
│  │  Candidate   │  │  Interview   │  │  Evaluation  │              │
│  │  Sourcing    │  │  Questions   │  │  & Recommend │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PYTHON APPLICATION LAYER                       │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Phase 1: Sourcing Module                                      │  │
│  │  • Job Parser (extract requirements)                          │  │
│  │  • Candidate Generator (mock/real data)                       │  │
│  │  • 🤖 AI Scorer (adaptive ranking weights)                     │  │
│  │  • Ranking Engine (top N shortlist)                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Phase 3: Questions Module                                     │  │
│  │  • 🤖 Question Distribution AI (determine categories)          │  │
│  │  • Question Generator (role-specific)                         │  │
│  │  • Difficulty Adjuster (level-appropriate)                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Phase 5: Evaluation Module                                    │  │
│  │  • Feedback Analyzer (aggregate scores)                       │  │
│  │  • 🤖 AI Recommendation Engine (holistic decision)             │  │
│  │  • Report Generator (detailed output)                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AI/LLM LAYER (FREE)                             │
│                                                                       │
│         ┌──────────────────────────────────────────┐                │
│         │        Ollama + Llama 3                  │                │
│         │     (Local LLM - 100% Free)              │                │
│         │                                          │                │
│         │  • Autonomous decision-making            │                │
│         │  • Contextual reasoning                  │                │
│         │  • Natural language generation           │                │
│         └──────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA PERSISTENCE LAYER                            │
│                                                                       │
│                  ┌─────────────────────────┐                         │
│                  │   PostgreSQL Database   │                         │
│                  │      (Open Source)      │                         │
│                  │                         │                         │
│                  │  Tables:                │                         │
│                  │  • jobs                 │                         │
│                  │  • candidates           │                         │
│                  │  • job_applications     │                         │
│                  │  • interview_questions  │                         │
│                  │  • interview_feedback   │                         │
│                  │  • ai_recommendations   │                         │
│                  │  • system_logs          │                         │
│                  └─────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                             │
│                       (Optional/Future)                              │
│                                                                       │
│  • Email (Gmail API - Free tier)                                     │
│  • Calendar (Google Calendar API - Free)                             │
│  • LinkedIn (scraping or API)                                        │
│  • GitHub (public API - Free)                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Phase 1: Candidate Sourcing Flow

```
Job Posting Input
    │
    ├─→ Job Parser → Extract structured data
    │
    ├─→ Candidate Generator → Create/fetch candidate pool
    │
    ├─→ 🤖 AI Weight Determiner → Analyze job, decide optimal weights
    │       (Agentic AI: Autonomous decision based on job type)
    │
    ├─→ Scorer → Calculate match scores for each candidate
    │
    ├─→ Ranker → Sort and select top N candidates
    │
    └─→ Database → Save candidates + applications + scores
         │
         └─→ Output: Shortlist with rankings
```

### Phase 3: Question Generation Flow

```
Job + Candidate Input
    │
    ├─→ 🤖 AI Distribution Analyzer → Determine question categories
    │       (Agentic AI: Adapts based on role/level)
    │
    ├─→ Question Generator (per category)
    │       ├─→ Technical questions
    │       ├─→ Problem-solving questions
    │       ├─→ Behavioral questions
    │       └─→ System design questions
    │
    ├─→ Difficulty Adjuster → Match to experience level
    │
    └─→ Database → Save questions + metadata
         │
         └─→ Output: Customized question set
```

### Phase 5: Evaluation & Recommendation Flow

```
Interview Feedback Input
    │
    ├─→ Feedback Validator → Check data integrity
    │
    ├─→ Score Aggregator → Calculate averages + weighted scores
    │
    ├─→ 🤖 AI Recommendation Engine → Holistic analysis
    │       (Agentic AI: Beyond averaging, considers patterns)
    │       │
    │       ├─→ Analyze ratings
    │       ├─→ Evaluate comments
    │       ├─→ Consider job requirements
    │       ├─→ Assess growth potential
    │       └─→ Generate recommendation + justification
    │
    └─→ Database → Save recommendation + analysis
         │
         └─→ Output: Hire/Reject decision with confidence
```

## Agentic AI Decision Points

### 🤖 Decision Point 1: Ranking Weight Optimization (Phase 1)
**Location**: `python/sourcing/candidate_scorer.py`

**Input**: Job characteristics (title, level, location, skills)

**AI Task**: Determine optimal weights for:
- Skills match (30-50%)
- Experience match (15-35%)
- Location match (5-20%)
- Education match (10-25%)

**Agentic Behavior**: 
- Analyzes job type (technical vs non-technical)
- Considers experience level (entry needs more education weight)
- Adjusts for remote positions (location less important)

**Output**: Dictionary of optimized weights

---

### 🤖 Decision Point 2: Question Distribution (Phase 3)
**Location**: `python/questions/question_generator.py`

**Input**: Job details, candidate background

**AI Task**: Distribute 10 questions across:
- Technical knowledge
- Problem-solving
- Coding challenges
- System design
- Behavioral
- Situational

**Agentic Behavior**:
- Senior roles get more system design questions
- Entry roles focus on fundamentals
- Adapts to specific technical stack

**Output**: Question count per category

---

### 🤖 Decision Point 3: Hiring Recommendation (Phase 5)
**Location**: `python/evaluation/recommendation_engine.py`

**Input**: Interview ratings, comments, candidate profile, job requirements

**AI Task**: Make hiring decision (Strong Hire / Hire / Consider / Reject)

**Agentic Behavior**:
- Goes beyond simple score averaging
- Considers severity of concerns
- Evaluates growth potential
- Assesses risk vs opportunity
- Generates detailed justification

**Output**: Recommendation with confidence score and reasoning

---

## Technology Stack Summary

| Component | Technology | Cost |
|-----------|-----------|------|
| **Programming** | Python 3.9+ | FREE |
| **Database** | PostgreSQL | FREE (Open Source) |
| **LLM/AI** | Ollama + Llama 3 | FREE (Local) |
| **Orchestration** | n8n (self-hosted) | FREE (Open Source) |
| **ORM** | SQLAlchemy | FREE |
| **Mock Data** | Faker | FREE |
| **Web Framework** | Flask | FREE |
| **Calendar** | Google Calendar API | FREE (Tier) |
| **Email** | Gmail SMTP | FREE (Tier) |

**Total Cost: $0/month** 💰

---

## Scalability Considerations

### Current Limitations (Prototype)
- Single-machine deployment
- Limited to Ollama's local inference speed
- Mock data only
- Synchronous processing

### Production Scaling Path
1. **Database**: PostgreSQL with read replicas
2. **LLM**: 
   - Option A: Keep Ollama, add GPU server
   - Option B: Switch to free tier of Hugging Face Inference API
3. **Job Queue**: Add Redis + Celery for async processing
4. **Caching**: Redis for frequently accessed data
5. **API Layer**: Deploy Flask with Gunicorn + Nginx
6. **Monitoring**: Prometheus + Grafana (both free)

---

## Security Considerations

### Implemented
- Environment variable management (.env)
- SQL injection protection (SQLAlchemy ORM)
- Input validation in parsers

### Recommended for Production
- SSL/TLS for all connections
- API authentication (JWT tokens)
- Rate limiting on webhooks
- Encrypted candidate data storage
- GDPR compliance measures
- Audit logging

---

## Advantages of This Architecture

✅ **Completely Free**: No recurring costs
✅ **Privacy-First**: All data stays local
✅ **Transparent AI**: Full control over LLM prompts
✅ **Modular**: Easy to replace components
✅ **Extensible**: Add phases or features easily
✅ **Testable**: Each phase runs independently
✅ **Debuggable**: Clear logs and decision trails

---

**Built for learning, designed for autonomy, powered by open source** 🚀
