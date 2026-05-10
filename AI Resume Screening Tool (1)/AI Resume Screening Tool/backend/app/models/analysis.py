from app import db
from datetime import datetime
import json

class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analyses'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'))

    # Scores
    match_score = db.Column(db.Float)
    resume_rating = db.Column(db.Float)
    skills_match = db.Column(db.Float)
    experience_match = db.Column(db.Float)
    education_match = db.Column(db.Float)
    github_score = db.Column(db.Float)
    final_fit_score = db.Column(db.Float)

    # Category
    category = db.Column(db.String(50))  # Highly Qualified / Qualified / Not a Fit

    # AI Analysis
    summary = db.Column(db.Text)
    strengths = db.Column(db.Text)       # JSON list
    weaknesses = db.Column(db.Text)      # JSON list
    recommendations = db.Column(db.Text) # JSON list
    overall_assessment = db.Column(db.Text)
    criteria_decisions = db.Column(db.Text)  # JSON
    fact_check = db.Column(db.Text)          # JSON

    # Extracted
    skills = db.Column(db.Text)       # JSON list
    skills_found = db.Column(db.Text) # JSON list
    skills_gap = db.Column(db.Text)   # JSON list
    experience = db.Column(db.Text)   # JSON list
    education = db.Column(db.Text)    # JSON list
    experience_years = db.Column(db.Float)

    # GitHub
    github_url = db.Column(db.String(255))
    github_data = db.Column(db.Text)   # JSON

    # Bias
    bias_data = db.Column(db.Text)     # JSON
    blind_resume = db.Column(db.Text)

    # Meta
    ai_model = db.Column(db.String(50), default='openai')
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def _load(self, val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return val

    def _load_dict(self, val):
        if not val:
            return {}
        try:
            return json.loads(val)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_posting_id': self.job_posting_id,
            'match_score': self.match_score,
            'resume_rating': self.resume_rating,
            'skills_match': self.skills_match,
            'experience_match': self.experience_match,
            'education_match': self.education_match,
            'github_score': self.github_score,
            'final_fit_score': self.final_fit_score,
            'category': self.category,
            'summary': self.summary,
            'strengths': self._load(self.strengths),
            'weaknesses': self._load(self.weaknesses),
            'recommendations': self._load(self.recommendations),
            'overall_assessment': self.overall_assessment,
            'criteria_decisions': self._load_dict(self.criteria_decisions),
            'fact_check': self._load_dict(self.fact_check),
            'skills': self._load(self.skills),
            'skills_found': self._load(self.skills_found),
            'skills_gap': self._load(self.skills_gap),
            'experience': self._load(self.experience),
            'education': self._load(self.education),
            'experience_years': self.experience_years,
            'github_url': self.github_url,
            'github_data': self._load_dict(self.github_data),
            'bias_data': self._load_dict(self.bias_data),
            'ai_model': self.ai_model,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
