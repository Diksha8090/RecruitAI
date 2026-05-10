# AI Resume Screening Tool - Backend

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
Update `.env` with your database URL:
```
DATABASE_URL=postgresql://username:password@localhost:5432/resume_screening
```

### 4. Setup OpenAI API
Get your API key from https://platform.openai.com/account/api-keys and add to `.env`:
```
OPENAI_API_KEY=your-api-key-here
```

### 5. Run the Application
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Resumes
- `GET /api/resumes` - Get all resumes
- `POST /api/resumes` - Upload resume
- `GET /api/resumes/<id>` - Get resume details
- `DELETE /api/resumes/<id>` - Delete resume

### Job Postings
- `GET /api/job-postings` - Get all job postings
- `POST /api/job-postings` - Create job posting
- `GET /api/job-postings/<id>` - Get job posting
- `PUT /api/job-postings/<id>` - Update job posting
- `DELETE /api/job-postings/<id>` - Delete job posting

### Analysis
- `POST /api/analysis/analyze` - Analyze resume
- `GET /api/analysis/<id>` - Get analysis
- `POST /api/analysis/bulk-analyze` - Analyze multiple resumes

## Project Structure
```
backend/
├── app/
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── resume_routes.py
│   │   ├── analysis_routes.py
│   │   └── job_posting_routes.py
│   ├── models/
│   │   ├── user.py
│   │   ├── resume.py
│   │   ├── job_posting.py
│   │   └── analysis.py
│   ├── services/
│   │   ├── resume_parser.py
│   │   └── resume_analyzer.py
│   └── __init__.py
├── config.py
├── requirements.txt
├── run.py
└── .env
```
