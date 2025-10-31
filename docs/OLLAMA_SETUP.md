# 🦙 Ollama + Llama3 Setup Guide

This guide walks you through installing Ollama and Llama3 to enable AI-powered agentic decision-making in the HR Recruitment System.

---

## Why Ollama?

**Ollama** provides:
- ✅ **100% FREE** local LLM hosting
- ✅ **No API costs** (unlike OpenAI, Anthropic)
- ✅ **Privacy** - all data stays on your machine
- ✅ **Fast inference** - optimized for local GPUs/CPUs
- ✅ **Simple API** - REST API compatible with Python

**Llama3** is Meta's open-source LLM with:
- Excellent reasoning capabilities
- Strong code generation
- Good at structured output (JSON)
- Available in 8B and 70B parameter versions

---

## Installation Steps

### 1. Download Ollama

**Windows:**
```bash
# Download installer from:
https://ollama.ai/download/windows

# Or use winget:
winget install Ollama.Ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
# Download from:
https://ollama.ai/download/mac

# Or use Homebrew:
brew install ollama
```

### 2. Start Ollama Service

**Windows:**
- Ollama runs automatically after installation
- Check system tray for Ollama icon

**Linux/macOS:**
```bash
# Start as background service
ollama serve

# Or use systemd (Linux):
systemctl start ollama
```

### 3. Pull Llama3 Model

```bash
# Pull the 8B parameter model (recommended, ~4.7GB)
ollama pull llama3

# OR pull the 70B model (if you have powerful hardware, ~40GB)
ollama pull llama3:70b
```

**Download time:** 5-10 minutes depending on internet speed

### 4. Verify Installation

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Should return JSON with model list:
# {"models": [{"name": "llama3:latest", ...}]}
```

**Test in Python:**
```python
import requests

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'llama3',
        'prompt': 'Hello! Respond with just "OK" if you are working.',
        'stream': False
    }
)

print(response.json()['response'])
# Should print: "OK" or similar
```

---

## Configuration

### Update `.env` File

Ensure these settings in `.env`:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Set to false once Ollama is working
MOCK_DATA_ENABLED=false
```

### Test LLM Client

```bash
cd /c/Users/A/Agentic-Hiring-System-Prototype

python << 'EOF'
from python.utils.llm_client import OllamaLLM

llm = OllamaLLM()
response = llm.generate("What is 2+2? Answer with just the number.")
print(f"LLM Response: {response}")
EOF
```

**Expected output:**
```
Sending request to Ollama: llama3
LLM Response: 4
```

---

## Performance Optimization

### GPU Acceleration (Recommended)

Ollama automatically uses GPU if available:

**NVIDIA GPU (CUDA):**
- Ollama detects CUDA automatically
- Ensure NVIDIA drivers are up to date
- Check GPU usage: `nvidia-smi`

**AMD GPU (ROCm):**
- Set environment variable:
  ```bash
  export OLLAMA_GPU=amd
  ```

**Apple Silicon (M1/M2/M3):**
- Metal acceleration enabled by default
- No configuration needed

### CPU-Only Mode

If no GPU available:
```bash
# Ollama will use CPU automatically
# Performance: ~10-20 tokens/sec on modern CPUs
```

### Memory Requirements

| Model | RAM Required | Recommended |
|-------|--------------|-------------|
| llama3:8b | 8 GB | 16 GB |
| llama3:70b | 40 GB | 64 GB |

### Reduce Memory Usage

```bash
# Use quantized model (lower quality, less memory)
ollama pull llama3:8b-q4_0

# Update .env:
OLLAMA_MODEL=llama3:8b-q4_0
```

---

## Agentic AI Features Enabled

Once Ollama is running, these agentic decision points become active:

### Phase 1: Candidate Sourcing
**`CandidateScorer._determine_weights()`**
- AI analyzes job posting context
- Dynamically adjusts scoring weights
- Example: DevOps role → prioritize experience over education

**Before (rule-based):**
```
skills: 40%, experience: 30%, location: 15%, education: 15%
```

**After (AI-powered):**
```
AI Decision: For Senior Python Developer (remote):
  skills: 45%, experience: 35%, location: 5%, education: 15%
  Reasoning: Remote role reduces location importance; senior level 
  requires strong experience and technical skills
```

### Phase 3: Interview Questions
**`InterviewQuestionGenerator._decide_question_distribution()`**
- AI determines optimal question mix
- Adapts to candidate experience level
- Balances technical vs behavioral questions

**Before (rule-based):**
```
Senior: 2 tech, 2 problem-solving, 1 coding, 3 system design, 1 behavioral, 1 situational
```

**After (AI-powered):**
```
AI Decision: For Senior Python Developer with 5 years experience:
  technical: 3, problem_solving: 2, coding: 1, system_design: 2, 
  behavioral: 1, situational: 1
  Reasoning: Candidate has mid-level experience; focus on technical depth 
  and problem-solving rather than heavy system design
```

### Phase 5: Evaluation
**`FeedbackAnalyzer._generate_ai_recommendation()`**
- Holistic candidate evaluation
- Identifies patterns across interview responses
- Provides nuanced hire/reject reasoning

**Before (rule-based):**
```
Average score: 8.0 → HIRE
```

**After (AI-powered):**
```
AI Recommendation: HIRE with RESERVATIONS (85% confidence)
  Strengths: Excellent technical skills, strong problem-solving
  Concerns: Limited system design experience for senior role; recommend 
  mentorship pairing
  Justification: Candidate demonstrates high potential; technical 
  foundation is solid but needs architectural guidance
```

---

## Troubleshooting

### Issue: "Cannot connect to Ollama"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If no response:
# Windows: Restart Ollama from Start Menu
# Linux: ollama serve
# macOS: Restart Ollama app
```

### Issue: "Model not found"

```bash
# List installed models
ollama list

# If llama3 missing:
ollama pull llama3
```

### Issue: Slow inference (>30 seconds per request)

**Solutions:**
1. Use smaller model: `ollama pull llama3:8b-q4_0`
2. Reduce context length in prompts
3. Enable GPU acceleration
4. Close other applications consuming RAM/GPU

### Issue: Out of memory errors

```bash
# Use smaller quantized model
ollama pull llama3:8b-q4_0

# Or increase swap space (Linux):
sudo dd if=/dev/zero of=/swapfile bs=1G count=8
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Alternative: Use Different LLM

The system supports any Ollama-compatible model:

```bash
# Try Mistral (faster, good for structured output)
ollama pull mistral

# Update .env:
OLLAMA_MODEL=mistral
```

```bash
# Try Llama3.1 (latest version)
ollama pull llama3.1

# Update .env:
OLLAMA_MODEL=llama3.1
```

```bash
# Try CodeLlama (optimized for code generation)
ollama pull codellama

# Update .env:
OLLAMA_MODEL=codellama
```

---

## Testing After Setup

Run the test suite:

```bash
cd /c/Users/A/Agentic-Hiring-System-Prototype

# Test Phase 1 with AI
python << 'EOF'
from python.sourcing.job_parser import create_sample_jobs, JobParser
from python.sourcing.candidate_generator import CandidateGenerator
from python.sourcing.candidate_scorer import CandidateRanker

job = JobParser().parse(create_sample_jobs()[0])
candidates = CandidateGenerator().generate_for_job(job, count=10)
ranker = CandidateRanker(use_ai_weights=True)  # AI enabled!

scored = ranker.rank_candidates(candidates, job)
print(f"Top candidate: {scored[0]['full_name']} - {scored[0]['match_score']:.1f}")
EOF
```

**Look for:**
```
DECISION: AI determined adaptive weights for Senior Python Developer
  skills: 45%, experience: 35%, ...
```

---

## Next Steps

After Ollama is working:

1. ✅ Re-run tests with AI enabled (remove `use_ai_weights=False`)
2. ✅ Verify agentic decision-making logs
3. ✅ Set up PostgreSQL database
4. ✅ Implement Phase 2: Candidate Onboarding
5. ✅ Test end-to-end pipeline

---

## Support

**Ollama Documentation:** https://github.com/ollama/ollama  
**Llama3 Model Card:** https://ollama.ai/library/llama3  
**Community:** https://discord.gg/ollama

**Project Issues:** Open an issue in this repository
