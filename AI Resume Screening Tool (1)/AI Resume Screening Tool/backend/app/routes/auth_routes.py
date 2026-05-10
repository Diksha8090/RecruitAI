from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource
from functools import wraps
import jwt
from app import db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'message': 'Invalid token format'}, 401
        
        if not token:
            return {'message': 'Token is missing'}, 401
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                return {'message': 'User not found'}, 401
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
        
        if args:
            # Preserve method binding when decorating class methods
            return f(args[0], current_user, *args[1:], **kwargs)
        return f(current_user, *args, **kwargs)
    return decorated

class Register(Resource):
    def post(self):
        """Register new user"""
        data = request.get_json(silent=True) or {}
        
        if not data or not data.get('email') or not data.get('password') or not data.get('username'):
            return {'message': 'Missing required fields'}, 400
        
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 409
        
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 409
        
        try:
            user = User(
                email=data['email'],
                username=data['username'],
                organization=data.get('organization', '')
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'message': 'User registered successfully',
                'user': user.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

class Login(Resource):
    def post(self):
        """Login user"""
        data = request.get_json(silent=True) or {}
        
        if not data or not data.get('email') or not data.get('password'):
            return {'message': 'Missing email or password'}, 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid credentials'}, 401
        
        token = jwt.encode(
            {'user_id': user.id},
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return {
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }, 200

class Profile(Resource):
    @token_required
    def get(self, current_user):
        """Get current user profile"""
        return {'user': current_user.to_dict()}, 200
    
    @token_required
    def put(self, current_user):
        """Update user profile"""
        data = request.get_json(silent=True) or {}
        
        if 'organization' in data:
            current_user.organization = data['organization']
        if 'username' in data:
            current_user.username = data['username']
        
        db.session.commit()
        
        return {
            'message': 'Profile updated',
            'user': current_user.to_dict()
        }, 200

api = Api(bp)
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Profile, '/profile')
