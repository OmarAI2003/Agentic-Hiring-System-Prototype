# 🤖 Agentic Hiring System - Complete Automation# Agentic-Hiring-System-Prototype

Agentic AI-Powered HR Recruitment System Prototype built with n8n.

A fully automated end-to-end recruitment system powered by AI that handles everything from job posting to interview scheduling with **zero manual intervention**.

[![n8n](https://img.shields.io/badge/n8n-1A1A1A?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io/)

## ✨ Key Features[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)



### **Fully Automatic Workflow**

1. **AI-Powered Job Descriptions** - Generate professional job descriptions from just a title using Groq AI (Llama 3.3 70B)<a id=""></a>

2. **Smart Candidate Sourcing** - Automatically generate mock candidates or integrate with real sources

3. **Automated MCQ Generation** - AI creates relevant technical assessment questions

4. **Email Automation** - Sends onboarding and MCQ assessment links automatically## **Contents**

5. **Intelligent Interview Scheduling** - Automatically schedules interviews based on MCQ performance

   - **≤3 candidates**: Sends interview invitations immediately after each MCQ- [🎯 Overview `⇧`](#overview-)

   - **>3 candidates**: Waits for all to complete, then selects top 3 performers- [🌟 Features `⇧`](#features-)

- [🏗️ Architecture `⇧`](#architecture-)

### **Zero Manual Steps After Job Creation**- [🛠️ Environment setup `⇧`](#environment-setup-)

Once HR creates a job, the system handles:- [🧩 Project Structure `⇧`](#project-structure-)

- ✅ Candidate sourcing

- ✅ Email sending<a id="overview-"></a>

- ✅ MCQ assessment

- ✅ Performance evaluation# Agentic AI HR Recruitment System 🤖

- ✅ Interview invitation scheduling

An intelligent, autonomous HR recruitment system demonstrating agentic AI principles through smart candidate sourcing, interview question generation, and data-driven hiring recommendations—**built entirely with FREE, open-source tools**.

## 🚀 Quick Start

## � Key Features

### Prerequisites

- Python 3.8+### ✅ **Completely FREE Stack**

- Gmail account with App Password- **No Paid APIs**: Uses Ollama with Llama 3 (local LLM)

- Groq API key (free at console.groq.com)- **Open Source Database**: PostgreSQL

- **Self-Hosted Orchestration**: n8n (self-hosted)

### Installation- **Free Mock Data**: Faker library for candidate generation



```bash### 🧠 **Agentic AI Principles**

# Clone the repository

git clone https://github.com/OmarAI2003/Agentic-Hiring-System-Prototype.git1. **Autonomous Decision-Making**: AI intelligently determines ranking weights based on job characteristics

cd Agentic-Hiring-System-Prototype2. **Goal-Driven Behavior**: System adapts strategies to find optimal candidates for each role

3. **Tool Coordination**: Seamlessly orchestrates database, LLM, email, and scheduling systems

# Install dependencies4. **Contextual Reasoning**: Analyzes job requirements and candidate profiles holistically

pip install -r requirements.txt

## 🏗️ System Architecture

# Setup environment variables

cp .env.example .env```

# Edit .env and add your credentials:┌─────────────────────────────────────────────────────────────┐

#   GROQ_API_KEY=your_groq_api_key│                    n8n Workflow Orchestration                │

#   GMAIL_EMAIL=your_gmail@gmail.com└─────────────────────────────────────────────────────────────┘

#   GMAIL_APP_PASSWORD=your_16_char_app_password                              │

```        ┌─────────────────────┼─────────────────────┐

        │                     │                     │

### Running the System   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐

   │ Phase 1 │          │ Phase 3 │          │ Phase 5 │

Open **3 terminal windows** and run:   │Sourcing │          │Questions│          │  Eval   │

   └────┬────┘          └────┬────┘          └────┬────┘

```bash        │                     │                     │

# Terminal 1: HR Control Panel        └─────────────────────┼─────────────────────┘

python start_hr_panel.py                              │

# Access at: http://localhost:3000                    ┌─────────▼──────────┐

                    │   Ollama + Llama3   │

# Terminal 2: Onboarding Form Server                    │   (Local LLM - FREE)│

python start_form_server.py                    └─────────┬──────────┘

# Running on: http://localhost:5000                              │

                    ┌─────────▼──────────┐

# Terminal 3: MCQ Assessment Server                      │   PostgreSQL DB     │

python start_mcq_server.py                    │   (FREE)            │

# Running on: http://localhost:5001                    └────────────────────┘

``````



### Usage## 📦 Implemented Phases



1. **Open HR Panel**: Navigate to http://localhost:3000### ✅ Phase 1: Candidate Sourcing & Ranking

2. **Create Job**:**Demonstrates**: Autonomous decision-making, adaptive ranking

   - Enter job title (e.g., "Python Developer")

   - Click "Generate with AI" for automatic job description**Features**:

   - Enter number of candidates- Intelligent job description parsing

   - Enter Gmail credentials (pre-filled with defaults)- Mock candidate generation (tailored to job requirements)

3. **Click "Start Recruitment Workflow"**- **AI-driven ranking weights**: Automatically determines optimal scoring factors based on:

4. **Done!** The system handles everything automatically:  - Job experience level (entry/mid/senior)

   - Sources candidates  - Role type (technical vs non-technical)

   - Generates MCQ questions  - Location requirements (remote vs on-site)

   - Sends onboarding emails- Smart candidate scoring across multiple dimensions

   - Sends MCQ assessment links- Top candidate shortlisting

   - Evaluates performance

   - Sends interview invitations to top performers**Agentic Behavior**: System autonomously decides how to weight skills match, experience, location, and education based on job context.



## 📧 Automatic Email Flow### ✅ Phase 3: Interview Question Generation

**Demonstrates**: Context-aware content generation, role adaptation

The system sends 4 types of automated emails:

**Features**:

1. **Onboarding Email** - Welcome with form link- **AI determines question distribution** across categories:

2. **MCQ Assessment Email** - Technical assessment link    - Technical knowledge

3. **Feedback Email** - Score and results after MCQ completion  - Problem-solving

4. **Interview Invitation** - Sent to top performers with time slot options  - Coding challenges

  - System design

## 🎯 Interview Scheduling Logic  - Behavioral questions

- Difficulty adjustment based on experience level

### For Small Candidate Pools (≤3 candidates)- Personalized questions when candidate data available

- Sends interview invitations **immediately** after each candidate completes their MCQ- Expected answers and evaluation criteria included

- All candidates receive interview invitations (fair opportunity)

**Agentic Behavior**: AI analyzes job requirements and candidate background to generate relevant, appropriately challenging questions.

### For Large Candidate Pools (>3 candidates)

- Waits for **all candidates** to complete MCQ assessments### ✅ Phase 5: Evaluation & Recommendations

- Ranks by performance**Demonstrates**: Holistic reasoning, multi-factor decision-making

- Selects **top 3 performers**

- Sends interview invitations with 6 time slot options**Features**:

- **AI-powered candidate assessment** (not just score averaging)

## 📁 Project Structure- Analyzes:

  - Interview ratings

```  - Interviewer comments

Agentic-Hiring-System-Prototype/  - Candidate background

├── hr_control_panel.py          # Main HR web interface  - Job requirements

├── start_hr_panel.py             # HR panel launcher- Generates:

├── start_form_server.py          # Onboarding form launcher  - Recommendation (Strong Hire / Hire / Consider / Reject)

├── start_mcq_server.py           # MCQ assessment launcher  - Confidence score

├── python/  - Detailed justification

│   ├── sourcing/                 # Candidate sourcing engine  - Key strengths and weaknesses

│   ├── questions/                # MCQ generation & server  - Suggested next steps

│   │   ├── mcq_generator.py

│   │   └── mcq_form_server.py**Agentic Behavior**: AI makes nuanced hiring decisions by considering patterns, concerns, and growth potential—not just numeric scores.

│   ├── onboarding/               # Form & email automation

│   │   ├── email_automation.py## 🚀 Quick Start

│   │   └── web_form.py

│   ├── interview/                # Interview scheduling### Prerequisites

│   │   └── interview_scheduler.py

│   └── evaluation/               # Recommendation engine1. **Python 3.9+**

├── templates/                    # HTML templates2. **PostgreSQL** (Free)

├── data/                         # Storage (gitignored)3. **Ollama** with Llama 3 model (Free, local LLM)

│   ├── jobs/                     # Job postings4. **n8n** (Self-hosted, free)

│   ├── candidates/               # Candidate data

│   ├── questions/                # Generated MCQs### Installation

│   ├── answers/                  # MCQ responses

│   └── forms/                    # Onboarding responses```bash

├── config/                       # Configuration files# 1. Clone the repository

├── AUTOMATIC_WORKFLOW.md         # Detailed workflow documentationgit clone <repository-url>

├── QUICK_START.md                # Quick start guidecd Agentic-Hiring-System-Prototype

└── README.md                     # This file

```# 2. Install Python dependencies

pip install -r requirements.txt

## 🔧 Configuration

# 3. Install and setup Ollama (if not already installed)

### Gmail Setup# Visit: https://ollama.ai

1. Enable 2-Factor Authentication in your Google Account# Then pull Llama 3:

2. Generate App Password: https://myaccount.google.com/apppasswordsollama pull llama3

3. Use the 16-character password in the system

# 4. Setup PostgreSQL database

### Groq API Setup# Create database

1. Sign up at: https://console.groq.comcreatedb hr_recruitment

2. Create API key

3. Add to `.env` file# Initialize schema

psql hr_recruitment < database/schema.sql

## 📝 Documentation# OR use Python ORM:

python -c "from database.models import init_database; init_database()"

- **[AUTOMATIC_WORKFLOW.md](AUTOMATIC_WORKFLOW.md)** - Detailed workflow explanation with scenarios

- **[QUICK_START.md](QUICK_START.md)** - Step-by-step setup guide# 5. Configure environment

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture detailscp .env.example .env

# Edit .env with your settings

## 🧪 Testing

# 6. Create required directories

1. **Create a test job** with 2-3 candidatespython -c "from python.utils.helpers import ensure_directories; ensure_directories()"

2. **Use your own email** as test candidate email```

3. **Check your inbox** for automated emails

4. **Complete the workflow** from onboarding → MCQ → interview invitation### Running the System



## 🤝 Contributing#### Option 1: Run Phases Individually



Contributions are welcome! Please feel free to submit a Pull Request.```bash

# Phase 1: Candidate Sourcing

## 📄 Licensepython -m python.sourcing.main



This project is open source and available under the MIT License.# Phase 3: Interview Questions

python -m python.questions.question_generator

## 🙏 Acknowledgments

# Phase 5: Evaluation & Recommendations

- **Groq** for fast LLM inferencepython -m python.evaluation.recommendation_engine

- **Flask** for web framework```

- Built with ❤️ for automated recruitment

#### Option 2: Use n8n Workflows

---

```bash

**Created by**: Omar AI  # 1. Start n8n (self-hosted)

**GitHub**: [@OmarAI2003](https://github.com/OmarAI2003)  npx n8n

**Project**: Agentic Hiring System Prototype

# 2. Import workflows from n8n_workflows/ directory
# 3. Configure webhook URLs in your .env
# 4. Trigger workflows via HTTP POST
```

## 📊 Database Schema

The system uses PostgreSQL with the following core tables:

- **`jobs`**: Job postings with requirements
- **`candidates`**: Candidate profiles and information
- **`job_applications`**: Applications with match scores and rankings
- **`interview_questions`**: AI-generated interview questions
- **`interview_schedule`**: Interview appointments
- **`interview_feedback`**: Interviewer ratings and comments
- **`ai_recommendations`**: AI-generated hiring recommendations
- **`system_logs`**: Tracks all agentic AI decisions

## 🧪 Testing

```bash
# Test LLM connection
python python/utils/llm_client.py

# Test job parser
python python/sourcing/job_parser.py

# Test candidate generator
python python/sourcing/candidate_generator.py

# Test scoring system
python python/sourcing/candidate_scorer.py

# Run full Phase 1 pipeline
python python/sourcing/main.py
```

## �🎯 How It Demonstrates Agentic AI

### 1. **Autonomous Decision-Making**
- AI independently determines optimal ranking weights without hardcoded rules
- Adapts question difficulty and distribution based on role analysis
- Makes hiring recommendations considering multiple contextual factors

### 2. **Goal-Driven Behavior**
- Optimizes for finding best-fit candidates, not just highest scores
- Balances technical skills, cultural fit, and growth potential
- Adjusts strategies based on job characteristics

### 3. **Tool Coordination**
- Seamlessly integrates: Database ↔ LLM ↔ Email ↔ Calendars
- Manages state across multiple workflow phases
- Handles errors and fallbacks intelligently

### 4. **Contextual Reasoning**
- Understands job-candidate fit beyond keyword matching
- Generates personalized interview questions
- Provides nuanced recommendations with justifications

## 📁 Project Structure

```
Agentic-Hiring-System-Prototype/
├── python/
│   ├── sourcing/               # Phase 1: Candidate Sourcing
│   │   ├── job_parser.py       # Job description parser
│   │   ├── candidate_generator.py  # Mock candidate generation
│   │   ├── candidate_scorer.py # Intelligent scoring & ranking
│   │   └── main.py             # Phase 1 orchestrator
│   ├── questions/              # Phase 3: Interview Questions
│   │   └── question_generator.py
│   ├── evaluation/             # Phase 5: Evaluation & Recommendations
│   │   └── recommendation_engine.py
│   └── utils/
│       ├── helpers.py          # Utility functions
│       └── llm_client.py       # Ollama/Llama3 integration
├── database/
│   ├── schema.sql              # PostgreSQL schema
│   └── models.py               # SQLAlchemy ORM models
├── n8n_workflows/              # n8n workflow definitions
│   ├── phase1_candidate_sourcing.json
│   ├── phase3_interview_questions.json
│   └── phase5_evaluation.json
├── data/                       # Generated data
│   ├── jobs/
│   ├── candidates/
│   └── questions/
├── reports/                    # Generated reports
├── logs/                       # System logs
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configuration

Key environment variables (`.env`):

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hr_recruitment
DB_USER=postgres
DB_PASSWORD=your_password

# Ollama (Local LLM - FREE)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Application
MOCK_DATA_ENABLED=true
CANDIDATE_POOL_SIZE=100
TOP_CANDIDATES_COUNT=10
```

## 🎓 Key Technologies

- **Python 3.9+**: Core application logic
- **PostgreSQL**: Database (free, open-source)
- **Ollama + Llama 3**: Local LLM inference (100% free)
- **SQLAlchemy**: ORM for database operations
- **Faker**: Mock data generation
- **n8n**: Workflow automation (self-hosted, free)
- **Flask**: API endpoints for webhooks

## 🚧 Limitations & Assumptions

1. **Mock Data**: Uses generated candidate profiles (not real LinkedIn/GitHub scraping)
2. **Local LLM**: Ollama/Llama 3 performance depends on hardware
3. **No Real Integrations**: Placeholder for Google Calendar, email services
4. **Simplified Scheduling**: Phase 2 and 4 not fully implemented
5. **Single Interviewer**: Doesn't handle panel interviews

## 🔮 Future Enhancements

- [ ] Real LinkedIn/GitHub API integration
- [ ] Phase 2: Automated onboarding forms
- [ ] Phase 4: Calendar scheduling with timezone handling
- [ ] Multi-interviewer feedback aggregation
- [ ] Advanced NLP for resume parsing
- [ ] Bias detection and fairness metrics
- [ ] Integration with ATS systems
- [ ] Candidate communication chatbot

## 📜 License

MIT License - Free to use and modify

## 🤝 Contributing

Contributions welcome! This is an educational/demo project showcasing agentic AI principles.

## 📞 Support

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ using 100% FREE, open-source tools**

**No paid APIs • No subscriptions • Fully self-hosted**



<a id="features-"></a>

# 🌟 Features [`⇧`](#contents)
