from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app import db
from app.models import JobPosting
from app.routes.auth_routes import token_required

bp = Blueprint('job_posting', __name__, url_prefix='/api/job-postings')

class JobPostingsCollection(Resource):
    @token_required
    def get(self, current_user):
        """Get all job postings for current user"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = JobPosting.query.filter_by(user_id=current_user.id)\
                                     .paginate(page=page, per_page=per_page)
        
        return {
            'job_postings': [job.to_dict() for job in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }, 200
    
    @token_required
    def post(self, current_user):
        """Create a new job posting"""
        data = request.get_json(silent=True) or {}
        
        if not data.get('title') or not data.get('description'):
            return {'message': 'Missing required fields'}, 400
        
        try:
            job_posting = JobPosting(
                user_id=current_user.id,
                title=data['title'],
                description=data['description'],
                requirements=data.get('requirements'),
                skills=data.get('skills'),
                experience_required=data.get('experience_required'),
                location=data.get('location'),
                salary_range=data.get('salary_range')
            )
            
            db.session.add(job_posting)
            db.session.commit()
            
            return {
                'message': 'Job posting created',
                'job_posting': job_posting.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

class JobPostingDetail(Resource):
    @token_required
    def get(self, current_user, job_posting_id):
        """Get job posting details"""
        job_posting = JobPosting.query.filter_by(
            id=job_posting_id,
            user_id=current_user.id
        ).first()
        
        if not job_posting:
            return {'message': 'Job posting not found'}, 404
        
        return {'job_posting': job_posting.to_dict()}, 200
    
    @token_required
    def put(self, current_user, job_posting_id):
        """Update job posting"""
        job_posting = JobPosting.query.filter_by(
            id=job_posting_id,
            user_id=current_user.id
        ).first()
        
        if not job_posting:
            return {'message': 'Job posting not found'}, 404
        
        data = request.get_json(silent=True) or {}
        
        if 'title' in data:
            job_posting.title = data['title']
        if 'description' in data:
            job_posting.description = data['description']
        if 'requirements' in data:
            job_posting.requirements = data['requirements']
        if 'skills' in data:
            job_posting.skills = data['skills']
        if 'experience_required' in data:
            job_posting.experience_required = data['experience_required']
        if 'location' in data:
            job_posting.location = data['location']
        if 'salary_range' in data:
            job_posting.salary_range = data['salary_range']
        
        db.session.commit()
        
        return {
            'message': 'Job posting updated',
            'job_posting': job_posting.to_dict()
        }, 200
    
    @token_required
    def delete(self, current_user, job_posting_id):
        """Delete job posting"""
        job_posting = JobPosting.query.filter_by(
            id=job_posting_id,
            user_id=current_user.id
        ).first()
        
        if not job_posting:
            return {'message': 'Job posting not found'}, 404
        
        try:
            db.session.delete(job_posting)
            db.session.commit()
            
            return {'message': 'Job posting deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

api = Api(bp)
api.add_resource(JobPostingsCollection, '')
api.add_resource(JobPostingDetail, '/<int:job_posting_id>')
