# RecruitAI — AI-Powered Resume Screening System

A full-stack HR tool that uses OpenAI GPT and Google Gemini to screen, rank, and analyze resumes with bias detection and GitHub profile analysis.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TailwindCSS, Framer Motion |
| Backend | Python 3.11+, Flask |
| Database | SQLite (local, no setup needed) |
| AI | OpenAI GPT-4o Mini + Google Gemini Pro |
| Auth | JWT tokens |

---

## Prerequisites — Install These First

1. **Python 3.11+** → https://python.org/downloads
2. **Node.js 18+** → https://nodejs.org
3. Git (optional)

---

## Setup Instructions

### Step 1 — Extract the ZIP

Extract the ZIP. You will get:
```
AI Resume Screening Tool/
├── backend/
├── frontend/
└── README.md
```

---

### Step 2 — Backend Setup

Open a terminal inside the project folder and run:

```bash
cd "AI Resume Screening Tool/backend"

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3 — Configure API Keys

Open `backend/.env` in any text editor and fill in:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=any-random-secret-string-here
JWT_SECRET_KEY=any-random-jwt-secret-here

DATABASE_URL=sqlite:///dev.db

OPENAI_API_KEY=sk-proj-xxxxxxxx        ← REQUIRED
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxx  ← REQUIRED
GITHUB_TOKEN=                          ← optional

ALLOWED_EXTENSIONS=pdf,docx,doc
MAX_FILE_SIZE=52428800
LLM_MODEL=gpt-4o-mini
AI_MODEL=openai
```

**Where to get API keys:**
- OpenAI → https://platform.openai.com/api-keys
- Gemini → https://aistudio.google.com/app/apikey
- GitHub Token (optional, avoids rate limits) → https://github.com/settings/tokens → Generate new token → select `public_repo`

---

### Step 4 — Start the Backend

```bash
# Inside backend/ with venv active
python run.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

**Leave this terminal open.**

---

### Step 5 — Frontend Setup

Open a **second** terminal and run:

```bash
cd "AI Resume Screening Tool/frontend"

npm install

npm start
```

Browser opens at → **http://localhost:3000**

---

## Using the App

| Step | Action |
|------|--------|
| 1 | Register an account |
| 2 | Go to **Jobs** → Create a job posting with title, description, and required skills |
| 3 | Go to **Candidates** → Drag & drop PDF/DOCX resumes |
| 4 | Select the job, choose AI model, click **Analyze All** |
| 5 | Click any candidate to see full analysis, scores, GitHub data, bias report |
| 6 | Go to **AI Chat** to ask HR questions about your candidates |

---

## Features

### Core
- Bulk resume upload (PDF + DOCX), drag & drop
- AI scoring: match score, resume rating (0–10)
- Category: Highly Qualified / Qualified / Not a Fit
- Ranked candidate list sorted by fit score

### AI Analysis (OpenAI or Gemini)
- Skills match, experience match, education match (0–100%)
- Strengths, weaknesses, recommendations
- Criteria decisions with reasons (education, experience, skills, leadership)
- Skills found vs skills gap
- Fact checking of resume claims

### GitHub Analysis
- Auto-extracts GitHub URL from resume text
- Fetches repos, stars, languages, top projects
- GitHub score contributes to Final Fit Score

### Bias Detection
- Detects gender, age, location, education bias
- Blind Screening mode removes names/emails/phones before AI analysis
- Bias risk level + recommendations

### HR AI Chat
- Ask questions about all candidates ("Who are the top 3?", "Who knows Python?")
- Per-candidate chat on individual detail page

---

## Project Structure

```
AI Resume Screening Tool/
├── backend/
│   ├── app/
│   │   ├── models/           # User, Resume, JobPosting, ResumeAnalysis
│   │   ├── routes/           # auth, resume, analysis, job_posting, chat
│   │   └── services/
│   │       ├── resume_analyzer.py   # OpenAI GPT analysis
│   │       ├── gemini_analyzer.py   # Google Gemini analysis
│   │       ├── github_analyzer.py   # GitHub profile analysis
│   │       └── bias_detector.py     # Bias detection + blind resume
│   ├── .env                  # ← PUT YOUR API KEYS HERE
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Sidebar, Topbar
│   │   ├── pages/            # Dashboard, Jobs, Candidates, CandidateDetail, Chat, Settings
│   │   ├── services/         # Axios API client
│   │   └── store/            # Zustand auth state
│   ├── tailwind.config.js
│   └── package.json
│
└── README.md
```

---

## API Reference

| Method | URL | What it does |
|--------|-----|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login, get JWT token |
| GET | `/api/resumes` | List all resumes |
| POST | `/api/resumes` | Upload resume (multipart/form-data) |
| DELETE | `/api/resumes/:id` | Delete resume |
| GET | `/api/job-postings` | List all jobs |
| POST | `/api/job-postings` | Create job |
| PUT | `/api/job-postings/:id` | Update job |
| DELETE | `/api/job-postings/:id` | Delete job |
| POST | `/api/analysis/analyze` | Analyze single resume |
| POST | `/api/analysis/bulk-analyze` | Analyze multiple resumes |
| POST | `/api/analysis/bias` | Run bias check only |
| POST | `/api/chat/hr` | HR assistant chat |
| POST | `/api/chat/candidate/:id` | Chat about a specific candidate |

---

## Troubleshooting

**`ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**`TypeError: proxies` error with OpenAI**
```bash
pip install "openai>=1.52.0" "httpx>=0.27.0,<0.28.0"
```

**Port 3000 already in use (Windows)**
```powershell
$proc = Get-NetTCPConnection -LocalPort 3000 | Select-Object -ExpandProperty OwningProcess
Stop-Process -Id $proc -Force
npm start
```

**CORS error in browser**
Make sure backend is running on port 5000 before starting the frontend.

**Analysis fails**
- Check `OPENAI_API_KEY` in `.env` is correct
- Check OpenAI account has credits at https://platform.openai.com/usage

---

## Important Notes

- Database: SQLite file auto-created at `backend/app/dev.db` — no setup needed
- Uploads stored at: `backend/app/uploads/`
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`
- Never share your `.env` file — it contains secret API keys
