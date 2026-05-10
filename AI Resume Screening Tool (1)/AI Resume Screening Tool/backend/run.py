import os
from app import create_app, db
from app.models import User, Resume, JobPosting, ResumeAnalysis

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Resume': Resume,
        'JobPosting': JobPosting,
        'ResumeAnalysis': ResumeAnalysis
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
