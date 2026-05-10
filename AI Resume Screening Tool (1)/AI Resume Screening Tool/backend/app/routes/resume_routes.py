from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Resume, ResumeAnalysis, JobPosting
from app.services.resume_parser import ResumeParser
from app.services.resume_analyzer import ResumeAnalyzer
from app.services.gemini_analyzer import GeminiAnalyzer
from app.routes.auth_routes import token_required

bp = Blueprint('resume', __name__, url_prefix='/api/resumes')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'doc'}

class ResumesCollection(Resource):
    @token_required
    def get(self, current_user):
        """Get all resumes for current user"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = Resume.query.filter_by(user_id=current_user.id)\
                                  .paginate(page=page, per_page=per_page)
        
        return {
            'resumes': [resume.to_dict() for resume in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }, 200
    
    @token_required
    def post(self, current_user):
        """Upload a new resume"""
        if 'file' not in request.files:
            return {'message': 'No file provided'}, 400
        
        file = request.files['file']
        
        if file.filename == '':
            return {'message': 'No file selected'}, 400
        
        if not allowed_file(file.filename):
            return {'message': 'Invalid file type. Allowed: pdf, docx, doc'}, 400
        
        try:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads', str(current_user.id))
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Check file size
            if file_size > current_app.config['MAX_FILE_SIZE']:
                os.remove(file_path)
                return {'message': 'File too large'}, 413
            
            # Extract text from resume
            parser = ResumeParser()
            raw_text = parser.extract_text(file_path)
            
            # Extract candidate info
            candidate_info = parser.extract_candidate_info(raw_text)
            
            # Create resume record
            resume = Resume(
                user_id=current_user.id,
                candidate_name=candidate_info.get('name', 'Unknown'),
                email=candidate_info.get('email'),
                phone=candidate_info.get('phone'),
                file_path=file_path,
                file_type=file.filename.rsplit('.', 1)[1].lower(),
                file_size=file_size,
                raw_text=raw_text
            )
            
            db.session.add(resume)
            db.session.flush()  # Flush to get the ID without committing
            db.session.commit()
            
            # Build resume response
            resume_data = {
                'id': resume.id,
                'candidate_name': resume.candidate_name,
                'email': resume.email,
                'phone': resume.phone,
                'file_type': resume.file_type,
                'file_size': resume.file_size,
                'created_at': resume.created_at.isoformat() if resume.created_at else None,
                'updated_at': resume.updated_at.isoformat() if resume.updated_at else None
            }

            # Start analysis if we have a single job posting or a provided job posting id
            job_posting_id = request.form.get('job_posting_id')
            job_posting = None
            if job_posting_id:
                job_posting = JobPosting.query.filter_by(id=job_posting_id, user_id=current_user.id).first()
            else:
                postings = JobPosting.query.filter_by(user_id=current_user.id).all()
                if len(postings) == 1:
                    job_posting = postings[0]

            analysis_data = None
            if job_posting:
                try:
                    analyzer = ResumeAnalyzer()
                    analysis_result = analyzer.analyze(
                        resume.raw_text,
                        job_posting.title,
                        job_posting.description,
                        job_posting.requirements,
                        job_posting.skills
                    )
                except Exception as openai_error:
                    # Fallback to Gemini if OpenAI fails
                    error_msg = str(openai_error)
                    if 'insufficient_quota' in error_msg or '429' in error_msg:
                        print(f"⚠️ OpenAI quota exceeded, falling back to Gemini...")
                        analyzer = GeminiAnalyzer()
                        analysis_result = analyzer.analyze(
                            resume.raw_text,
                            job_posting.title,
                            job_posting.description or '',
                            job_posting.requirements or '',
                            job_posting.skills or ''
                        )
                    else:
                        raise

                analysis = ResumeAnalysis(
                    resume_id=resume.id,
                    job_posting_id=job_posting.id,
                    match_score=analysis_result['match_score'],
                    skills_match=analysis_result['skills_match'],
                    experience_match=analysis_result['experience_match'],
                    education_match=analysis_result['education_match'],
                    summary=analysis_result['summary'],
                    strengths=str(analysis_result['strengths']),
                    weaknesses=str(analysis_result['weaknesses']),
                    recommendations=str(analysis_result['recommendations']),
                    overall_assessment=analysis_result['overall_assessment'],
                    skills=str(analysis_result['skills']),
                    experience=str(analysis_result['experience']),
                    education=str(analysis_result['education']),
                    status='completed'
                )
                db.session.add(analysis)
                db.session.commit()
                analysis_data = analysis.to_dict()

            response_data = {
                'message': 'Resume uploaded successfully',
                'resume': resume_data
            }
            if analysis_data:
                response_data['analysis'] = analysis_data

            return response_data, 201
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return {'message': f'Error uploading resume: {str(e)}'}, 500

class ResumeDetail(Resource):
    @token_required
    def get(self, current_user, resume_id):
        """Get resume details"""
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            return {'message': 'Resume not found'}, 404
        
        result = resume.to_dict()
        result['raw_text'] = resume.raw_text
        
        return {'resume': result}, 200
    
    @token_required
    def delete(self, current_user, resume_id):
        """Delete a resume"""
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            return {'message': 'Resume not found'}, 404
        
        try:
            # Delete file
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
            
            db.session.delete(resume)
            db.session.commit()
            
            return {'message': 'Resume deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

api = Api(bp)
api.add_resource(ResumesCollection, '')
api.add_resource(ResumeDetail, '/<int:resume_id>')
