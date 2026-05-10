import re
from typing import Dict, List

MALE_INDICATORS = ['mr.', 'sir', 'he/him', 'his ', 'himself']
FEMALE_INDICATORS = ['ms.', 'mrs.', 'miss', 'she/her', 'her ', 'herself']
AGE_PATTERNS = [r'\b(19[5-9]\d|200[0-5])\b', r'\b\d{2}\s*years?\s*old\b', r'dob\s*:', r'date of birth']
LOCATION_INDICATORS = ['village', 'rural', 'tier-3', 'tier 3', 'small town']
ELITE_SCHOOLS = ['iit', 'iim', 'mit', 'harvard', 'stanford', 'oxford', 'cambridge']
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'(\+?\d[\d\s\-().]{7,}\d)',
    'address': r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|blvd|nagar|colony|sector)',
    'name_line': r'^[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?$',
}

class BiasDetector:

    def analyze(self, resume_text: str) -> Dict:
        text_lower = resume_text.lower()
        results = {
            'gender_bias': self._check_gender(text_lower),
            'age_bias': self._check_age(text_lower),
            'location_bias': self._check_location(text_lower),
            'education_bias': self._check_education(text_lower),
        }
        flagged = [k for k, v in results.items() if v['detected']]
        bias_score = len(flagged) * 25
        recommendations = self._recommendations(results)
        return {
            'bias_detected': len(flagged) > 0,
            'bias_score': bias_score,
            'categories': results,
            'flagged_categories': flagged,
            'recommendations': recommendations,
            'overall_risk': 'High' if bias_score >= 50 else 'Medium' if bias_score >= 25 else 'Low'
        }

    def create_blind_resume(self, resume_text: str) -> str:
        blind = resume_text
        blind = re.sub(PII_PATTERNS['email'], '[EMAIL REDACTED]', blind)
        blind = re.sub(PII_PATTERNS['phone'], '[PHONE REDACTED]', blind, flags=re.IGNORECASE)
        blind = re.sub(PII_PATTERNS['address'], '[ADDRESS REDACTED]', blind, flags=re.IGNORECASE)
        for ind in MALE_INDICATORS + FEMALE_INDICATORS:
            blind = re.sub(re.escape(ind), '[PRONOUN REDACTED]', blind, flags=re.IGNORECASE)
        blind = re.sub(r'\b(19[5-9]\d|200[0-5])\b', '[YEAR REDACTED]', blind)
        lines = blind.split('\n')
        if lines and re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', lines[0].strip()):
            lines[0] = 'CANDIDATE'
        return '\n'.join(lines)

    def _check_gender(self, text: str) -> Dict:
        found = [ind for ind in MALE_INDICATORS + FEMALE_INDICATORS if ind in text]
        return {'detected': bool(found), 'indicators': found, 'description': 'Gender identifiers found in resume'}

    def _check_age(self, text: str) -> Dict:
        found = [p for p in AGE_PATTERNS if re.search(p, text, re.IGNORECASE)]
        return {'detected': bool(found), 'indicators': found, 'description': 'Age/DOB information found'}

    def _check_location(self, text: str) -> Dict:
        found = [ind for ind in LOCATION_INDICATORS if ind in text]
        return {'detected': bool(found), 'indicators': found, 'description': 'Location bias indicators found'}

    def _check_education(self, text: str) -> Dict:
        found = [s for s in ELITE_SCHOOLS if s in text]
        return {
            'detected': bool(found),
            'indicators': found,
            'description': 'Elite institution names may introduce education prestige bias'
        }

    def _recommendations(self, results: Dict) -> List[str]:
        recs = []
        if results['gender_bias']['detected']:
            recs.append('Remove gender pronouns and titles (Mr./Ms.) for blind screening')
        if results['age_bias']['detected']:
            recs.append('Remove date of birth and graduation years to prevent age bias')
        if results['location_bias']['detected']:
            recs.append('Focus evaluation on skills and experience rather than candidate location')
        if results['education_bias']['detected']:
            recs.append('Evaluate candidates based on skills demonstrated, not institution prestige')
        if not recs:
            recs.append('Resume appears relatively bias-free. Continue with standard evaluation.')
        return recs
