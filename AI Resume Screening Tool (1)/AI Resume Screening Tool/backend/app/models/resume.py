from app import db
from datetime import datetime

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    candidate_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10))  # pdf, docx, doc
    file_size = db.Column(db.Integer)  # in bytes
    raw_text = db.Column(db.Text)  # extracted text from resume
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('ResumeAnalysis', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_name': self.candidate_name,
            'email': self.email,
            'phone': self.phone,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'analyses': [analysis.to_dict() for analysis in self.analyses]
        }
