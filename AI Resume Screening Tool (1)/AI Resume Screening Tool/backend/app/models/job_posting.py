from app import db
from datetime import datetime

class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)  # comma-separated or JSON
    skills = db.Column(db.Text)  # comma-separated
    experience_required = db.Column(db.String(100))
    location = db.Column(db.String(255))
    salary_range = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('ResumeAnalysis', backref='job_posting', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'skills': self.skills,
            'experience_required': self.experience_required,
            'location': self.location,
            'salary_range': self.salary_range,
            'created_at': self.created_at.isoformat()
        }
