from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app import db
from app.models import ResumeAnalysis, Resume, JobPosting
from app.services.ai_service import get_ai_service
from app.services.github_analyzer import GitHubAnalyzer
from app.services.bias_detector import BiasDetector
from app.routes.auth_routes import token_required
import json
import os
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')


def _run_analysis(resume, job_posting, ai_model='mock', use_blind=False):
    resume_text = resume.raw_text or ''
    if use_blind:
        bd = BiasDetector()
        resume_text = bd.create_blind_resume(resume_text)

    ai_service = get_ai_service()
    result, success = ai_service.analyze(
        resume_text,
        job_posting.title,
        job_posting.description or '',
        job_posting.requirements or '',
        job_posting.skills or '',
        ai_model
    )

    # GitHub analysis
    github_url = result.get('github_url')
    github_data = {}
    github_score = 0
    if not github_url:
        gh = GitHubAnalyzer()
        github_url = gh.extract_github_url(resume.raw_text or '')
    if github_url:
        gh = GitHubAnalyzer()
        github_data = gh.analyze(github_url)
        github_score = github_data.get('github_score', 0)

    # Bias analysis
    bd = BiasDetector()
    bias_data = bd.analyze(resume.raw_text or '')
    blind_resume = resume_text if use_blind else None

    final_fit = round(result['match_score'] * 0.6 + github_score * 0.4, 1)

    return result, github_url, github_data, github_score, bias_data, blind_resume, final_fit


def _save_analysis(analysis, result, github_url, github_data, github_score, bias_data, blind_resume, final_fit):
    analysis.match_score = result['match_score']
    analysis.resume_rating = result.get('resume_rating', 5)
    analysis.skills_match = result['skills_match']
    analysis.experience_match = result['experience_match']
    analysis.education_match = result['education_match']
    analysis.github_score = github_score
    analysis.final_fit_score = final_fit
    analysis.category = result.get('category', 'Qualified')
    analysis.summary = result.get('summary', '')
    analysis.strengths = json.dumps(result.get('strengths', []))
    analysis.weaknesses = json.dumps(result.get('weaknesses', []))
    analysis.recommendations = json.dumps(result.get('recommendations', []))
    analysis.overall_assessment = result.get('overall_assessment', '')
    analysis.criteria_decisions = json.dumps(result.get('criteria_decisions', {}))
    analysis.fact_check = json.dumps(result.get('fact_check', {}))
    analysis.skills = json.dumps(result.get('skills', []))
    analysis.skills_found = json.dumps(result.get('skills_found', []))
    analysis.skills_gap = json.dumps(result.get('skills_gap', []))
    analysis.experience = json.dumps(result.get('experience', []))
    analysis.education = json.dumps(result.get('education', []))
    analysis.experience_years = result.get('experience_years')
    analysis.github_url = github_url
    analysis.github_data = json.dumps(github_data)
    analysis.bias_data = json.dumps(bias_data)
    analysis.blind_resume = blind_resume
    analysis.ai_model = result.get('ai_model', 'openrouter')
    analysis.status = 'completed'


class AnalyzeResume(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json(silent=True) or {}
        if not data.get('resume_id') or not data.get('job_posting_id'):
            return {'message': 'Missing resume_id or job_posting_id'}, 400

        resume = Resume.query.filter_by(id=data['resume_id'], user_id=current_user.id).first()
        job_posting = JobPosting.query.filter_by(id=data['job_posting_id'], user_id=current_user.id).first()

        if not resume:
            return {'message': 'Resume not found'}, 404
        if not job_posting:
            return {'message': 'Job posting not found'}, 404

        ai_model = data.get('ai_model', os.getenv('AI_MODEL', 'mock'))
        use_blind = data.get('blind_mode', False)

        try:
            existing = ResumeAnalysis.query.filter_by(
                resume_id=resume.id, job_posting_id=job_posting.id
            ).first()

            if existing and existing.status == 'completed' and not data.get('force_reanalyze'):
                return {'analysis': existing.to_dict()}, 200

            result, github_url, github_data, github_score, bias_data, blind_resume, final_fit = \
                _run_analysis(resume, job_posting, ai_model, use_blind)

            analysis = existing or ResumeAnalysis(resume_id=resume.id, job_posting_id=job_posting.id)
            _save_analysis(analysis, result, github_url, github_data, github_score, bias_data, blind_resume, final_fit)

            if not existing:
                db.session.add(analysis)
            db.session.commit()

            return {'message': 'Analysis completed', 'analysis': analysis.to_dict()}, 201

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            logger.error(f"Analysis error: {error_msg}")
            if 'quota' in error_msg.lower() or '429' in error_msg:
                return {'message': 'API quota exceeded. Try again later.', 'error': 'quota_exceeded'}, 429
            return {'message': f'Analysis error: {error_msg}', 'error': 'analysis_failed'}, 500


class BulkAnalyze(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json(silent=True) or {}
        if not data.get('resume_ids') or not data.get('job_posting_id'):
            return {'message': 'Missing resume_ids or job_posting_id'}, 400

        job_posting = JobPosting.query.filter_by(id=data['job_posting_id'], user_id=current_user.id).first()
        if not job_posting:
            return {'message': 'Job posting not found'}, 404

        ai_model = data.get('ai_model', os.getenv('AI_MODEL', 'mock'))
        use_blind = data.get('blind_mode', False)
        results = []

        for resume_id in data['resume_ids']:
            resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
            if not resume:
                results.append({'resume_id': resume_id, 'error': 'Resume not found'})
                continue
            try:
                result, github_url, github_data, github_score, bias_data, blind_resume, final_fit = \
                    _run_analysis(resume, job_posting, ai_model, use_blind)

                analysis = ResumeAnalysis(resume_id=resume.id, job_posting_id=job_posting.id)
                _save_analysis(analysis, result, github_url, github_data, github_score, bias_data, blind_resume, final_fit)
                db.session.add(analysis)
                db.session.commit()
                results.append({'resume_id': resume_id, 'analysis': analysis.to_dict()})
            except Exception as e:
                db.session.rollback()
                results.append({'resume_id': resume_id, 'error': str(e)})

        return {'results': results}, 200


class AnalysisDetail(Resource):
    @token_required
    def get(self, current_user, analysis_id):
        analysis = ResumeAnalysis.query.get(analysis_id)
        if not analysis or analysis.resume.user_id != current_user.id:
            return {'message': 'Analysis not found'}, 404
        return {'analysis': analysis.to_dict()}, 200


class BiasAnalysis(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json(silent=True) or {}
        resume = Resume.query.filter_by(id=data.get('resume_id'), user_id=current_user.id).first()
        if not resume:
            return {'message': 'Resume not found'}, 404
        bd = BiasDetector()
        result = bd.analyze(resume.raw_text or '')
        blind = bd.create_blind_resume(resume.raw_text or '')
        return {'bias_analysis': result, 'blind_resume_preview': blind[:500]}, 200


api = Api(bp)
api.add_resource(AnalyzeResume, '/analyze')
api.add_resource(BulkAnalyze, '/bulk-analyze')
api.add_resource(AnalysisDetail, '/<int:analysis_id>')
api.add_resource(BiasAnalysis, '/bias')
