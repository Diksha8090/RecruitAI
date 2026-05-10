from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.models import Resume, ResumeAnalysis, JobPosting
from app.routes.auth_routes import token_required
import os
import traceback
import logging
import warnings

try:
    from google import genai
    GEMINI_AVAILABLE = True
    GEMINI_SDK = 'google-genai'
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_SDK = 'google-generativeai'
        warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')
    except ImportError:
        GEMINI_AVAILABLE = False
        GEMINI_SDK = None

try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# --- OpenRouter client (uses OpenAI SDK, free models) ---
openrouter_client = None
if OPENAI_SDK_AVAILABLE and os.getenv('OPENROUTER_API_KEY'):
    # OpenRouter requires HTTP-Referer header for authentication
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv('OPENROUTER_API_KEY'),
        default_headers={
            "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
            "X-Title": "RecruitAI Resume Screening"
        }
    )

# --- Gemini client ---
gemini_model = None
gemini_client = None
gemini_model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
    if GEMINI_SDK == 'google-genai':
        gemini_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    else:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        gemini_model = genai.GenerativeModel(gemini_model_name)


def _chat_openrouter(system_content, messages):
    model = os.getenv('OPENROUTER_MODEL', 'openrouter/free')
    response = openrouter_client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_content}] + messages[-10:],
        temperature=0.5,
        max_tokens=800,
    )
    return response.choices[0].message.content, 'openrouter'


def _chat_gemini(system_content, messages):
    full_prompt = f"{system_content}\n\n"
    for m in messages[-10:]:
        role = "User" if m.get('role') == 'user' else "Assistant"
        full_prompt += f"{role}: {m.get('content', '')}\n"
    if gemini_client:
        response = gemini_client.models.generate_content(
            model=gemini_model_name,
            contents=full_prompt
        )
    else:
        response = gemini_model.generate_content(full_prompt)
    return response.text, 'gemini'


def _chat_local(system_content, messages):
    question = (messages[-1].get('content') if messages else '').strip()
    lines = system_content.splitlines()
    jobs = [line for line in lines if line.startswith('- ') and ':' in line]
    candidates = [line for line in lines if line.startswith('- ') and '| Score:' in line]

    if any(word in question.lower() for word in ['candidate', 'applicant', 'resume', 'score', 'rank']):
        if candidates:
            return "Remote AI is unavailable right now, so here is a local snapshot:\n" + "\n".join(candidates[:8]), 'local'
        return "Remote AI is unavailable right now, and there are no candidates loaded yet.", 'local'

    if any(word in question.lower() for word in ['job', 'position', 'opening']):
        if jobs:
            return "Remote AI is unavailable right now, so here are the open positions:\n" + "\n".join(jobs[:8]), 'local'
        return "Remote AI is unavailable right now, and there are no open positions loaded yet.", 'local'

    return (
        "Remote AI is unavailable right now. I can still summarize the loaded hiring data: "
        f"{len(candidates)} candidate(s) and {len(jobs)} open position(s)."
    ), 'local'


def _chat(system_content, messages):
    """Try OpenRouter first, fallback to Gemini, then a local data summary."""
    if openrouter_client:
        try:
            return _chat_openrouter(system_content, messages)
        except Exception as e:
            logger.warning(f"OpenRouter chat failed: {e}")

    if gemini_client or gemini_model:
        try:
            return _chat_gemini(system_content, messages)
        except Exception as e:
            logger.warning(f"Gemini chat failed: {e}")

    return _chat_local(system_content, messages)


def _build_context(current_user):
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    jobs = JobPosting.query.filter_by(user_id=current_user.id).all()
    analyses = ResumeAnalysis.query.join(Resume).filter(Resume.user_id == current_user.id).all()

    ctx = "You are an AI HR assistant. Here is the current hiring data:\n\n"
    ctx += f"OPEN POSITIONS ({len(jobs)}):\n"
    for j in jobs:
        ctx += f"- {j.title}: {(j.description or '')[:150]}\n"

    ctx += f"\nCANDIDATES ({len(resumes)}):\n"
    for r in resumes:
        analysis = next((a for a in analyses if a.resume_id == r.id), None)
        score = f"{analysis.match_score:.0f}%" if analysis and analysis.match_score else "Not analyzed"
        category = analysis.category if analysis else "Pending"
        ctx += f"- {r.candidate_name or 'Unknown'} | Score: {score} | {category}\n"

    return ctx


class HRChat(Resource):
    @token_required
    def post(self, current_user):
        try:
            data = request.get_json(silent=True) or {}
            messages = data.get('messages', [])
            if not messages:
                return {'message': 'No messages provided'}, 400

            context = _build_context(current_user)
            system_content = (
                f"{context}\n\n"
                "Answer HR questions concisely. Use the data above to provide specific insights."
            )

            reply, model_used = _chat(system_content, messages)
            return {'reply': reply, 'role': 'assistant', 'model': model_used}, 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"HR chat error: {error_msg}\n{traceback.format_exc()}")
            if 'No AI model' in error_msg:
                return {'message': 'No AI API configured. Add OPENROUTER_API_KEY or GEMINI_API_KEY to .env'}, 500
            if '429' in error_msg or 'quota' in error_msg.lower():
                return {'message': 'API quota exceeded. Try again later.'}, 429
            return {'message': f'Chat error: {error_msg}'}, 500


class CandidateChat(Resource):
    @token_required
    def post(self, current_user, resume_id):
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        if not resume:
            return {'message': 'Resume not found'}, 404

        analysis = ResumeAnalysis.query.filter_by(resume_id=resume_id).first()
        data = request.get_json(silent=True) or {}
        messages = data.get('messages', [])

        resume_ctx = f"Candidate: {resume.candidate_name or 'Unknown'}\n"
        resume_ctx += f"Resume Text: {(resume.raw_text or '')[:2000]}\n"
        if analysis:
            resume_ctx += f"Match Score: {analysis.match_score}\n"
            resume_ctx += f"Category: {analysis.category}\n"
            resume_ctx += f"Summary: {analysis.summary}\n"

        system_content = (
            f"You are an AI HR assistant discussing a specific candidate.\n\n"
            f"{resume_ctx}\n\n"
            "Answer questions about this candidate concisely and professionally."
        )

        try:
            reply, model_used = _chat(system_content, messages)
            return {'reply': reply, 'role': 'assistant', 'model': model_used}, 200
        except Exception as e:
            logger.error(f"Candidate chat error: {str(e)}\n{traceback.format_exc()}")
            return {'message': f'Chat error: {str(e)}'}, 500


api = Api(bp)
api.add_resource(HRChat, '/hr')
api.add_resource(CandidateChat, '/candidate/<int:resume_id>')
