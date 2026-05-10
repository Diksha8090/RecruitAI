from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_FILE_SIZE'] = int(os.getenv('MAX_FILE_SIZE', 5242880))
    app.config['MAX_CONTENT_LENGTH'] = app.config['MAX_FILE_SIZE']
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import auth_routes, resume_routes, analysis_routes, job_posting_routes
    from app.routes import chat_routes

    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(resume_routes.bp)
    app.register_blueprint(analysis_routes.bp)
    app.register_blueprint(job_posting_routes.bp)
    app.register_blueprint(chat_routes.bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
