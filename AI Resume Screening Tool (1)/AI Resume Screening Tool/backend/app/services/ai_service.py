"""
Robust AI Service Layer with retry, fallback, and caching.
Primary: Gemini (google.genai)
Secondary: OpenAI (optional fallback)
"""

import os
import json
import hashlib
import logging
import time
import re
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import Gemini SDK (supports both new and old packages)
try:
    from google import genai
    GEMINI_AVAILABLE = True
    GEMINI_SDK_VERSION = "genai"
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_SDK_VERSION = "generativeai"
    except ImportError:
        GEMINI_AVAILABLE = False
        GEMINI_SDK_VERSION = None

# Try to import OpenAI SDK
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIServiceCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, resume_text: str, job_title: str) -> str:
        """Generate MD5 hash key from resume and job title"""
        combined = f"{resume_text[:500]}|{job_title}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, resume_text: str, job_title: str) -> Optional[Dict]:
        """Get cached result if exists and not expired"""
        key = self._generate_key(resume_text, job_title)
        
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires']:
                logger.info(f"Cache HIT for {key[:8]}...")
                return entry['data']
            else:
                logger.info(f"Cache EXPIRED for {key[:8]}...")
                del self.cache[key]
        
        return None
    
    def set(self, resume_text: str, job_title: str, data: Dict) -> None:
        """Store result in cache with TTL"""
        key = self._generate_key(resume_text, job_title)
        self.cache[key] = {
            'data': data,
            'expires': datetime.now() + timedelta(seconds=self.ttl),
            'created': datetime.now()
        }
        logger.info(f"Cached result for {key[:8]}...")
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        logger.info("Cache cleared")


class GeminiProvider:
    """Gemini API provider - supports both google.genai and google.generativeai SDKs"""
    
    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise Exception(
                "google-genai or google-generativeai not installed. "
                "Run: pip install google-genai"
            )
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not set in environment variables")
        
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        
        if GEMINI_SDK_VERSION == "genai":
            self.client = genai.Client(api_key=api_key)
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.client = None
            self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"Initialized Gemini provider with model: {self.model_name}, SDK: {GEMINI_SDK_VERSION}")
    
    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str) -> Dict:
        """Analyze resume using Gemini"""
        prompt = self._build_prompt(
            resume_text, job_title, job_description, requirements, required_skills
        )
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
            else:
                response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
            
            raw = response.text
            result = self._parse_response(raw)
            result['ai_model'] = 'gemini'
            return result
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
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
    "skills_gap": ["<missing_skill1>"],
    "experience_years": <number or null>,
    "github_url": "<url or null>",
    "criteria_decisions": {{
        "education": {{"met": true, "reason": "<reason>"}},
        "experience": {{"met": true, "reason": "<reason>"}},
        "skills": {{"met": true, "reason": "<reason>"}}
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
    
    def _parse_response(self, raw: str) -> Dict:
        """Parse JSON response from Gemini"""
        cleaned = re.sub(r'```json|```', '', raw).strip()
        
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = {}
        
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
        }


class OpenAIProvider:
    """OpenAI API provider (optional fallback)"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY not set")
        
        if not OPENAI_AVAILABLE:
            raise Exception(
                "openai package not installed. "
                "Run: pip install openai"
            )
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        logger.info(f"Initialized OpenAI provider with model: {self.model}")
    
    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str) -> Dict:
        """Analyze resume using OpenAI"""
        prompt = self._build_prompt(
            resume_text, job_title, job_description, requirements, required_skills
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR recruiter. Analyze resumes and return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            raw = response.choices[0].message.content
            result = self._parse_response(raw)
            result['ai_model'] = 'openai'
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI error: {str(e)}")
    
    def _build_prompt(self, resume_text, job_title, job_description, requirements, required_skills):
        return f"""Analyze this resume against the job posting and return a JSON object.

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description}
REQUIRED QUALIFICATIONS: {requirements}
REQUIRED SKILLS: {required_skills}

RESUME:
{resume_text[:4000]}

Return this exact JSON structure:
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
    "skills_gap": ["<missing_skill1>"],
    "experience_years": <number or null>,
    "github_url": "<url or null>",
    "criteria_decisions": {{
        "education": {{"met": true, "reason": "<reason>"}},
        "experience": {{"met": true, "reason": "<reason>"}},
        "skills": {{"met": true, "reason": "<reason>"}}
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
    
    def _parse_response(self, raw: str) -> Dict:
        """Parse JSON response from OpenAI"""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
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
        }


class OpenRouterProvider:
    """OpenRouter API provider using OpenAI SDK with OpenRouter base URL"""
    
    def __init__(self):
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise Exception("OPENROUTER_API_KEY not set")
        
        if not OPENAI_AVAILABLE:
            raise Exception(
                "openai package not installed. "
                "Run: pip install openai"
            )
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "RecruitAI Resume Screening"
            }
        )
        self.model = os.getenv('OPENROUTER_MODEL', 'openrouter/free')
        logger.info(f"Initialized OpenRouter provider with model: {self.model}")
    
    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str) -> Dict:
        """Analyze resume using OpenRouter"""
        prompt = self._build_prompt(
            resume_text, job_title, job_description, requirements, required_skills
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR recruiter. Analyze resumes and return ONLY valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            raw = response.choices[0].message.content
            result = self._parse_response(raw)
            result['ai_model'] = 'openrouter'
            return result
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise Exception(f"OpenRouter error: {str(e)}")
    
    def _build_prompt(self, resume_text, job_title, job_description, requirements, required_skills):
        return f"""Analyze this resume against the job posting and return a JSON object.

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description}
REQUIRED QUALIFICATIONS: {requirements}
REQUIRED SKILLS: {required_skills}

RESUME:
{resume_text[:4000]}

Return this exact JSON structure:
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
    "skills_gap": ["<missing_skill1>"],
    "experience_years": <number or null>,
    "github_url": "<url or null>",
    "criteria_decisions": {{
        "education": {{"met": true, "reason": "<reason>"}},
        "experience": {{"met": true, "reason": "<reason>"}},
        "skills": {{"met": true, "reason": "<reason>"}}
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
    
    def _parse_response(self, raw: str) -> Dict:
        """Parse JSON response from OpenRouter"""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
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
        }


class MockProvider:
    """Mock provider for fallback when all APIs fail"""
    
    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str) -> Dict:
        """Generate realistic default analysis"""
        skills = self._extract_skills(resume_text, required_skills)
        experience = self._extract_experience(resume_text)
        education = self._extract_education(resume_text)
        
        skills_match = min(100, len(skills) * 25) if skills else 0
        experience_match = 60 if len(experience) > 0 else 20
        education_match = 80 if len(education) > 0 else 30
        match_score = round((skills_match + experience_match + education_match) / 3)
        
        logger.info(f"Mock analysis: match_score={match_score}, skills={len(skills)}")
        
        return {
            'match_score': match_score,
            'resume_rating': 6 if match_score > 60 else 5,
            'skills_match': skills_match,
            'experience_match': experience_match,
            'education_match': education_match,
            'category': self._determine_category(match_score, skills_match),
            'summary': f"Resume shows alignment with {job_title} position.",
            'strengths': [f"Has {len(skills)} relevant skills", "Professional experience shown", "Educational background present"][:3],
            'weaknesses': [s for s in ["Limited technical details", "Could expand experience section"] if match_score < 70],
            'recommendations': ["Add specific achievements", "Include measurable results", "Detail technical projects"],
            'overall_assessment': f"Candidate with {len(experience)} roles and {len(education)} education entries.",
            'skills_found': skills,
            'skills_gap': [],
            'experience_years': len(experience) if experience else None,
            'github_url': None,
            'criteria_decisions': {
                'education': {'met': len(education) > 0, 'reason': 'Education found' if education else 'None found'},
                'experience': {'met': len(experience) > 0, 'reason': f'{len(experience)} roles found' if experience else 'None found'},
                'skills': {'met': skills_match > 50, 'reason': f'{len(skills)} skills identified'}
            },
            'fact_check': {
                'verified_claims': ['Dates and roles extracted'],
                'unverified_claims': [],
                'flags': []
            },
            'bias_indicators': {
                'gender_bias': False,
                'age_bias': False,
                'location_bias': False,
                'education_bias': False,
                'bias_score': 10,
                'details': []
            },
            'ai_model': 'mock'
        }
    
    def _extract_skills(self, text: str, required_skills: str = '') -> list:
        """Extract skills from resume text"""
        common = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'flask', 'django', 'fastapi', 'sql', 'mongodb', 'postgresql',
            'redis', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'html',
            'css', 'tailwind', 'graphql', 'rest api', 'machine learning', 'deep learning',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'data analysis', 'nlp'
        ]
        tl = text.lower()
        return [s for s in common if s in tl]
    
    def _extract_experience(self, text: str) -> list:
        """Extract work experience from resume"""
        indicators = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'lead']
        experience = []
        for line in text.split('\n'):
            if any(ind in line.lower() for ind in indicators) and len(line.strip()) > 10:
                experience.append({'position': line.strip()[:100]})
                if len(experience) >= 5:
                    break
        return experience
    
    def _extract_education(self, text: str) -> list:
        """Extract education from resume"""
        degrees = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba']
        education = []
        for line in text.split('\n'):
            if any(d in line.lower() for d in degrees):
                education.append({'degree': line.strip()[:100]})
        return education
    
    def _determine_category(self, match_score: int, skills_match: int) -> str:
        """Determine candidate category"""
        if match_score >= 75 and skills_match >= 50:
            return 'Highly Qualified'
        elif match_score >= 50:
            return 'Qualified'
        else:
            return 'Not a Fit'


class AIService:
    """Main AI Service with retry, fallback, and caching"""
    
    def __init__(self, max_retries: int = 1):
        self.max_retries = max_retries
        self.cache = AIServiceCache(ttl_seconds=3600)
        self.gemini_provider = None
        self.openai_provider = None
        self.openrouter_provider = None
        self.mock_provider = MockProvider()
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers"""
        # Initialize Gemini (primary)
        try:
            if GEMINI_AVAILABLE:
                self.gemini_provider = GeminiProvider()
                logger.info("✓ Gemini provider initialized")
            else:
                logger.warning("✗ Gemini SDK not available")
        except Exception as e:
            logger.warning(f"✗ Gemini initialization failed: {str(e)}")
        
        # Initialize OpenAI (secondary, optional)
        try:
            if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                self.openai_provider = OpenAIProvider()
                logger.info("✓ OpenAI provider initialized")
            else:
                logger.info("✗ OpenAI not configured")
        except Exception as e:
            logger.warning(f"✗ OpenAI initialization failed: {str(e)}")
        
        # Initialize OpenRouter (optional)
        try:
            if OPENAI_AVAILABLE and os.getenv('OPENROUTER_API_KEY'):
                self.openrouter_provider = OpenRouterProvider()
                logger.info("✓ OpenRouter provider initialized")
            else:
                logger.info("✗ OpenRouter not configured")
        except Exception as e:
            logger.warning(f"✗ OpenRouter initialization failed: {str(e)}")
    
    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str, ai_model: str = None) -> Tuple[Dict, bool]:
        """
        Analyze resume with retry, fallback, and caching.
        Returns: (result_dict, success_bool)
        """
        # Check cache first
        cached = self.cache.get(resume_text, job_title)
        if cached:
            cached['cached'] = True
            return cached, True
        
        providers = []
        
        # Build provider list in order of preference
        ai_model_env = ai_model or os.getenv('AI_MODEL', 'gemini')
        
        # Add the preferred model first
        if ai_model_env == 'gemini' and self.gemini_provider:
            providers.append(('gemini', self.gemini_provider))
        elif ai_model_env == 'openai' and self.openai_provider:
            providers.append(('openai', self.openai_provider))
        elif ai_model_env == 'openrouter' and self.openrouter_provider:
            providers.append(('openrouter', self.openrouter_provider))
        elif ai_model_env == 'mock':
            providers.append(('mock', self.mock_provider))
        
        # Add remaining providers in fallback order
        if self.gemini_provider and ('gemini' not in [p[0] for p in providers]):
            providers.append(('gemini', self.gemini_provider))
        if self.openai_provider and ('openai' not in [p[0] for p in providers]):
            providers.append(('openai', self.openai_provider))
        if self.openrouter_provider and ('openrouter' not in [p[0] for p in providers]):
            providers.append(('openrouter', self.openrouter_provider))
        
        # Always end with mock analyzer
        providers.append(('mock', self.mock_provider))
        
        last_error = None
        
        for provider_name, provider in providers:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"[{provider_name}] Attempt {attempt}/{self.max_retries}")
                    
                    result = provider.analyze(
                        resume_text, job_title, job_description,
                        requirements, required_skills
                    )
                    
                    # Cache successful results
                    if provider_name != 'mock':
                        self.cache.set(resume_text, job_title, result)
                    
                    logger.info(f"[{provider_name}] Success ✓")
                    result['cached'] = False
                    return result, True
                    
                except Exception as e:
                    last_error = str(e)
                    logger.warning(
                        f"[{provider_name}] Attempt {attempt} failed: {last_error}"
                    )
                    
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                        logger.info(f"[{provider_name}] Retrying in {wait_time}s...")
                        time.sleep(wait_time)
        
        # If all providers fail, return structured error
        error_response = {
            'success': False,
            'message': 'AI service temporarily unavailable. Please try again later.',
            'error': last_error,
            'cached': False,
            'ai_model': 'error'
        }
        
        logger.error(f"All providers failed. Last error: {last_error}")
        return error_response, False
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()


# Global instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get or create global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService(max_retries=1)
    return _ai_service
