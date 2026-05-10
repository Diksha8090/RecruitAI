from openai import OpenAI
import os
import json
import re
from typing import Dict, List


class OpenRouterAnalyzer:
    """Analyze resume using OpenRouter free models (Llama, Gemma, etc.)"""

    def __init__(self):
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise Exception(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable. "
                "Get your key from: https://openrouter.ai/keys"
            )
        # OpenRouter requires HTTP-Referer header for authentication
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
                "X-Title": "RecruitAI Resume Screening"
            }
        )
        self.model = os.getenv('OPENROUTER_MODEL', 'openrouter/free')

    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str) -> Dict:
        prompt = self._build_prompt(resume_text, job_title, job_description, requirements, required_skills)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR recruiter. Analyze resumes and return ONLY valid JSON. No markdown, no explanation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500,
            )
            raw = response.choices[0].message.content
            return self._parse(raw, resume_text)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "auth" in error_msg.lower():
                error_msg = (
                    f"OpenRouter authentication failed: {error_msg}. "
                    "Check that OPENROUTER_API_KEY is set correctly at: https://openrouter.ai/keys"
                )
            raise Exception(f"OpenRouter error: {error_msg}")

    def _build_prompt(self, resume_text, job_title, job_description, requirements, required_skills):
        return f"""Analyze this resume against the job posting and return ONLY a valid JSON object.

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

    def _parse(self, raw: str, resume_text: str) -> Dict:
        cleaned = re.sub(r'```json|```', '', raw).strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            data = json.loads(match.group()) if match else {}

        skills = self._extract_skills(resume_text)
        experience = self._extract_experience(resume_text)
        education = self._extract_education(resume_text)

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
            'skills_found': data.get('skills_found', skills),
            'skills_gap': data.get('skills_gap', []),
            'experience_years': data.get('experience_years'),
            'github_url': data.get('github_url'),
            'criteria_decisions': data.get('criteria_decisions', {}),
            'fact_check': data.get('fact_check', {}),
            'bias_indicators': data.get('bias_indicators', {}),
            'skills': skills,
            'experience': experience,
            'education': education,
            'ai_model': 'openrouter'
        }

    def _extract_skills(self, text: str) -> List[str]:
        common = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'flask', 'django', 'fastapi', 'sql', 'mongodb', 'postgresql',
            'redis', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'html',
            'css', 'tailwind', 'graphql', 'rest api', 'machine learning', 'deep learning',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'data analysis', 'nlp',
            'project management', 'agile', 'scrum', 'figma', 'linux', 'ci/cd'
        ]
        tl = text.lower()
        return [s for s in common if s in tl]

    def _extract_experience(self, text: str) -> List[Dict]:
        indicators = ['engineer', 'developer', 'manager', 'analyst', 'specialist',
                      'consultant', 'architect', 'lead', 'intern']
        experience = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(ind in line.lower() for ind in indicators) and len(line.strip()) > 10:
                desc = lines[i + 1].strip() if i + 1 < len(lines) else ''
                experience.append({'position': line.strip(), 'description': desc})
                if len(experience) >= 5:
                    break
        return experience

    def _extract_education(self, text: str) -> List[Dict]:
        degrees = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'b.e', 'm.e',
                   'mba', 'bca', 'mca', 'b.sc', 'm.sc']
        education = []
        for line in text.split('\n'):
            if any(d in line.lower() for d in degrees):
                education.append({'degree': line.strip()})
        return education
