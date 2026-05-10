import json
import re
from typing import Dict, List

class MockAnalyzer:
    """Mock analyzer for when all AI providers fail - returns smart default analysis"""

    def analyze(self, resume_text: str, job_title: str, job_description: str,
                requirements: str, required_skills: str) -> Dict:
        """Generate a realistic default analysis based on resume content"""
        
        skills = self._extract_skills(resume_text, required_skills)
        experience = self._extract_experience(resume_text)
        education = self._extract_education(resume_text)
        
        # Calculate basic match scores based on what was found
        skills_match = min(100, len(skills) * 25) if skills else 0
        experience_match = 60 if len(experience) > 0 else 20
        education_match = 80 if len(education) > 0 else 30
        match_score = round((skills_match + experience_match + education_match) / 3)
        
        category = self._determine_category(match_score, skills_match, experience_match)
        
        return {
            'match_score': match_score,
            'resume_rating': 6 if match_score > 60 else 5,
            'skills_match': skills_match,
            'experience_match': experience_match,
            'education_match': education_match,
            'category': category,
            'summary': f"This resume shows {'strong' if match_score > 70 else 'moderate' if match_score > 50 else 'weak'} alignment with the {job_title} position.",
            'strengths': self._get_strengths(skills, experience, education),
            'weaknesses': self._get_weaknesses(skills, required_skills),
            'recommendations': [
                f"Consider highlighting more experience in {job_title}",
                "Include specific metrics and achievements",
                "Add details on relevant projects"
            ],
            'overall_assessment': f"Candidate has {len(experience)} work experience{'s' if len(experience) != 1 else ''} and {len(education)} education record{'s' if len(education) != 1 else ''}. Skills alignment is {'good' if skills_match > 50 else 'needs improvement'}.",
            'skills_found': skills,
            'skills_gap': [s.strip() for s in (required_skills or '').split(',') if s.strip() and s.strip().lower() not in [sk.lower() for sk in skills]],
            'experience_years': len(experience) if experience else None,
            'github_url': None,
            'criteria_decisions': {
                'education': {'met': len(education) > 0, 'reason': 'Education credentials found' if education else 'No education found'},
                'experience': {'met': len(experience) > 0, 'reason': f'{len(experience)} experience entries found' if experience else 'No experience found'},
                'skills': {'met': skills_match > 50, 'reason': f'{len(skills)} relevant skills identified'},
                'leadership': {'met': any(t in resume_text.lower() for t in ['lead', 'manager', 'director', 'coordinator']), 'reason': 'Leadership keywords found' if any(t in resume_text.lower() for t in ['lead', 'manager', 'director', 'coordinator']) else 'No leadership experience'}
            },
            'fact_check': {
                'verified_claims': ['Dates and role titles extracted from resume'],
                'unverified_claims': ['Cannot verify actual job duties and achievements'],
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

    def _extract_skills(self, text: str, required_skills: str = '') -> List[str]:
        """Extract skills from resume text"""
        common = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'flask', 'django', 'fastapi', 'sql', 'mongodb', 'postgresql',
            'redis', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'html',
            'css', 'tailwind', 'graphql', 'rest api', 'machine learning', 'deep learning',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'data analysis', 'nlp',
            'project management', 'agile', 'scrum', 'figma', 'linux', 'ci/cd',
            'communication', 'leadership', 'problem solving', 'teamwork', 'analysis'
        ]
        tl = text.lower()
        found = [s for s in common if s in tl]
        
        # Add required skills if mentioned
        if required_skills:
            required = [s.strip().lower() for s in required_skills.split(',')]
            for req in required:
                if req in tl and req not in found:
                    found.append(req)
        
        return found

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience from resume"""
        indicators = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'consultant', 'architect', 'lead', 'intern', 'associate', 'senior']
        experience = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if any(ind in line.lower() for ind in indicators) and len(line.strip()) > 10:
                desc = lines[i + 1].strip() if i + 1 < len(lines) else ''
                experience.append({'position': line.strip()[:100], 'description': desc[:200]})
                if len(experience) >= 5:
                    break
        
        return experience

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education from resume"""
        degrees = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'b.e', 'm.e', 'mba', 'bca', 'mca', 'b.sc', 'm.sc', 'diploma']
        education = []
        
        for line in text.split('\n'):
            if any(d in line.lower() for d in degrees):
                education.append({'degree': line.strip()[:100]})
        
        return education

    def _determine_category(self, match_score: int, skills_match: int, experience_match: int) -> str:
        """Determine candidate category based on scores"""
        if match_score >= 75 and skills_match >= 50:
            return 'Highly Qualified'
        elif match_score >= 50:
            return 'Qualified'
        else:
            return 'Not a Fit'

    def _get_strengths(self, skills: List[str], experience: List[Dict], education: List[Dict]) -> List[str]:
        """Generate strengths based on extracted data"""
        strengths = []
        if skills:
            strengths.append(f"Possesses {len(skills)} relevant technical skills")
        if len(experience) >= 3:
            strengths.append("Strong work experience background")
        if education:
            strengths.append("Solid educational foundation")
        if not strengths:
            strengths.append("Shows professional background")
        return strengths[:3]

    def _get_weaknesses(self, skills: List[str], required_skills: str) -> List[str]:
        """Generate weaknesses based on missing skills"""
        weaknesses = []
        if not skills:
            weaknesses.append("Limited technical skills mentioned")
        if required_skills:
            required = [s.strip().lower() for s in required_skills.split(',')]
            missing = [s for s in required if s and s not in [sk.lower() for sk in skills]]
            if missing:
                weaknesses.append(f"Missing skills: {', '.join(missing[:2])}")
        if not weaknesses:
            weaknesses.append("Could provide more details on achievements")
        return weaknesses[:2]
