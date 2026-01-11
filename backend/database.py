"""
Database initialization and connection management
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Import models to register them with SQLAlchemy
        import models
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")

def get_db_session():
    """Get database session for non-Flask contexts"""
    engine = create_engine(os.getenv('DATABASE_URL'))
    session = scoped_session(sessionmaker(bind=engine))
    return session
