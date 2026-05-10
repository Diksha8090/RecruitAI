import os
import json
import re
from typing import Dict, List

try:
    from google import genai
    GEMINI_AVAILABLE = True
    GEMINI_SDK = 'google-genai'
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_SDK = 'google-generativeai'
    except ImportError:
        GEMINI_AVAILABLE = False
        GEMINI_SDK = None

class GeminiAnalyzer:
    """Analyze resume using Google Gemini"""

    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise Exception("google-genai not installed. Run: pip install google-genai")

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not set in environment variables")

        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        if GEMINI_SDK == 'google-genai':
            self.client = genai.Client(api_key=api_key)
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.client = None
            self.model = genai.GenerativeModel(self.model_name)

    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str) -> Dict:
        prompt = self._build_prompt(resume_text, job_title, job_description, requirements, required_skills)
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
            else:
                response = self.model.generate_content(prompt)
            raw = response.text
            return self._parse(raw)
        except Exception as e:
            raise Exception(f"Gemini error: {str(e)}")

    def _build_prompt(self, resume_text, job_title, job_description, requirements, required_skills):
        return f"""You are an expert HR recruiter. Analyze this resume and return ONLY a valid JSON object.

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description}
REQUIRED QUALIFICATIONS: {requirements}
REQUIRED SKILLS: {required_skills}

RESUME:
{resume_text[:4000]}

Return ONLY this JSON (no markdown, no explanation):
{{
    "match_score": <0-100>,
    "resume_rating": <0-10>,
    "skills_match": <0-100>,
    "experience_match": <0-100>,
    "education_match": <0-100>,
    "category": "<Highly Qualified|Qualified|Not a Fit>",
    "summary": "<2-3 sentence summary>",
    "strengths": ["<strength1>", "<strength2>", "<strength3>"],
    "weaknesses": ["<weakness1>", "<weakness2>"],
    "recommendations": ["<rec1>", "<rec2>"],
    "overall_assessment": "<detailed paragraph>",
    "skills_found": ["<skill1>", "<skill2>"],
    "skills_gap": ["<missing_skill1>", "<missing_skill2>"],
    "experience_years": <number or null>,
    "github_url": "<url or null>",
    "criteria_decisions": {{
        "education": {{"met": true, "reason": "<reason>"}},
        "experience": {{"met": true, "reason": "<reason>"}},
        "skills": {{"met": true, "reason": "<reason>"}},
        "leadership": {{"met": false, "reason": "<reason>"}}
    }},
    "fact_check": {{
        "verified_claims": [],
        "unverified_claims": [],
        "flags": []
    }},
    "bias_indicators": {{
        "gender_bias": false,
        "age_bias": false,
        "location_bias": false,
        "education_bias": false,
        "bias_score": 10,
        "details": []
    }}
}}"""

    def _parse(self, raw: str) -> Dict:
        cleaned = re.sub(r'```json|```', '', raw).strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            data = json.loads(match.group()) if match else {}

        return {
            'match_score': data.get('match_score', 50),
            'resume_rating': data.get('resume_rating', 5),
            'skills_match': data.get('skills_match', 0),
            'experience_match': data.get('experience_match', 0),
            'education_match': data.get('education_match', 0),
            'category': data.get('category', 'Qualified'),
            'summary': data.get('summary', ''),
            'strengths': data.get('strengths', []),
            'weaknesses': data.get('weaknesses', []),
            'recommendations': data.get('recommendations', []),
            'overall_assessment': data.get('overall_assessment', ''),
            'skills_found': data.get('skills_found', []),
            'skills_gap': data.get('skills_gap', []),
            'experience_years': data.get('experience_years'),
            'github_url': data.get('github_url'),
            'criteria_decisions': data.get('criteria_decisions', {}),
            'fact_check': data.get('fact_check', {}),
            'bias_indicators': data.get('bias_indicators', {}),
            'skills': data.get('skills_found', []),
            'experience': [],
            'education': [],
            'ai_model': 'gemini'
        }
